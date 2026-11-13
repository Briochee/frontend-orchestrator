from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from frontend_design_director.cli import (
    _bundled_codex_resources,
    _codex_install_locations,
    _codex_manifest_path,
    _install_codex,
    _installation_doctor,
    _python_installation_report,
    _uninstall_codex,
    main,
)


class CodexInstallationSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-director-install-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def resources_with(self, resource_id: str, content: bytes) -> list[dict[str, object]]:
        resources = _bundled_codex_resources()
        for resource in resources:
            if resource["id"] == resource_id:
                resource["content"] = content
                return resources
        self.fail(f"Unknown bundled resource: {resource_id}")

    def component(self, result: dict[str, object], resource_id: str) -> dict[str, object]:
        components = result["components"]
        assert isinstance(components, list)
        return next(item for item in components if item["id"] == resource_id)

    def test_fresh_install_creates_versioned_manifest_and_hashes_every_resource(self) -> None:
        result = _install_codex(self.project, "project")
        manifest_path = Path(result["install_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "synchronized")
        self.assertTrue(result["verification"]["passed"])
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(len(manifest["resources"]), 6)
        self.assertTrue(all(item["managed"] for item in manifest["resources"].values()))
        for item in result["components"]:
            destination = Path(item["destination"])
            self.assertEqual(item["status"], "installed")
            self.assertEqual(hashlib.sha256(destination.read_bytes()).hexdigest(), item["bundled_sha256"])

    def test_repeat_update_is_idempotent_and_does_not_rewrite_current_files(self) -> None:
        first = _install_codex(self.project, "project")
        before = {
            Path(item["destination"]): Path(item["destination"]).stat().st_mtime_ns
            for item in first["components"]
        }
        second = _install_codex(self.project, "project", upgrade=True)

        self.assertEqual(second["status"], "synchronized")
        self.assertTrue(all(item["status"] == "current" for item in second["components"]))
        self.assertEqual(
            before,
            {path: path.stat().st_mtime_ns for path in before},
        )

    def test_upgrade_replaces_managed_unmodified_file_and_leaves_current_files_untouched(self) -> None:
        original = _install_codex(self.project, "project")
        target = next(item for item in original["components"] if item["id"].startswith("agent:"))
        target_path = Path(target["destination"])
        unchanged = {
            Path(item["destination"]): Path(item["destination"]).stat().st_mtime_ns
            for item in original["components"]
            if item["destination"] != target["destination"]
        }
        new_content = b"# Updated bundled agent\n"

        with patch(
            "frontend_design_director.cli._bundled_codex_resources",
            return_value=self.resources_with(str(target["id"]), new_content),
        ):
            result = _install_codex(self.project, "project", upgrade=True)

        self.assertEqual(self.component(result, str(target["id"]))["status"], "updated")
        self.assertEqual(target_path.read_bytes(), new_content)
        self.assertEqual(unchanged, {path: path.stat().st_mtime_ns for path in unchanged})
        manifest = json.loads(Path(result["install_manifest"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["resources"][target["id"]]["sha256"], hashlib.sha256(new_content).hexdigest())

    def test_normal_upgrade_preserves_local_modification_and_force_backs_it_up(self) -> None:
        installed = _install_codex(self.project, "project")
        target = next(item for item in installed["components"] if item["id"].startswith("agent:"))
        target_path = Path(target["destination"])
        local_content = b"# Local customizations\n"
        bundled_content = b"# New upstream agent\n"
        target_path.write_bytes(local_content)
        resources = self.resources_with(str(target["id"]), bundled_content)

        with patch("frontend_design_director.cli._bundled_codex_resources", return_value=resources):
            safe_result = _install_codex(self.project, "project", upgrade=True)
            self.assertEqual(self.component(safe_result, str(target["id"]))["status"], "modified_locally")
            self.assertEqual(target_path.read_bytes(), local_content)

            forced_result = _install_codex(self.project, "project", upgrade=True, force=True)

        component = self.component(forced_result, str(target["id"]))
        backup = Path(component["backup"])
        self.assertEqual(component["status"], "backed_up_and_updated")
        self.assertEqual(backup.read_bytes(), local_content)
        self.assertEqual(target_path.read_bytes(), bundled_content)
        self.assertEqual(backup.stat().st_mode & 0o777, target_path.stat().st_mode & 0o777)

    def test_untracked_legacy_file_requires_force_and_is_backed_up(self) -> None:
        resources = _bundled_codex_resources()
        target = next(item for item in resources if item["id"].startswith("agent:"))
        agents = self.project / ".codex" / "agents"
        agents.mkdir(parents=True)
        destination = agents / str(target["name"])
        unrelated = agents / "user-created-agent.toml"
        legacy_content = b"# Older manually installed agent\n"
        destination.write_bytes(legacy_content)
        unrelated.write_bytes(b"# unrelated user agent\n")

        normal = _install_codex(self.project, "project", upgrade=True)
        self.assertEqual(self.component(normal, str(target["id"]))["status"], "untracked_legacy")
        self.assertEqual(destination.read_bytes(), legacy_content)

        with patch("frontend_design_director.cli._bundled_codex_resources", return_value=resources):
            forced = _install_codex(self.project, "project", upgrade=True, force=True)
        component = self.component(forced, str(target["id"]))
        self.assertEqual(component["status"], "backed_up_and_updated")
        self.assertEqual(Path(component["backup"]).read_bytes(), legacy_content)
        self.assertEqual(destination.read_bytes(), target["content"])
        self.assertEqual(unrelated.read_bytes(), b"# unrelated user agent\n")

    def test_force_replaces_untracked_install_without_any_manifest(self) -> None:
        resources = _bundled_codex_resources()
        for resource in resources:
            destination = (
                self.project / ".agents" / "skills" / "frontend-design-director" / "SKILL.md"
                if resource["id"] == "skill"
                else self.project / ".codex" / "agents" / str(resource["name"])
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"old file with no ownership manifest\n")

        result = _install_codex(self.project, "project", upgrade=True, force=True)

        self.assertEqual(result["status"], "synchronized")
        self.assertEqual(len(result["backups"]), 6)
        self.assertTrue(all(item["status"] == "backed_up_and_updated" for item in result["components"]))
        manifest = json.loads(Path(result["install_manifest"]).read_text(encoding="utf-8"))
        self.assertTrue(all(item["managed"] for item in manifest["resources"].values()))

    def test_legacy_v1_manifest_migrates_and_remains_uninstallable(self) -> None:
        installed = _install_codex(self.project, "project")
        manifest_path = Path(installed["install_manifest"])
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        legacy = {
            "schema_version": 1,
            "scope": current["scope"],
            "root": current["root"],
            "agents_directory": current["agents_directory"],
            "skill_sha256": current["resources"]["skill"]["sha256"],
            "agent_sha256": {
                key.removeprefix("agent:"): value["sha256"]
                for key, value in current["resources"].items()
                if key.startswith("agent:")
            },
        }
        manifest_path.write_text(json.dumps(legacy), encoding="utf-8")
        skill_content = b"# Revised skill\n"

        with patch(
            "frontend_design_director.cli._bundled_codex_resources",
            return_value=self.resources_with("skill", skill_content),
        ):
            result = _install_codex(self.project, "project", upgrade=True)

        migrated = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["resources"]["skill"]["sha256"], hashlib.sha256(skill_content).hexdigest())
        self.assertEqual(Path(self.component(result, "skill")["destination"]).read_bytes(), skill_content)
        uninstall = _uninstall_codex(self.project, "project")
        self.assertEqual(len(uninstall["removed"]), 6)

    def test_end_to_end_legacy_install_updates_then_forces_with_recovery_backup(self) -> None:
        home = self.root / "home"
        codex_home = self.root / "codex-home"
        home.mkdir()
        codex_home.mkdir()
        bundled = _bundled_codex_resources()
        old_resources = {item["id"]: f"legacy {item['name']}\n".encode() for item in bundled}
        with patch("pathlib.Path.home", return_value=home), patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
            root, _, _, agents_directory = _codex_install_locations(self.project, "user", create=False)
            skill_path = home / ".agents" / "skills" / "frontend-design-director" / "SKILL.md"
            agents_directory.mkdir(parents=True)
            (skill_path.parent).mkdir(parents=True)
            skill_path.write_bytes(old_resources["skill"])
            for item in bundled:
                if item["type"] == "agent":
                    (agents_directory / str(item["name"])).write_bytes(old_resources[str(item["id"])])
            legacy_manifest = {
                "schema_version": 1,
                "scope": "user",
                "root": str(root),
                "agents_directory": str(agents_directory),
                "skill_sha256": hashlib.sha256(old_resources["skill"]).hexdigest(),
                "agent_sha256": {
                    str(item["name"]): hashlib.sha256(old_resources[str(item["id"])]).hexdigest()
                    for item in bundled
                    if item["type"] == "agent"
                },
            }
            manifest_path = _codex_manifest_path(root, agents_directory)
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(json.dumps(legacy_manifest), encoding="utf-8")

            update = _install_codex(self.project, "user", upgrade=True)
            self.assertTrue(update["verification"]["passed"])
            self.assertEqual(len(update["backups"]), 6)
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8"))["schema_version"], 2)

            skill_path.write_bytes(b"local skill customization\n")
            ordinary = _install_codex(self.project, "user", upgrade=True)
            self.assertEqual(self.component(ordinary, "skill")["status"], "modified_locally")
            self.assertEqual(skill_path.read_bytes(), b"local skill customization\n")

            forced = _install_codex(self.project, "user", upgrade=True, force=True)
            skill_component = self.component(forced, "skill")
            self.assertEqual(skill_component["status"], "backed_up_and_updated")
            self.assertEqual(Path(skill_component["backup"]).read_bytes(), b"local skill customization\n")
            final = _installation_doctor(self.project, "user")
            self.assertEqual(final["codex"]["status"], "current")
            self.assertEqual(final["codex"]["summary"]["current"], 6)

    def test_backup_failure_aborts_before_replacing_any_file(self) -> None:
        installed = _install_codex(self.project, "project")
        target = next(item for item in installed["components"] if item["id"].startswith("agent:"))
        destination = Path(target["destination"])
        local_content = b"private local edit\n"
        destination.write_bytes(local_content)
        resources = self.resources_with(str(target["id"]), b"new bundled content\n")

        with patch("frontend_design_director.cli._bundled_codex_resources", return_value=resources):
            with patch("frontend_design_director.cli._create_codex_backup", side_effect=OSError("backup unavailable")):
                with self.assertRaises(OSError):
                    _install_codex(self.project, "project", upgrade=True, force=True)

        self.assertEqual(destination.read_bytes(), local_content)
        self.assertFalse(any(path.name.endswith(".tmp") for path in self.root.rglob("*")))

    def test_failed_manifest_write_rolls_back_replaced_files(self) -> None:
        installed = _install_codex(self.project, "project")
        target = installed["components"][0]
        destination = Path(target["destination"])
        original_content = destination.read_bytes()
        resources = self.resources_with(str(target["id"]), b"new content\n")

        with patch("frontend_design_director.cli._bundled_codex_resources", return_value=resources):
            with patch("frontend_design_director.cli._write_codex_manifest", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    _install_codex(self.project, "project", upgrade=True)

        self.assertEqual(destination.read_bytes(), original_content)
        self.assertFalse(any(path.name.endswith(".tmp") for path in self.root.rglob("*")))

    def test_partial_replace_failure_restores_earlier_files(self) -> None:
        installed = _install_codex(self.project, "project")
        old_contents = {item["id"]: Path(item["destination"]).read_bytes() for item in installed["components"]}
        resources = _bundled_codex_resources()
        for resource in resources:
            resource["content"] = b"updated " + str(resource["id"]).encode() + b"\n"

        real_replace = os.replace
        replacements = 0

        def fail_second_replacement(source, destination):
            nonlocal replacements
            replacements += 1
            if replacements == 2:
                raise OSError("simulated replacement failure")
            return real_replace(source, destination)

        with patch("frontend_design_director.cli._bundled_codex_resources", return_value=resources):
            with patch("frontend_design_director.cli.os.replace", side_effect=fail_second_replacement):
                with self.assertRaises(OSError):
                    _install_codex(self.project, "project", upgrade=True)

        for item in installed["components"]:
            self.assertEqual(Path(item["destination"]).read_bytes(), old_contents[item["id"]])

    def test_symlink_resource_is_rejected_without_touching_link_target(self) -> None:
        outside = self.root / "outside.toml"
        outside.write_bytes(b"user data\n")
        target = self.project / ".codex" / "agents" / "frontend-code-auditor.toml"
        target.parent.mkdir(parents=True)
        target.symlink_to(outside)

        result = _install_codex(self.project, "project", upgrade=True, force=True)
        self.assertEqual(self.component(result, "agent:frontend-code-auditor.toml")["status"], "invalid")
        self.assertTrue(target.is_symlink())
        self.assertEqual(outside.read_bytes(), b"user data\n")

    def test_symlink_manifest_is_rejected_without_touching_its_target(self) -> None:
        outside = self.root / "outside.json"
        outside.write_text("user data", encoding="utf-8")
        root, _, _, agents_directory = _codex_install_locations(self.project, "project", create=False)
        manifest = _codex_manifest_path(root, agents_directory)
        manifest.parent.mkdir(parents=True)
        manifest.symlink_to(outside)

        with self.assertRaises(ValueError):
            _install_codex(self.project, "project", upgrade=True, force=True)
        self.assertEqual(outside.read_text(encoding="utf-8"), "user data")

    def test_doctor_reports_unsafe_parent_directory_without_following_it(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / ".agents").symlink_to(outside, target_is_directory=True)

        result = _installation_doctor(self.project, "project")

        self.assertEqual(result["codex"]["status"], "conflicts")
        self.assertIn("symbolic link", result["codex"]["path_error"])
        self.assertEqual(list(outside.iterdir()), [])

    def test_doctor_reports_component_hashes_and_custom_codex_home(self) -> None:
        home = self.root / "home"
        home.mkdir()
        codex_home = self.root / "custom-codex"
        with patch("pathlib.Path.home", return_value=home), patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
            _install_codex(self.project, "user")
            result = _installation_doctor(self.project, "user")

        self.assertEqual(result["codex"]["agents_directory"], str((codex_home / "agents").resolve(strict=False)))
        self.assertEqual(result["codex"]["status"], "current")
        self.assertEqual(result["codex"]["summary"]["current"], 6)
        self.assertTrue(result["codex"]["manifest"]["present"])

    def test_doctor_reports_current_legacy_files_without_claiming_ownership(self) -> None:
        installed = _install_codex(self.project, "project")
        Path(installed["install_manifest"]).unlink()
        result = _installation_doctor(self.project, "project")

        self.assertEqual(result["codex"]["status"], "current_unmanaged")
        self.assertEqual(result["codex"]["summary"]["current"], 6)
        self.assertFalse(result["codex"]["manifest"]["present"])
        self.assertTrue(any("Create an ownership manifest" in item for item in result["recommendations"]))

    def test_python_install_mode_is_unknown_without_editable_metadata(self) -> None:
        class Distribution:
            version = "0.1.0"

            def locate_file(self, _path: str) -> Path:
                return Path("/tmp/site-packages")

            def read_text(self, _name: str) -> None:
                return None

        with patch("frontend_design_director.cli.metadata.distribution", return_value=Distribution()):
            result = _python_installation_report(None)

        self.assertIsNone(result["editable"])
        self.assertEqual(result["installation_mode"], "unknown")

    def test_obsolete_managed_agent_is_reported_and_preserved(self) -> None:
        installed = _install_codex(self.project, "project")
        manifest_path = Path(installed["install_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        agents_directory = Path(manifest["agents_directory"])
        obsolete_path = agents_directory / "frontend-retired-auditor.toml"
        obsolete_content = b"# Retired but still managed\n"
        obsolete_path.write_bytes(obsolete_content)
        manifest["resources"]["agent:frontend-retired-auditor.toml"] = {
            "type": "agent",
            "name": obsolete_path.name,
            "source": "data/agents/frontend-retired-auditor.toml",
            "destination": str(obsolete_path),
            "sha256": hashlib.sha256(obsolete_content).hexdigest(),
            "managed": True,
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        updated = _install_codex(self.project, "project", upgrade=True)
        doctor = _installation_doctor(self.project, "project")

        self.assertEqual(updated["status"], "conflicts")
        self.assertEqual(updated["obsolete_resources"][0]["status"], "obsolete_managed")
        self.assertEqual(doctor["codex"]["summary"]["obsolete"], 1)
        self.assertTrue(obsolete_path.is_file())

    def test_project_cli_update_is_scope_local_and_doctor_help_is_available(self) -> None:
        user_home = self.root / "home"
        user_home.mkdir()
        project_agent = self.project / ".codex" / "agents" / "frontend-visual-auditor.toml"
        user_agent = user_home / ".codex" / "agents" / "frontend-visual-auditor.toml"
        with patch("pathlib.Path.home", return_value=user_home):
            _install_codex(self.project, "user")
            user_before = user_agent.read_bytes()
            project_agent.parent.mkdir(parents=True)
            project_agent.write_bytes(b"# local old project agent\n")
            output = StringIO()
            with redirect_stdout(output):
                status = main([
                    "--no-update-check",
                    "update-codex",
                    "--scope",
                    "project",
                    "--project",
                    str(self.project),
                    "--force",
                    "--json",
                ])

        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["scope"], "project")
        self.assertEqual(user_agent.read_bytes(), user_before)
        for command in ("install-codex", "update-codex", "doctor"):
            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit) as result:
                    main([command, "--help"])
            self.assertEqual(result.exception.code, 0)


if __name__ == "__main__":
    unittest.main()

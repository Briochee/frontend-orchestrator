"""Phase-aware command execution safeguards."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence


IMPLEMENTATION_NO_RTK_INSTRUCTION = (
    "During the Frontend Design Director implementation phase, RTK is disabled. Do not invoke `rtk`, "
    "prefix terminal commands with `rtk`, or delegate work that does so. Run native executables directly. "
    "This applies to implementation, Git inspection, patch review, tests, retries, and verification. "
    "Preserve complete native stdout, stderr, structured JSON, and exit status without command wrappers or output transformations. "
    "This policy does not authorize extra commands or change existing permissions, scope, or approval requirements."
)


@dataclass(frozen=True)
class ExecutionPolicy:
    """Execution constraints propagated through one workflow phase."""

    phase: str
    allow_rtk: bool = True


IMPLEMENTATION_EXECUTION_POLICY = ExecutionPolicy(phase="implement", allow_rtk=False)
IMPLEMENTATION_CODEX_RULE = '''prefix_rule(
    pattern = ["rtk"],
    decision = "forbidden",
    justification = "RTK is disabled during Frontend Design Director implementation; run the native command directly.",
)
'''


class RTKExecutionBlocked(RuntimeError):
    """Raised when a Frontend Design Director child process tries to launch RTK."""


def execution_policy_for_phase(phase: object, *, paused_from: object | None = None) -> ExecutionPolicy:
    """Return the implementation policy for implementation and its verification stages."""
    value = getattr(phase, "value", phase)
    name = str(value).strip().casefold()
    if name == "paused" and paused_from is not None:
        name = str(getattr(paused_from, "value", paused_from)).strip().casefold()
    implementation_phases = {
        "implement", "implementation", "implementing", "apply", "applying", "verify", "verification", "verifying",
    }
    if name in implementation_phases:
        return IMPLEMENTATION_EXECUTION_POLICY
    return ExecutionPolicy(phase=name or "unspecified", allow_rtk=True)


def instruction_with_execution_policy(instruction: str, policy: ExecutionPolicy | None) -> str:
    """Attach the implementation command restriction to each provider task context."""
    if policy is None or policy.allow_rtk:
        return instruction
    if IMPLEMENTATION_NO_RTK_INSTRUCTION in instruction:
        return instruction
    return f"{instruction.rstrip()}\n\nExecution policy:\n{IMPLEMENTATION_NO_RTK_INSTRUCTION}"


@contextmanager
def codex_execution_rules(working_directory: Path, policy: ExecutionPolicy | None) -> Iterator[Path | None]:
    """Add a temporary Codex rule for RTK-free phases inside the disposable workspace."""
    if policy is None or policy.allow_rtk:
        yield None
        return

    root = working_directory.resolve(strict=True)
    codex_directory = root / ".codex"
    rules_directory = codex_directory / "rules"
    if codex_directory.is_symlink() or rules_directory.is_symlink():
        raise ValueError("Cannot place the implementation command policy through a symbolic link.")
    codex_existed = codex_directory.exists()
    rules_existed = rules_directory.exists()
    rules_directory.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix="frontend-director-no-rtk-", suffix=".rules", dir=rules_directory)
    rule_path = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(IMPLEMENTATION_CODEX_RULE)
        rule_path.chmod(0o400)
        yield rule_path
    finally:
        rule_path.chmod(0o600)
        rule_path.unlink(missing_ok=True)
        if not rules_existed:
            try:
                rules_directory.rmdir()
            except OSError:
                pass
        if not codex_existed:
            try:
                codex_directory.rmdir()
            except OSError:
                pass


def run_process(
    arguments: Sequence[str | os.PathLike[str]],
    *,
    policy: ExecutionPolicy | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Run an argument-array command unchanged, with an implementation-scoped RTK guard."""
    command = [os.fspath(item) for item in arguments]
    if not command or not command[0]:
        raise ValueError("A process command must include an executable.")
    if policy is None or policy.allow_rtk:
        return subprocess.run(command, **kwargs)

    if _command_invokes_rtk(command):
        raise RTKExecutionBlocked(
            f"RTK is disabled during the {policy.phase} phase; invoke the native command directly."
        )

    # A PATH-first deny shim also blocks bare `rtk` calls made by shell tools inside a
    # provider process. It leaves every other executable and the rest of PATH intact.
    original_environment = kwargs.get("env")
    environment = dict(os.environ if original_environment is None else original_environment)
    with tempfile.TemporaryDirectory(prefix="frontend-director-no-rtk-") as temporary:
        shim_directory = Path(temporary)
        path = shim_directory / ("rtk.cmd" if os.name == "nt" else "rtk")
        if os.name == "nt":
            path.write_text(
                "@echo off\r\necho RTK is disabled during Frontend Design Director implementation. 1>&2\r\nexit /b 126\r\n",
                encoding="utf-8",
            )
        else:
            path.write_text(
                "#!/bin/sh\nprintf '%s\\n' 'RTK is disabled during Frontend Design Director implementation.' >&2\nexit 126\n",
                encoding="utf-8",
            )
            path.chmod(0o700)
        prior_path = environment.get("PATH", "")
        environment["PATH"] = os.pathsep.join(part for part in (str(shim_directory), prior_path) if part)
        kwargs["env"] = environment
        return subprocess.run(command, **kwargs)


def _command_invokes_rtk(command: Sequence[str]) -> bool:
    executable = command[0]
    if _is_rtk_executable(executable):
        return True
    if Path(executable).name.casefold() in {"python", "python3", "python.exe", "python3.exe"}:
        return any(command[index] == "-m" and index + 1 < len(command) and command[index + 1].casefold() == "rtk" for index in range(1, len(command)))
    if Path(executable).name.casefold() in {"env", "env.exe"}:
        return _env_command_invokes_rtk(command)
    return False


def _env_command_invokes_rtk(command: Sequence[str]) -> bool:
    index = 1
    while index < len(command):
        token = command[index]
        if token == "--":
            index += 1
            break
        if token in {"-i", "--ignore-environment", "-0", "--null"}:
            index += 1
            continue
        if token in {"-u", "--unset", "-C", "--chdir"}:
            index += 2
            continue
        if token.startswith(("--unset=", "--chdir=")):
            index += 1
            continue
        if token in {"-S", "--split-string"}:
            if index + 1 >= len(command):
                return False
            try:
                split = shlex.split(command[index + 1])
            except ValueError:
                return False
            return bool(split and _is_rtk_executable(split[0]))
        if token.startswith("-"):
            # Unknown env options are left to PATH protection rather than guessed at.
            return False
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token):
            index += 1
            continue
        break
    return index < len(command) and _is_rtk_executable(command[index])


def _is_rtk_executable(value: str) -> bool:
    return Path(value).name.casefold() in {"rtk", "rtk.exe", "rtk.cmd", "rtk.bat"}

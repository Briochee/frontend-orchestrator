from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SampleFrontendTests(unittest.TestCase):
    def test_dashboard_has_primary_landmarks_and_summary_content(self) -> None:
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<main id="main">', page)
        self.assertIn('aria-label="Main navigation"', page)
        self.assertIn("Recent projects", page)
        self.assertIn("Recent activity", page)

    def test_styles_include_tablet_mobile_and_reduced_motion_rules(self) -> None:
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 900px)", styles)
        self.assertIn("@media (max-width: 620px)", styles)
        self.assertIn("prefers-reduced-motion: reduce", styles)


if __name__ == "__main__":
    unittest.main()

"""The documentation site builds, has a page for every example, and every link
on it inside the site goes somewhere (scripts/pages.py)."""
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pages as docsite  # noqa: E402


class Site(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / "site"
        cls.pages = docsite.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_example_has_a_page_and_a_title(self):
        for path in sorted((ROOT / "examples").glob("*.tex")):
            self.assertIn(f"examples/{path.stem}.html", self.pages)
            self.assertTrue(path.read_text().startswith("%% "), path.name)

    def test_every_link_inside_the_site_resolves(self):
        for name in self.pages:
            page = self.out / name
            for target in re.findall(r'(?:href|src)="([^"#]+)', page.read_text()):
                if re.match(r"[a-z]+:", target):
                    continue
                self.assertTrue((page.parent / target).resolve().exists(),
                                f"{name} links to {target}")

    def test_the_reference_is_docs_api(self):
        text = (self.out / "api.html").read_text()
        for command in re.findall(r"^### `(\\tn[a-z]+)", (ROOT / "docs/api.md").read_text(), re.M):
            self.assertIn(command, text)


if __name__ == "__main__":
    unittest.main()

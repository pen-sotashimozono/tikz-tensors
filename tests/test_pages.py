"""The documentation site builds, has a page for every example, and every link
on it inside the site goes somewhere (scripts/pages.py); and publishing it to
gh-pages keeps the versions side by side (scripts/publish.py)."""
import json
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pages as docsite  # noqa: E402
import publish  # noqa: E402


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

    def test_every_example_is_in_a_section_in_order(self):
        exs = docsite.examples()
        self.assertEqual([e.number for e in exs], sorted(e.number for e in exs))
        for e in exs:
            self.assertIn(docsite.section(e), [t for _, t in docsite.SECTIONS])

    def test_every_link_inside_the_site_resolves(self):
        for name in self.pages:
            page = self.out / name
            for target in re.findall(r'(?:href|src)="([^"#]+)', page.read_text()):
                if re.match(r"[a-z]+:", target):
                    continue
                self.assertTrue((page.parent / target).resolve().exists(),
                                f"{name} links to {target}")

    def test_every_anchor_a_link_names_exists(self):
        ids = {}
        for name in self.pages:
            for target in re.findall(r'href="([^"#:]*)#([^"]+)"', (self.out / name).read_text()):
                page = ((self.out / name).parent / target[0]).resolve() if target[0] \
                    else (self.out / name).resolve()
                if page not in ids:
                    ids[page] = set(re.findall(r'id="([^"]+)"', page.read_text()))
                self.assertIn(target[1], ids[page], f"{name} links to {target[0]}#{target[1]}")

    def test_code_links_every_command_to_the_reference(self):
        text = (self.out / "examples/08-canonical.html").read_text()
        for command in ("tnstack", "tnlayer", "tnconnect", "tnopen"):
            self.assertIn(f'href="../commands.html#{command}"', text)
        styles = (self.out / "styles.html").read_text()
        self.assertIn('href="commands.html#tnlayer"', styles)
        self.assertIn('href="styles.html#tn-box"', styles)

    def test_the_reference_is_docs_reference(self):
        text = (self.out / "commands.html").read_text()
        doc = (ROOT / "docs/reference/commands.md").read_text()
        for command in re.findall(r"^### `(\\tn[a-z]+)", doc, re.M):
            self.assertIn(f'id="{command[1:]}"', text)

    def test_every_style_has_a_definition_and_a_picture(self):
        text = (self.out / "styles.html").read_text()
        plain = re.sub(r"<[^>]+>", "", text)
        for name in re.findall(r"`(tn [a-z ]+?)`", (ROOT / "docs/reference/styles.md").read_text()):
            self.assertIn(f"{name}/.", plain, f"{name} has no definition on the page")
        for path in (ROOT / "docs/reference/styles").glob("*.tex"):
            self.assertIn(f"figures/{path.stem}.svg", text)

    def test_the_overview_builds_a_figure_step_by_step(self):
        text = (self.out / "api.html").read_text()
        steps = sorted((ROOT / "docs/reference/steps").glob("step-*.tex"))
        self.assertGreater(len(steps), 1)
        for path in steps:
            self.assertIn(f'id="{path.stem}"', text)
            self.assertIn(f"figures/{path.stem}.svg", text)
        # every step adds something, and only what it adds is marked
        cards = re.findall(r'<article class="doc step".*?</article>', text, re.S)
        self.assertEqual(len(cards), len(steps))
        for card in cards:
            self.assertIn('class="ln add"', card)
        self.assertEqual(cards[-1].count('class="ln add"'), 7)


class Publish(unittest.TestCase):
    def test_versions_side_by_side_and_previews_come_and_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            site = tmp / "site"
            docsite.build(site)
            ghp = tmp / "gh-pages"
            publish.main([str(ghp), str(site), "v0.9.0", "stable"])
            publish.main([str(ghp), str(site), "v0.10.0", "stable"])
            publish.main([str(ghp), str(site), "previews/PR7"])
            self.assertEqual(json.loads((ghp / "versions.json").read_text()),
                             ["stable", "v0.10.0", "v0.9.0"])
            self.assertTrue((ghp / "previews/PR7/index.html").is_file())
            self.assertIn("url=stable/", (ghp / "index.html").read_text())
            publish.main([str(ghp), "--remove", "previews/PR7"])
            self.assertFalse((ghp / "previews/PR7").exists())
            self.assertTrue((ghp / "v0.9.0/index.html").is_file())

    def test_only_a_version_stable_or_a_preview_is_a_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            docsite.build(tmp / "site")
            with self.assertRaises(SystemExit):
                publish.main([str(tmp / "ghp"), str(tmp / "site"), "../elsewhere"])


if __name__ == "__main__":
    unittest.main()

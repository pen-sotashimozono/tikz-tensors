"""scripts/version.py against throwaway repositories.

    python3 -m unittest discover -s tests

Each test copies the package into a fresh git repository, commits it as the
base, makes one kind of change, and asks `check` whether the version moved
as it must.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class VersionCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        for part in ("tex", "theme", "scripts"):
            shutil.copytree(ROOT / part, self.tmp / part,
                            ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(ROOT / "CHANGELOG.md", self.tmp / "CHANGELOG.md")
        (self.tmp / "tests/reference").mkdir(parents=True)
        (self.tmp / "tests/reference/a.svg").write_bytes(b"one")
        self.git("init", "-q", "-b", "main")
        self.commit("base")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.tmp), *args], check=True, capture_output=True)

    def commit(self, message):
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)

    def run_version(self, *args):
        return subprocess.run([sys.executable, str(self.tmp / "scripts/version.py"), *args],
                              capture_output=True, text=True)

    def check(self):
        out = self.run_version("check", "--base", "HEAD")
        return out.returncode, out.stdout

    def edit_sty(self, old, new):
        """Replace <old> in the one file of the package (tex/) that has it."""
        files = [p for p in sorted((self.tmp / "tex").rglob("*.*")) if old in p.read_text()]
        self.assertEqual(len(files), 1, old)
        files[0].write_text(files[0].read_text().replace(old, new, 1))

    def bump(self, level, summary="Why."):
        out = self.run_version("bump", level, summary)
        self.assertEqual(out.returncode, 0, out.stderr)

    def version(self):
        return self.run_version().stdout.strip()

    NEW_STYLE = ("  tn small/.style", "  tn hexagon/.style = {tn node, regular polygon},\n  tn small/.style")
    NO_SMALL = ("  tn small/.style          = {minimum size=6mm, font=\\scriptsize},\n", "")
    # A change under tex/ that adds and removes no public name. It anchors on
    # \NeedsTeXFormat and adds a comment, rather than rewriting a value inside a
    # style: the styles are the thing under development, and a fixture that
    # quotes one of their numbers breaks when that number moves, which says
    # nothing about the rule being tested.
    INTERNAL = ("\\NeedsTeXFormat{LaTeX2e}",
                "% an internal change: nothing public added or removed\n\\NeedsTeXFormat{LaTeX2e}")

    # -- nothing to release -------------------------------------------------

    def test_no_package_change_keeps_the_version(self):
        (self.tmp / "README.md").write_text("docs\n")
        self.assertEqual(self.check()[0], 0)

    def test_a_bump_without_a_package_change_is_refused(self):
        self.bump("patch")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("Put it back", out)

    def test_a_new_reference_image_needs_no_bump(self):
        (self.tmp / "tests/reference/b.svg").write_bytes(b"new case")
        self.assertEqual(self.check()[0], 0)

    # -- how large the step must be -----------------------------------------

    def test_an_internal_change_needs_a_patch(self):
        self.edit_sty(*self.INTERNAL)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("patch", out)
        self.bump("patch")
        self.assertEqual(self.check()[0], 0)

    def test_a_new_style_needs_a_minor(self):
        self.edit_sty(*self.NEW_STYLE)
        self.bump("patch")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("adds style 'tn hexagon'", out)
        self.assertIn("needs a minor step", out)

    def test_a_new_style_with_a_minor_passes(self):
        self.edit_sty(*self.NEW_STYLE)
        self.bump("minor")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_a_removed_style_before_1_0_needs_a_minor(self):
        self.edit_sty(*self.NO_SMALL)
        self.bump("patch")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("removes style 'tn small'", out)
        self.git("checkout", "CHANGELOG.md", "tex/")
        self.edit_sty(*self.NO_SMALL)
        self.bump("minor")
        self.assertEqual(self.check()[0], 0)

    def test_a_removed_style_after_1_0_needs_a_major(self):
        self.edit_sty(" v0.", " v1.")  # make the base a 1.x release
        self.commit("1.x")
        self.edit_sty(*self.NO_SMALL)
        self.bump("minor")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("needs a major step", out)

    def test_a_changed_reference_image_needs_a_minor(self):
        (self.tmp / "tests/reference/a.svg").write_bytes(b"two")
        self.bump("patch")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("render", out)

    def test_two_steps_at_once_are_refused(self):
        self.edit_sty(*self.INTERNAL)
        self.bump("patch")
        self.bump("patch")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("not one step", out)

    # -- the CHANGELOG ------------------------------------------------------

    def test_bump_writes_the_version_and_the_changelog(self):
        before = self.version()
        self.bump("minor", "A reason.")
        after = self.version()
        self.assertNotEqual(before, after)
        text = (self.tmp / "CHANGELOG.md").read_text()
        self.assertIn(f"## v{after} — ", text)
        self.assertLess(text.index(f"## v{after}"), text.index(f"## v{before}"))
        self.assertEqual(self.run_version("notes", f"v{after}").stdout.strip(), "A reason.")

    def test_a_bump_left_as_todo_is_refused(self):
        self.edit_sty(*self.INTERNAL)
        self.bump("patch", "")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("TODO", out)

    # -- main is its release ------------------------------------------------

    def released(self):
        out = self.run_version("released")
        return out.returncode, out.stdout

    def test_released_needs_the_tag(self):
        code, out = self.released()
        self.assertEqual(code, 1)
        self.assertIn("there is no tag", out)

    def test_released_holds_when_the_package_is_the_tag(self):
        self.git("tag", f"v{self.version()}")
        (self.tmp / "README.md").write_text("docs move freely\n")
        self.commit("docs")
        self.assertEqual(self.released()[0], 0)

    def test_released_fails_when_the_package_moved_without_a_release(self):
        self.git("tag", f"v{self.version()}")
        self.edit_sty(*self.INTERNAL)
        self.commit("unreleased change")
        code, out = self.released()
        self.assertEqual(code, 1)
        self.assertIn("differs from that release in: tex/tikz-tensors.sty", out)

    def test_version_at_a_ref(self):
        base = self.version()
        self.bump("minor")
        self.assertEqual(self.run_version("--ref", "HEAD").stdout.strip(), base)


if __name__ == "__main__":
    unittest.main()

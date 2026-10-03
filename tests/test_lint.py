"""tests/lint.py: each rule fires on what it is for, and on nothing else.

    python3 -m unittest discover -s tests
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lint  # noqa: E402

HEAD = "\n".join(lint.HEAD) + "\n"
TAIL = "\n".join(lint.TAIL) + "\n"


class Rules(unittest.TestCase):
    def rules(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as f:
            f.write(text)
        path = pathlib.Path(f.name)
        self.addCleanup(path.unlink)
        return sorted({rule for _, rule, _ in lint.lint(path)})

    def body(self, *lines):
        return self.rules(HEAD + "\n".join(lines) + "\n" + TAIL)

    def test_a_figure_of_package_commands_passes(self):
        self.assertEqual(self.body(
            r"% a comment may say 3.5cm and \node[fill=red] (0,0)",
            r"\tnstack{S}{2}{ket}",
            r"\tnlayer{S}{ket}{canl/$A$, center/$C_{12}$}",
            r"\tnopen[label=$n_{#1}$]{down}{S}",
            r"\tnput[above]{S-ket-1}{$x = 0.5$}"), [])

    def test_lengths(self):
        for text in (r"\tnlegs{16mm}{S1-leg}", r"\tnlegs{1.6}{S1-leg}",
                     r"\tngate{U}{$U$}{S1-leg}{28.5mm}", r"\tnlegs{2 cm}{S1}"):
            self.assertIn("length", self.body(text), text)

    def test_a_factor_is_not_a_length(self):
        for text in (r"\tnstack[scale=0.6, rise=0.5]{S}{2}{a}",
                     r"\tnlayer[size=0.8]{S}{a}{2*canl/$A$}",
                     r"\tngrid[pitch=1.5]{P}{2}{2}{coef/$A$}",
                     r"\tnlayer{S}{a}{{canl, tn size=1.2}/$A$, canr/$B$}"):
            self.assertEqual(self.body(text), [], text)
        for text in (r"\tnstack[pitch=5mm]{S}{2}{a}", r"\tnstack[rise=0.5 cm]{S}{2}{a}",
                     r"\tnput[above=0.5]{S-a-1}{$x$}"):
            self.assertIn("length", self.body(text), text)
        # TikZ's own scale is still a key a role decides
        self.assertIn("key", self.body(r"\tnput[scale=2]{S-a-1}{$x$}"))

    def test_coordinates(self):
        self.assertIn("coord", self.body(r"\tnbond{(A) -- ++(0,-1)}"))
        self.assertNotIn("coord", self.body(r"\tnbond{(A1) -- (A2)}"))

    def test_keys_a_role_decides(self):
        for key in ("fill=red", "minimum width=7mm", "xshift=5mm",
                    "anchor=west", "draw=exact"):
            self.assertIn("key", self.body(rf"\tnbond[{key}]{{(A1) -- (A2)}}"), key)

    def test_raw_tikz_and_tex(self):
        for text in (r"\node[op] (O) at (A) {$O$};", r"\draw (A) -- (B);",
                     r"\begin{scope}", r"\end{scope}", r"\tikzset{x/.style={}}",
                     r"\pgfmathtruncatemacro{\c}{\b+1}", r"\tnbond{(A1) -- (A2)}",
                     r"\tnset{pitch=20mm}",
                     r"\foreach \i in {1,...,4} \tnput[below]{P-\i-down}{$\i$};"):
            self.assertIn("command", self.body(text), text)
        self.assertNotIn("command", self.body(r"\tnodes{A}"))
        self.assertNotIn("command", self.body(r"\tnjoin{A-ket-1:left}{A-ket-4:right}"))

    def test_the_frame(self):
        self.assertIn("frame", self.rules(
            HEAD.replace(r"\begin{tikzpicture}", r"\begin{tikzpicture}[x=1cm]")
            + TAIL))
        self.assertIn("frame", self.rules(
            HEAD.replace(r"\begin{document}", "\\def\\gap{6mm}\n\\begin{document}")
            + TAIL))
        self.assertIn("frame", self.rules(HEAD + TAIL + HEAD + TAIL))
        self.assertEqual(self.rules(HEAD + TAIL), [])


if __name__ == "__main__":
    unittest.main()

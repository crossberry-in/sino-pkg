#!/usr/bin/env python3
"""
Self-tests for the sino-pkg CLI.
Tests the core functionality: init, build, add, remove, semver, toml parsing.

Run: python3 tests/test_cli.py
"""

import os
import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Copy the sino script to a .py file so we can import it as a module
import shutil as _shutil
_sino_py = PROJECT_ROOT / "tests" / "_sino_import.py"
_shutil.copy2(PROJECT_ROOT / "sino", _sino_py)
import _sino_import as sino_module

SINO = str(PROJECT_ROOT / "sino")
if not Path(SINO).exists():
    SINO = shutil.which("sino") or "sino"


def run_sino(*args, cwd=None):
    """Run the sino CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, SINO] + list(args),
        capture_output=True, text=True, cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr


class TestSemVer(unittest.TestCase):
    """Test the SemVer parser."""

    def test_parse_simple(self):
        from _sino_import import SemVer
        v = SemVer.parse("1.2.3")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 3)

    def test_parse_with_v_prefix(self):
        from _sino_import import SemVer
        v = SemVer.parse("v1.2.3")
        self.assertEqual(v.major, 1)

    def test_parse_prerelease(self):
        from _sino_import import SemVer
        v = SemVer.parse("1.0.0-beta.1")
        self.assertEqual(v.pre, "beta.1")

    def test_comparison(self):
        from _sino_import import SemVer
        self.assertTrue(SemVer.parse("1.0.0") < SemVer.parse("2.0.0"))
        self.assertTrue(SemVer.parse("1.0.0") < SemVer.parse("1.1.0"))
        self.assertTrue(SemVer.parse("1.0.0") < SemVer.parse("1.0.1"))
        self.assertTrue(SemVer.parse("1.0.0") == SemVer.parse("1.0.0"))

    def test_version_req_caret(self):
        from _sino_import import SemVer, parse_version_req
        req = parse_version_req("^1.2.3")
        self.assertTrue(req(SemVer.parse("1.2.3")))
        self.assertTrue(req(SemVer.parse("1.3.0")))
        self.assertTrue(req(SemVer.parse("1.9.9")))
        self.assertFalse(req(SemVer.parse("2.0.0")))
        self.assertFalse(req(SemVer.parse("1.2.2")))

    def test_version_req_tilde(self):
        from _sino_import import SemVer, parse_version_req
        req = parse_version_req("~1.2.3")
        self.assertTrue(req(SemVer.parse("1.2.3")))
        self.assertTrue(req(SemVer.parse("1.2.9")))
        self.assertFalse(req(SemVer.parse("1.3.0")))

    def test_version_req_star(self):
        from _sino_import import SemVer, parse_version_req
        req = parse_version_req("*")
        self.assertTrue(req(SemVer.parse("1.0.0")))
        self.assertTrue(req(SemVer.parse("99.99.99")))

    def test_version_req_exact(self):
        from _sino_import import SemVer, parse_version_req
        req = parse_version_req("1.2.3")
        self.assertTrue(req(SemVer.parse("1.2.3")))
        self.assertFalse(req(SemVer.parse("1.2.4")))


class TestTOMLParser(unittest.TestCase):
    """Test the minimal TOML parser."""

    def test_basic_string(self):
        from _sino_import import parse_toml
        data = parse_toml('name = "math"')
        self.assertEqual(data["name"], "math")

    def test_integer(self):
        from _sino_import import parse_toml
        data = parse_toml("version = 42")
        self.assertEqual(data["version"], 42)

    def test_float(self):
        from _sino_import import parse_toml
        data = parse_toml("pi = 3.14")
        self.assertEqual(data["pi"], 3.14)

    def test_boolean(self):
        from _sino_import import parse_toml
        data = parse_toml("c = true\nrust = false")
        self.assertTrue(data["c"])
        self.assertFalse(data["rust"])

    def test_array(self):
        from _sino_import import parse_toml
        data = parse_toml('authors = ["Alice", "Bob"]')
        self.assertEqual(data["authors"], ["Alice", "Bob"])

    def test_section(self):
        from _sino_import import parse_toml
        text = '''
name = "math"

[build]
c = true
cpp = false
'''
        data = parse_toml(text)
        self.assertEqual(data["name"], "math")
        self.assertTrue(data["build"]["c"])
        self.assertFalse(data["build"]["cpp"])

    def test_nested_section(self):
        from _sino_import import parse_toml
        text = '''
[build.output]
type = "static"
'''
        data = parse_toml(text)
        self.assertEqual(data["build"]["output"]["type"], "static")

    def test_comments(self):
        from _sino_import import parse_toml
        text = '''
# This is a comment
name = "math"  # inline comment
'''
        data = parse_toml(text)
        self.assertEqual(data["name"], "math")


class TestCLICommands(unittest.TestCase):
    """Test the CLI commands end-to-end."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_version(self):
        rc, stdout, _ = run_sino("version")
        self.assertEqual(rc, 0)
        self.assertIn("sino-pkg", stdout)
        self.assertIn("1.1.0", stdout)

    def test_help(self):
        rc, stdout, _ = run_sino("help")
        self.assertEqual(rc, 0)
        self.assertIn("sino", stdout.lower())

    def test_init_lib(self):
        os.chdir(self.tmpdir)
        rc, _, stderr = run_sino("init", "--lib", "testlib")
        self.assertEqual(rc, 0)
        self.assertTrue(Path(self.tmpdir / "testlib" / "sino.toml").exists() if hasattr(self.tmpdir, '__truediv__') else (Path(self.tmpdir) / "testlib" / "sino.toml").exists())
        # Check structure
        lib_dir = Path(self.tmpdir) / "testlib"
        self.assertTrue((lib_dir / "sino.toml").exists())
        self.assertTrue((lib_dir / "src").is_dir())
        self.assertTrue((lib_dir / "native").is_dir())
        self.assertTrue((lib_dir / "include").is_dir())
        self.assertTrue((lib_dir / "tests").is_dir())
        self.assertTrue((lib_dir / "examples").is_dir())

    def test_init_bin(self):
        os.chdir(self.tmpdir)
        rc, _, _ = run_sino("init", "--bin", "testapp")
        self.assertEqual(rc, 0)
        app_dir = Path(self.tmpdir) / "testapp"
        self.assertTrue((app_dir / "sino.toml").exists())
        self.assertTrue((app_dir / "src" / "main.si").exists())

    def test_build_native(self):
        os.chdir(self.tmpdir)
        run_sino("init", "--lib", "buildtest")
        os.chdir(Path(self.tmpdir) / "buildtest")
        rc, _, stderr = run_sino("build", "--native")
        self.assertEqual(rc, 0, f"build --native failed: {stderr}")
        # Check .silib was created
        self.assertTrue((Path(self.tmpdir) / "buildtest" / "dist" / "buildtest.silib").exists())

    def test_add_remove(self):
        os.chdir(self.tmpdir)
        run_sino("init", "--lib", "deptest")
        os.chdir(Path(self.tmpdir) / "deptest")
        rc, _, _ = run_sino("add", "github:testuser/mydep", "1.0.0")
        self.assertEqual(rc, 0)
        # Check it was added to sino.toml
        toml = (Path(self.tmpdir) / "deptest" / "sino.toml").read_text()
        self.assertIn("github:testuser/mydep", toml)
        # Remove it
        rc, _, _ = run_sino("remove", "github:testuser/mydep")
        self.assertEqual(rc, 0)
        toml = (Path(self.tmpdir) / "deptest" / "sino.toml").read_text()
        self.assertNotIn("github:testuser/mydep", toml)


class TestSemVerSorting(unittest.TestCase):
    """Test semver sorting."""

    def test_sort(self):
        from _sino_import import SemVer
        versions = ["1.0.0", "1.10.0", "1.2.0", "2.0.0", "1.0.1"]
        parsed = [SemVer.parse(v) for v in versions]
        parsed.sort()
        result = [str(v) for v in parsed]
        self.assertEqual(result, ["1.0.0", "1.0.1", "1.2.0", "1.10.0", "2.0.0"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

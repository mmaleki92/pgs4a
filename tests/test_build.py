"""Tests for buildlib.build module - PatternList and utility functions."""

import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'buildlib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import build


class TestPatternList(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_simple_pattern(self):
        """Test simple filename pattern matching."""
        self.tmpfile.write("*.pyc\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        self.assertTrue(pl.match("test.pyc"))
        self.assertFalse(pl.match("test.py"))

    def test_double_star_pattern(self):
        """Test ** pattern matches across directories."""
        self.tmpfile.write("**/*.pyc\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        self.assertTrue(pl.match("dir/subdir/test.pyc"))
        self.assertTrue(pl.match("test.pyc"))

    def test_comment_ignored(self):
        """Test that comments are ignored in pattern files."""
        self.tmpfile.write("# This is a comment\n*.pyc\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        self.assertTrue(pl.match("test.pyc"))

    def test_empty_lines_ignored(self):
        """Test that empty lines are ignored."""
        self.tmpfile.write("\n\n*.pyc\n\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        self.assertTrue(pl.match("test.pyc"))

    def test_bracket_pattern(self):
        """Test bracket pattern matching."""
        self.tmpfile.write("*.[ch]\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        self.assertTrue(pl.match("test.c"))
        self.assertTrue(pl.match("test.h"))
        self.assertFalse(pl.match("test.py"))

    def test_slash_prefix_match(self):
        """Test that patterns match with leading slash added by match()."""
        self.tmpfile.write("*.pyc\n")
        self.tmpfile.close()
        pl = build.PatternList(self.tmpfile.name)
        # *.pyc matches only the filename part, not paths with directories
        self.assertTrue(pl.match("test.pyc"))
        # dir/test.pyc won't match *.pyc since * doesn't cross /
        self.assertFalse(pl.match("dir/test.pyc"))


class TestEditFile(unittest.TestCase):

    def test_edit_file(self):
        """Test editing a file by replacing matching lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("version=1.0\nname=test\nversion=old\n")
            tmppath = f.name

        try:
            build.edit_file(tmppath, r'^version=', 'version=2.0')
            with open(tmppath, 'r') as f:
                content = f.read()
            self.assertIn("version=2.0", content)
            self.assertIn("name=test", content)
        finally:
            os.unlink(tmppath)

    def test_edit_file_no_match(self):
        """Test editing a file with no matching lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("name=test\n")
            tmppath = f.name

        try:
            build.edit_file(tmppath, r'^version=', 'version=2.0')
            with open(tmppath, 'r') as f:
                content = f.read()
            self.assertEqual(content, "name=test\n")
        finally:
            os.unlink(tmppath)


class TestJoinAndCheck(unittest.TestCase):

    def test_existing_directory(self):
        """Test join_and_check with existing path."""
        result = build.join_and_check("/", "tmp")
        self.assertEqual(result, "/tmp")

    def test_nonexistent_directory(self):
        """Test join_and_check with non-existing path."""
        result = build.join_and_check("/tmp", "nonexistent_path_12345")
        self.assertIsNone(result)


class TestPatternCompile(unittest.TestCase):

    def test_compile_simple(self):
        """Test compiling simple glob pattern."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            tmppath = f.name
        try:
            pl = build.PatternList(tmppath)
            pattern = pl.compile("*.py")
            self.assertIsNotNone(pattern.match("test.py"))
            self.assertIsNone(pattern.match("test.pyc"))
        finally:
            os.unlink(tmppath)

    def test_compile_doublestar(self):
        """Test compiling ** glob pattern."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            tmppath = f.name
        try:
            pl = build.PatternList(tmppath)
            pattern = pl.compile("**/*.py")
            self.assertIsNotNone(pattern.match("a/b/c/test.py"))
        finally:
            os.unlink(tmppath)


if __name__ == "__main__":
    unittest.main()

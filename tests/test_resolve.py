"""Tests for resolve.py."""

import unittest

from importlab import fs
from importlab import parsepy
from importlab import resolve
from importlab import utils


FILES = {
        "a.py": "contents of a",
        "b.py": "contents of b",
        "foo/c.py": "contents of c",
        "foo/d.py": "contents of d",
        "bar/e.py": "contents of e"
}


class TestResolver(unittest.TestCase):
    """Tests for Resolver."""

    def setUp(self):
        self.path = [fs.StoredFileSystem(FILES)]

    def testResolveTopLevel(self):
        imp = parsepy.ImportStatement("a")
        r = resolve.Resolver(self.path, "b.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "a.py")

    def testResolvePackageFile(self):
        imp = parsepy.ImportStatement("foo.c")
        r = resolve.Resolver(self.path, "b.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "foo/c.py")

    def testResolveSamePackageFile(self):
        imp = parsepy.ImportStatement(".c")
        r = resolve.Resolver(self.path, "foo/d.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "foo/c.py")

    def testResolveParentPackageFile(self):
        imp = parsepy.ImportStatement("..a")
        r = resolve.Resolver(self.path, "foo/d.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "a.py")

    def testResolveSiblingPackageFile(self):
        imp = parsepy.ImportStatement("..bar.e")
        r = resolve.Resolver(self.path, "foo/d.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "bar/e.py")

    def testResolveModuleFromFile(self):
        # from foo import c
        imp = parsepy.ImportStatement("foo.c", is_from=True)
        r = resolve.Resolver(self.path, "x.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "foo/c.py")

    def testResolveSymbolFromFile(self):
        # from foo.c import X
        imp = parsepy.ImportStatement("foo.c.X", is_from=True)
        r = resolve.Resolver(self.path, "x.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "foo/c.py")

    def testOverrideSource(self):
        imp = parsepy.ImportStatement("foo.c", source="/system/c.py")
        r = resolve.Resolver(self.path, "x.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "foo/c.py")

    def testFallBackToSource(self):
        imp = parsepy.ImportStatement("f", source="/system/f.py")
        r = resolve.Resolver(self.path, "x.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "/system/f.py")

    def testGetPyFromPycSource(self):
        # Override a source pyc file with the corresponding py file if it exists
        # in the native filesystem.
        with utils.Tempdir() as d:
            py_file = d.create_file('f.py')
            pyc_file = d.create_file('f.pyc')
            imp = parsepy.ImportStatement("f", source=pyc_file)
            r = resolve.Resolver(self.path, "x.py")
            fname = r.resolve_import(imp)
            self.assertEqual(fname, py_file)

    def testPycSourceWithoutPy(self):
        imp = parsepy.ImportStatement("f", source="/system/f.pyc")
        r = resolve.Resolver(self.path, "x.py")
        fname = r.resolve_import(imp)
        self.assertEqual(fname, "/system/f.pyc")

if __name__ == "__main__":
    unittest.main()

"""Tests for buildlib.configure module."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'buildlib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import configure


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        config_path = os.path.join(self.tmpdir, ".android.json")
        if os.path.exists(config_path):
            os.unlink(config_path)
        os.rmdir(self.tmpdir)

    def test_default_values(self):
        """Test that Configuration has correct default values."""
        config = configure.Configuration(self.tmpdir)
        self.assertIsNone(config.package)
        self.assertIsNone(config.name)
        self.assertIsNone(config.icon_name)
        self.assertIsNone(config.version)
        self.assertIsNone(config.numeric_version)
        self.assertEqual(config.orientation, "user")
        self.assertEqual(config.permissions, [])
        self.assertFalse(config.include_pil)
        self.assertFalse(config.include_sqlite)
        self.assertEqual(config.layout, "internal")
        self.assertFalse(config.source)
        self.assertFalse(config.expansion)
        self.assertEqual(config.targetsdk, 33)

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        config = configure.Configuration(self.tmpdir)
        config.package = "com.test.app"
        config.name = "Test App"
        config.version = "1.0.0"
        config.save(self.tmpdir)

        # Verify file exists
        config_path = os.path.join(self.tmpdir, ".android.json")
        self.assertTrue(os.path.exists(config_path))

        # Verify JSON content
        with open(config_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["package"], "com.test.app")
        self.assertEqual(data["name"], "Test App")
        self.assertEqual(data["version"], "1.0.0")

        # Verify loading
        config2 = configure.Configuration(self.tmpdir)
        self.assertEqual(config2.package, "com.test.app")
        self.assertEqual(config2.name, "Test App")
        self.assertEqual(config2.version, "1.0.0")

    def test_set_version(self):
        """Test version number parsing."""
        config = configure.Configuration(self.tmpdir)
        configure.set_version(config, "1.2.3")
        self.assertEqual(config.version, "1.2.3")
        self.assertEqual(config.numeric_version, "10203")

    def test_set_version_simple(self):
        """Test simple version number."""
        config = configure.Configuration(self.tmpdir)
        configure.set_version(config, "2.0")
        self.assertEqual(config.version, "2.0")
        self.assertEqual(config.numeric_version, "200")

    def test_set_version_invalid(self):
        """Test invalid version string doesn't crash."""
        config = configure.Configuration(self.tmpdir)
        config.numeric_version = "999"
        configure.set_version(config, "abc")
        self.assertEqual(config.version, "abc")
        # numeric_version should remain unchanged on error
        self.assertEqual(config.numeric_version, "999")

    def test_load_nonexistent_config(self):
        """Test loading from directory without config file."""
        config = configure.Configuration(self.tmpdir)
        # Should not raise, just use defaults
        self.assertIsNone(config.package)


class TestSetConfig(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        config_path = os.path.join(self.tmpdir, ".android.json")
        if os.path.exists(config_path):
            os.unlink(config_path)
        os.rmdir(self.tmpdir)

    def test_set_config_version(self):
        """Test set_config with version variable."""
        class MockInterface:
            def fail(self, msg):
                raise RuntimeError(msg)

        iface = MockInterface()
        # Create initial config
        config = configure.Configuration(self.tmpdir)
        config.save(self.tmpdir)

        configure.set_config(iface, self.tmpdir, "version", "3.2.1")

        config2 = configure.Configuration(self.tmpdir)
        self.assertEqual(config2.version, "3.2.1")
        self.assertEqual(config2.numeric_version, "30201")

    def test_set_config_permissions(self):
        """Test set_config with permissions."""
        class MockInterface:
            def fail(self, msg):
                raise RuntimeError(msg)

        iface = MockInterface()
        config = configure.Configuration(self.tmpdir)
        config.save(self.tmpdir)

        configure.set_config(iface, self.tmpdir, "permissions", "INTERNET VIBRATE")

        config2 = configure.Configuration(self.tmpdir)
        self.assertEqual(config2.permissions, ["INTERNET", "VIBRATE"])

    def test_set_config_unknown_var(self):
        """Test set_config with unknown variable."""
        class MockInterface:
            def fail(self, msg):
                raise RuntimeError(msg)

        iface = MockInterface()
        config = configure.Configuration(self.tmpdir)
        config.save(self.tmpdir)

        with self.assertRaises(RuntimeError):
            configure.set_config(iface, self.tmpdir, "nonexistent_var", "value")


if __name__ == "__main__":
    unittest.main()

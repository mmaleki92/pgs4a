"""Tests for buildlib.install_sdk module - SDK URL configuration and error handling."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'buildlib'))

import install_sdk


class TestSDKUrls(unittest.TestCase):
    """Test that Android SDK download URLs use the correct version."""

    def test_cmdline_tools_version_linux(self):
        """Test that the Linux cmdline-tools URL uses the current version."""
        with patch('install_sdk.plat') as mock_plat:
            mock_plat.windows = False
            mock_plat.macintosh = False
            mock_plat.linux = True

            mock_iface = MagicMock()
            # Make os.path.exists return False so we don't skip
            with patch('os.path.exists', return_value=False):
                # Set PGS4A_NO_TERMS to skip terms acceptance
                with patch.dict(os.environ, {"PGS4A_NO_TERMS": "1"}):
                    # Mock urlretrieve to prevent actual download
                    with patch('install_sdk.urllib.request.urlretrieve') as mock_retrieve:
                        # Mock the zip extraction and directory operations
                        with patch('install_sdk.zipfile.ZipFile'):
                            with patch('install_sdk.shutil.move'):
                                with patch('os.makedirs'):
                                    with patch('os.chmod'):
                                        try:
                                            install_sdk.unpack_sdk(mock_iface)
                                        except Exception:
                                            pass  # May fail on other steps

                        # Check the first call to urlretrieve (cmdline-tools)
                        first_call_url = mock_retrieve.call_args_list[0][0][0]
                        self.assertIn("13114758", first_call_url,
                            "cmdline-tools URL should use version 13114758, got: " + first_call_url)
                        self.assertNotIn("11076708", first_call_url,
                            "cmdline-tools URL should NOT use old version 11076708")
                        self.assertEqual(first_call_url,
                            "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip")

    def test_cmdline_tools_version_windows(self):
        """Test that the Windows cmdline-tools URL uses the current version."""
        with patch('install_sdk.plat') as mock_plat:
            mock_plat.windows = True
            mock_plat.macintosh = False
            mock_plat.linux = False

            mock_iface = MagicMock()
            with patch('os.path.exists', return_value=False):
                with patch.dict(os.environ, {"PGS4A_NO_TERMS": "1"}):
                    with patch('install_sdk.urllib.request.urlretrieve') as mock_retrieve:
                        with patch('install_sdk.zipfile.ZipFile'):
                            with patch('install_sdk.shutil.move'):
                                with patch('os.makedirs'):
                                    try:
                                        install_sdk.unpack_sdk(mock_iface)
                                    except Exception:
                                        pass

                        first_call_url = mock_retrieve.call_args_list[0][0][0]
                        self.assertEqual(first_call_url,
                            "https://dl.google.com/android/repository/commandlinetools-win-13114758_latest.zip")

    def test_cmdline_tools_version_mac(self):
        """Test that the macOS cmdline-tools URL uses the current version."""
        with patch('install_sdk.plat') as mock_plat:
            mock_plat.windows = False
            mock_plat.macintosh = True
            mock_plat.linux = False

            mock_iface = MagicMock()
            with patch('os.path.exists', return_value=False):
                with patch.dict(os.environ, {"PGS4A_NO_TERMS": "1"}):
                    with patch('install_sdk.urllib.request.urlretrieve') as mock_retrieve:
                        with patch('install_sdk.zipfile.ZipFile'):
                            with patch('install_sdk.shutil.move'):
                                with patch('os.makedirs'):
                                    with patch('os.chmod'):
                                        try:
                                            install_sdk.unpack_sdk(mock_iface)
                                        except Exception:
                                            pass

                        first_call_url = mock_retrieve.call_args_list[0][0][0]
                        self.assertEqual(first_call_url,
                            "https://dl.google.com/android/repository/commandlinetools-mac-13114758_latest.zip")


class TestDownloadErrorHandling(unittest.TestCase):
    """Test that download failures produce helpful error messages."""

    def test_http_error_on_cmdline_tools_calls_fail(self):
        """Test that an HTTP 404 on cmdline-tools download calls interface.fail()."""
        import urllib.error

        with patch('install_sdk.plat') as mock_plat:
            mock_plat.windows = False
            mock_plat.macintosh = False
            mock_plat.linux = True

            mock_iface = MagicMock()
            # Make interface.fail raise SystemExit like the real one
            mock_iface.fail.side_effect = SystemExit(-1)

            with patch('os.path.exists', return_value=False):
                with patch.dict(os.environ, {"PGS4A_NO_TERMS": "1"}):
                    with patch('install_sdk.urllib.request.urlretrieve') as mock_retrieve:
                        mock_retrieve.side_effect = urllib.error.HTTPError(
                            "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip",
                            404, "Not Found", {}, None)

                        with self.assertRaises(SystemExit):
                            install_sdk.unpack_sdk(mock_iface)

                        # Verify fail was called with a helpful message
                        mock_iface.fail.assert_called_once()
                        fail_msg = mock_iface.fail.call_args[0][0]
                        self.assertIn("Failed to download", fail_msg)
                        self.assertIn("404", fail_msg)

    def test_url_error_on_ant_calls_fail(self):
        """Test that a network error on Ant download calls interface.fail()."""
        import urllib.error

        with patch('install_sdk.plat') as mock_plat:
            mock_plat.windows = False
            mock_plat.macintosh = False
            mock_plat.linux = True

            mock_iface = MagicMock()
            mock_iface.fail.side_effect = SystemExit(-1)

            with patch('os.path.exists', return_value=False):
                with patch('install_sdk.urllib.request.urlretrieve') as mock_retrieve:
                    mock_retrieve.side_effect = urllib.error.URLError("Connection refused")

                    with self.assertRaises(SystemExit):
                        install_sdk.unpack_ant(mock_iface)

                    mock_iface.fail.assert_called_once()
                    fail_msg = mock_iface.fail.call_args[0][0]
                    self.assertIn("Failed to download", fail_msg)
                    self.assertIn("internet connection", fail_msg)


if __name__ == "__main__":
    unittest.main()

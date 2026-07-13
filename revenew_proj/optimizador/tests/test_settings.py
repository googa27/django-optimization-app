import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class SecuritySettingsTest(SimpleTestCase):
    def test_debug_defaults_to_false(self):
        self.assertFalse(settings.DEBUG)

    def test_allowed_hosts_are_explicit_for_local_and_tests(self):
        self.assertIn("localhost", settings.ALLOWED_HOSTS)
        self.assertIn("127.0.0.1", settings.ALLOWED_HOSTS)
        self.assertIn("testserver", settings.ALLOWED_HOSTS)

    def test_upload_size_limits_are_configured(self):
        self.assertGreater(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 0)
        self.assertLessEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 1024 * 1024)
        self.assertEqual(
            settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
            settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
        )

    def test_secure_cookie_defaults_follow_non_debug_mode(self):
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)

    def test_production_settings_require_secret_key(self):
        env = os.environ.copy()
        env.pop("DJANGO_SECRET_KEY", None)
        env.pop("DJANGO_ALLOW_INSECURE_DEV_SECRET", None)
        env["DJANGO_DEBUG"] = "False"
        env["DJANGO_SETTINGS_MODULE"] = "revenew_proj.settings"

        result = subprocess.run(
            [sys.executable, "-c", "import django; django.setup()"],
            cwd=settings.BASE_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY is required", result.stderr)

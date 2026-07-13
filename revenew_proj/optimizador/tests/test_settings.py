import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class SecuritySettingsTest(SimpleTestCase):
    def _settings_subprocess_env(self):
        env = os.environ.copy()
        env.setdefault("DJANGO_SECRET_KEY", "test-secret")
        env["DJANGO_SETTINGS_MODULE"] = "revenew_proj.settings"
        return env

    def test_debug_defaults_to_false(self):
        self.assertFalse(settings.DEBUG)

    def test_allowed_hosts_are_explicit_for_local_and_tests(self):
        self.assertIn("localhost", settings.ALLOWED_HOSTS)
        self.assertIn("127.0.0.1", settings.ALLOWED_HOSTS)
        self.assertIn("testserver", settings.ALLOWED_HOSTS)

    def test_csrf_trusted_origins_prepend_https_to_bare_origins(self):
        env = self._settings_subprocess_env()
        env["DJANGO_CSRF_TRUSTED_ORIGINS"] = (
            "example.com:8443, http://localhost:8000"
        )

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django.conf import settings; "
                "import json; "
                "print(json.dumps(settings.CSRF_TRUSTED_ORIGINS))",
            ],
            cwd=settings.BASE_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            ["https://example.com:8443", "http://localhost:8000"],
        )

    def test_csrf_trusted_origins_reject_non_origin_values(self):
        env = self._settings_subprocess_env()
        env["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://example.com/path"

        result = subprocess.run(
            [sys.executable, "-c", "import django; django.setup()"],
            cwd=settings.BASE_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_CSRF_TRUSTED_ORIGINS entries", result.stderr)

    def test_upload_size_limits_are_configured(self):
        configured_limit = int(os.getenv("OPTIMIZADOR_MAX_UPLOAD_BYTES", "1048576"))

        self.assertGreater(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 0)
        self.assertEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, configured_limit)
        self.assertEqual(
            settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
            settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
        )

    def test_upload_size_limits_honor_environment_override(self):
        env = self._settings_subprocess_env()
        env["OPTIMIZADOR_MAX_UPLOAD_BYTES"] = "2097152"

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django.conf import settings; "
                "import json; "
                "print(json.dumps([settings.FILE_UPLOAD_MAX_MEMORY_SIZE, "
                "settings.DATA_UPLOAD_MAX_MEMORY_SIZE]))",
            ],
            cwd=settings.BASE_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [2097152, 2097152])

    def test_secure_cookie_defaults_follow_non_debug_mode(self):
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)

    def test_production_settings_require_secret_key(self):
        env = self._settings_subprocess_env()
        env.pop("DJANGO_SECRET_KEY", None)
        env.pop("DJANGO_ALLOW_INSECURE_DEV_SECRET", None)
        env["DJANGO_DEBUG"] = "False"

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

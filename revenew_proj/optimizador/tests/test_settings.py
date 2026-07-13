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
            settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 8192,
        )

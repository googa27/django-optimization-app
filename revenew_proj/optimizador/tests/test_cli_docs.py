from pathlib import Path

from django.test import SimpleTestCase


class ReadmeCliDocumentationTest(SimpleTestCase):
    def test_readme_documents_verified_cli_route_from_real_app_directory(self):
        readme = Path(__file__).resolve().parents[3] / "README.md"
        text = readme.read_text(encoding="utf-8")

        self.assertIn("Command-line route status", text)
        self.assertIn("cd revenew_proj", text)
        self.assertIn(
            "DJANGO_SECRET_KEY=*** uv run --with-requirements ../requirements.txt "
            "python main.py optimization_problem_data.csv",
            text,
        )
        self.assertIn("there is no root `manage.py` or root `main.py`", text)
        self.assertNotIn("Broken/unverified", text)
        self.assertNotIn("CLI route is documented as broken", text)

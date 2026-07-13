from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from optimizador.forms import UploadForm, MAX_UPLOAD_BYTES


class UploadFormBoundaryTest(SimpleTestCase):
    def test_rejects_non_csv_extension(self):
        upload = SimpleUploadedFile("params.txt", b"x,y\n1,2\n", content_type="text/plain")
        form = UploadForm(data={}, files={"csv_file": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("Only .csv files are supported.", form.errors["csv_file"])

    def test_rejects_unexpected_content_type(self):
        upload = SimpleUploadedFile(
            "params.csv", b"x,y\n1,2\n", content_type="application/x-msdownload"
        )
        form = UploadForm(data={}, files={"csv_file": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("Uploaded file must be a CSV text file.", form.errors["csv_file"])

    def test_rejects_generic_octet_stream_content_type(self):
        upload = SimpleUploadedFile(
            "params.csv", b"x,y\n1,2\n", content_type="application/octet-stream"
        )
        form = UploadForm(data={}, files={"csv_file": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("Uploaded file must be a CSV text file.", form.errors["csv_file"])

    def test_rejects_oversized_upload(self):
        upload = SimpleUploadedFile(
            "params.csv", b"a" * (MAX_UPLOAD_BYTES + 1), content_type="text/csv"
        )
        form = UploadForm(data={}, files={"csv_file": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("CSV file is too large", form.errors["csv_file"][0])

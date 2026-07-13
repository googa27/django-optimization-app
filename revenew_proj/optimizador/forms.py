from __future__ import annotations

import os
from pathlib import Path

from django import forms

MAX_UPLOAD_BYTES = int(os.getenv("OPTIMIZADOR_MAX_UPLOAD_BYTES", "1048576"))
ALLOWED_CSV_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "text/plain",
    "application/octet-stream",
}


class UploadForm(forms.Form):
    """Validate the single CSV upload boundary before parsing optimization data."""

    csv_file = forms.FileField(label="Upload CSV")

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        name = Path(getattr(csv_file, "name", ""))
        if name.suffix.lower() != ".csv":
            raise forms.ValidationError("Only .csv files are supported.")
        size = getattr(csv_file, "size", 0)
        if size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError(
                f"CSV file is too large; maximum is {MAX_UPLOAD_BYTES} bytes."
            )
        content_type = getattr(csv_file, "content_type", None)
        if content_type and content_type.lower() not in ALLOWED_CSV_CONTENT_TYPES:
            raise forms.ValidationError("Uploaded file must be a CSV text file.")
        return csv_file

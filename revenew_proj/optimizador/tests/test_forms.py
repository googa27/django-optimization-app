from django import forms
# This might be useful for custom validators, but not directly for this fix.
from django.core.exceptions import ValidationError


class UploadForm(forms.Form):
    '''Form for uploading a CSV file containing production parameters.
    This form includes a single file field for the CSV upload.
    Attributes:
        csv_file (FileField): The file field for uploading the CSV.
    '''
    csv_file = forms.FileField(label="Upload CSV")

    def clean_csv_file(self):
        """
        Custom clean method for csv_file.
        Ensures that the form itself does not invalidate an empty file,
        as content validation is handled by DataLoader.
        """
        csv_file = self.cleaned_data['csv_file']

        # If the file exists and has zero size, we allow it to pass form validation.
        # The DataLoader will handle the actual content validation for emptiness or malformed data.
        if csv_file.size == 0:
            return csv_file

        # For non-empty files, return as is
        return csv_file

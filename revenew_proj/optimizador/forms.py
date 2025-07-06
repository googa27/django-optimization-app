from django import forms


class UploadForm(forms.Form):
    '''Form for uploading a CSV file containing production parameters.
    This form includes a single file field for the CSV upload.
    Attributes:
        csv_file (FileField): The file field for uploading the CSV.
    '''
    csv_file = forms.FileField(label="Upload CSV",)

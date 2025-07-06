from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from io import StringIO
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile


class UploadViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('upload')

        # Define a valid CSV content string
        self.valid_csv_content = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A,Price_Product_B
10,15,600,5,8,480,25,30
"""
        self.valid_params = {
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 15,
            'Machine_1_Available_Hours': 600,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 8,
            'Machine_2_Available_Hours': 480,
            'Price_Product_A': 25,
            'Price_Product_B': 30
        }
        self.optimal_solution = {
            'status': 'Optimal',
            'Product_A': 60.0,
            'Product_B': 0.0,
            'Total_Revenue': 1500.0,
            'LpStatus': 1
        }
        self.formatted_result = {
            'status': 'Optimal',
            'Product_A': 60.0,
            'Product_B': 0.0,
            'Total_Revenue': 1500.0,
            'plot': 'base64_string_of_plot'  # Mock plot string
        }

    def test_get_request_displays_form(self):
        """Test that a GET request displays the upload form."""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'optimizador/upload.html')
        # Check for text on the form page
        self.assertContains(response, 'Upload CSV')

    # MODIFICATION HERE: Patch DataLoader in 'optimizador.views'

    @patch('optimizador.views.DataLoader')
    def test_post_request_invalid_csv_validation_error(self, MockDataLoader):
        """Test handling of an invalid CSV that raises ValidationError from DataLoader."""
        # Mock DataLoader's load method to raise a ValidationError
        MockDataLoader.return_value.load.side_effect = ValidationError(
            "Test invalid data error")

        mock_invalid_file = SimpleUploadedFile(
            "invalid.csv",
            b"invalid content",
            content_type="text/csv"
        )

        response = self.client.post(
            self.upload_url, {'csv_file': mock_invalid_file})

        # Should redirect back to the upload form with an error message
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'optimizador/upload.html')
        # This assertion should now pass, as the mock's error message will be displayed
        self.assertContains(response, "Test invalid data error")
        MockDataLoader.assert_called_once()

    def test_post_request_no_file(self):
        """Test POST request without a file (form validation error)."""
        response = self.client.post(self.upload_url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'optimizador/upload.html')
        self.assertContains(response, "This field is required.")

import unittest
import pandas as pd
from io import StringIO
from django.core.exceptions import ValidationError

# Assuming dataloader.py is in the same directory as this test file,
# or reachable via optimizador.dataloader
from optimizador.dataloader import DataLoader


class DataLoaderTest(unittest.TestCase):

    def setUp(self):
        # Define valid and invalid CSV content for testing
        self.valid_csv_content = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A,Price_Product_B
10,15,600,5,8,480,25,30
"""
        self.invalid_missing_col_csv = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A
10,15,600,5,8,480,25
"""  # Missing Price_Product_B

        self.invalid_non_numeric_csv = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A,Price_Product_B
10,invalid,600,5,8,480,25,30
"""

        self.invalid_negative_value_csv = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A,Price_Product_B
-10,15,600,5,8,480,25,30
"""

        self.invalid_multiple_rows_csv = """Product_A_Production_Time_Machine_1,Product_B_Production_Time_Machine_1,Machine_1_Available_Hours,Product_A_Production_Time_Machine_2,Product_B_Production_Time_Machine_2,Machine_2_Available_Hours,Price_Product_A,Price_Product_B
10,15,600,5,8,480,25,30
20,25,700,10,12,500,30,40
"""
        self.empty_csv = ""
        self.non_csv_content = "This is not a CSV."

    def test_load_valid_csv(self):
        """Test that a valid CSV loads correctly and returns expected parameters."""
        csv_file = StringIO(self.valid_csv_content)
        loader = DataLoader(csv_file)
        params = loader.load()

        expected_params = {
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 15,
            'Machine_1_Available_Hours': 600,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 8,
            'Machine_2_Available_Hours': 480,
            'Price_Product_A': 25,
            'Price_Product_B': 30
        }
        self.assertIsInstance(params, dict)
        self.assertEqual(params, expected_params)

    def test_load_invalid_missing_columns(self):
        """Test that a CSV with missing required columns raises ValidationError."""
        csv_file = StringIO(self.invalid_missing_col_csv)
        loader = DataLoader(csv_file)
        with self.assertRaisesRegex(ValidationError, "Missing required columns:"):
            loader.load()

    def test_load_invalid_non_numeric_values(self):
        """Test that a CSV with non-numeric values raises ValidationError."""
        csv_file = StringIO(self.invalid_non_numeric_csv)
        loader = DataLoader(csv_file)
        with self.assertRaisesRegex(ValidationError, "CSV contains non-numeric values in required columns."):
            loader.load()

    def test_load_invalid_negative_values(self):
        """Test that a CSV with negative values raises ValidationError."""
        csv_file = StringIO(self.invalid_negative_value_csv)
        loader = DataLoader(csv_file)
        with self.assertRaisesRegex(ValidationError, "CSV contains negative values in required columns."):
            loader.load()

    def test_load_invalid_multiple_rows(self):
        """Test that a CSV with more than one row raises ValidationError."""
        csv_file = StringIO(self.invalid_multiple_rows_csv)
        loader = DataLoader(csv_file)
        with self.assertRaisesRegex(ValidationError, "CSV should contain exactly one row of parameters."):
            loader.load()

    def test_load_empty_csv(self):
        """Test that an empty CSV file raises an error (likely pandas error)."""
        csv_file = StringIO(self.empty_csv)
        loader = DataLoader(csv_file)
        # Expecting a ValidationError from DataLoader's try-except
        with self.assertRaises(ValidationError):
            loader.load()

    def test_load_non_csv_content(self):
        """Test that non-CSV content raises an error."""
        csv_file = StringIO(self.non_csv_content)
        loader = DataLoader(csv_file)
        with self.assertRaises(ValidationError):
            loader.load()

    def test_data_loader_required_columns(self):
        """Test that the DataLoader has the correct required columns defined."""
        # This test ensures the internal consistency of the DataLoader
        expected_columns = [
            'Product_A_Production_Time_Machine_1',
            'Product_B_Production_Time_Machine_1',
            'Product_A_Production_Time_Machine_2',
            'Product_B_Production_Time_Machine_2',
            'Machine_1_Available_Hours',
            'Machine_2_Available_Hours',
            'Price_Product_A',
            'Price_Product_B'
        ]
        # Using sorted() for comparison to ignore order
        self.assertEqual(sorted(DataLoader.REQUIRED_COLUMNS),
                         sorted(expected_columns))

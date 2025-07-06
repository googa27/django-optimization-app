import pandas as pd
from django.core.exceptions import ValidationError


class DataLoader:
    '''
    Class to load and validate CSV data for the optimization problem.
    It checks for required columns, ensures numeric values, and validates
    the data types.
    Attributes:
        file (str): Path to the CSV file.
        REQUIRED_COLUMNS (list): List of required columns in the CSV.
    '''
    PRODUCTS = ['A', 'B']
    MACHINES = [1, 2]

    REQUIRED_COLUMNS = [
        *[f'Product_{p}_Production_Time_Machine_{m}'
          for m in MACHINES
          for p in ['A', 'B']],
        *[f'Machine_{m}_Available_Hours'
          for m in MACHINES],
        *[f'Price_Product_{p}'
          for p in PRODUCTS]
    ]

    def __init__(self, file):
        '''
        Initializes the DataLoader with the file path.
        Args:
            file (str): Path to the CSV file.
        '''
        self.file = file

    def load(self):
        '''
        Loads and validates the CSV file.
        Returns:
            dict: A dictionary containing the validated parameters.
        Raises:
            ValidationError: If the CSV file is invalid.
        '''
        try:
            # Load CSV into DataFrame
            df = pd.read_csv(self.file)
        except Exception as e:
            raise ValidationError(f"Error reading CSV file: {e}")

        # Ensure required columns are present
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValidationError(f"Missing required columns: {missing}")

        # Ensure all required columns are numeric
        if not df[self.REQUIRED_COLUMNS].apply(pd.to_numeric, errors='coerce').notnull().all().all():
            raise ValidationError(
                "CSV contains non-numeric values in required columns.")

        # Check that all required values are non-negative
        if (df[self.REQUIRED_COLUMNS] < 0).any().any():
            raise ValidationError(
                "CSV contains negative values in required columns.")

        # Optional: check if there is exactly one row
        if len(df) != 1:
            raise ValidationError(
                "CSV should contain exactly one row of parameters.")

        # Return the clean row as a dictionary
        return df.iloc[0].to_dict()

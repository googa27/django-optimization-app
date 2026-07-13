import unittest
from optimizador.results import ResultsHandler


class ResultsHandlerTest(unittest.TestCase):

    def setUp(self):
        self.params = {
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 15,
            'Machine_1_Available_Hours': 600,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 8,
            'Machine_2_Available_Hours': 480,
        }

    def test_format_optimal_solution(self):
        """Test formatting of an optimal solution."""
        optimal_solution = {
            'status': 'Optimal',
            'Product_A': 100,
            'Product_B': 50,
            'Total_Revenue': 5000,
            'LpStatus': 1  # Simulating pulp's internal status code for optimal
        }
        handler = ResultsHandler(optimal_solution, self.params)
        formatted_result = handler.format()

        self.assertIsInstance(formatted_result, dict)
        self.assertEqual(formatted_result['status'], 'Optimal')
        self.assertAlmostEqual(formatted_result['Product_A'], 100.0, places=2)
        self.assertAlmostEqual(formatted_result['Product_B'], 50.0, places=2)
        self.assertAlmostEqual(
            formatted_result['Total_Revenue'], 5000.0, places=2)
        self.assertIn('plot', formatted_result)
        self.assertIsInstance(formatted_result['plot'], str)
        # Plot string should not be empty
        self.assertTrue(len(formatted_result['plot']) > 0)

    def test_format_infeasible_solution(self):
        """Test formatting of an infeasible solution."""
        infeasible_solution = {
            'status': 'Infeasible',
            'Product_A': None,
            'Product_B': None,
            'Total_Revenue': None,
            'LpStatus': -1  # Simulating pulp's internal status code for infeasible
        }
        handler = ResultsHandler(infeasible_solution, self.params)
        formatted_result = handler.format()

        self.assertIsInstance(formatted_result, dict)
        self.assertEqual(formatted_result['status'], 'Infeasible')
        self.assertIn('error', formatted_result)
        self.assertIsNone(formatted_result['Product_A'])
        self.assertIsNone(formatted_result['Product_B'])
        self.assertIsNone(formatted_result['Total_Revenue'])
        # Plot should be None for errors
        self.assertIsNone(formatted_result['plot'])

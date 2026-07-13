import unittest
from optimizador.results import ResultsHandler
from optimizador.services import OptimizationSolution, ProductionParameters


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

    def test_format_accepts_typed_service_result_and_parameters(self):
        params = ProductionParameters.from_mapping({
            **self.params,
            'Price_Product_A': 25,
            'Price_Product_B': 30,
        })
        solution = OptimizationSolution(
            status='Optimal',
            product_a=60.0,
            product_b=0.0,
            total_revenue=1500.0,
        )

        formatted_result = ResultsHandler(solution, params).format()

        self.assertEqual(formatted_result['status'], 'Optimal')
        self.assertAlmostEqual(formatted_result['Product_A'], 60.0, places=2)
        self.assertAlmostEqual(formatted_result['Product_B'], 0.0, places=2)
        self.assertAlmostEqual(formatted_result['Total_Revenue'], 1500.0, places=2)
        self.assertTrue(formatted_result['plot'].startswith('data:image/png;base64,'))

    def test_feasible_region_plot_handles_zero_time_coefficients(self):
        params = {
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 0,
            'Machine_1_Available_Hours': 600,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 0,
            'Machine_2_Available_Hours': 480,
        }
        solution = {
            'status': 'Optimal',
            'Product_A': 60.0,
            'Product_B': 0.0,
            'Total_Revenue': 1500.0,
        }

        formatted_result = ResultsHandler(solution, params).format()

        self.assertTrue(
            formatted_result['feasible_region_plot'].startswith('data:image/png;base64,')
        )

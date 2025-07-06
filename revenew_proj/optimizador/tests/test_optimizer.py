import unittest
from pulp import LpStatus, value

# Assuming optimizer.py is in the same directory as this test file,
# or reachable via optimizador.optimizer
from optimizador.optimizer import OptimizationModel


class OptimizationModelTest(unittest.TestCase):

    def test_optimal_solution(self):
        """Test the optimizer with parameters leading to an optimal solution."""
        params = {
            'Price_Product_A': 25,
            'Price_Product_B': 30,
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 15,
            'Machine_1_Available_Hours': 600,  # e.g., 10 hours * 60 min/hr
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 8,
            'Machine_2_Available_Hours': 480,  # e.g., 8 hours * 60 min/hr
        }
        model = OptimizationModel(params)
        solution = model.solve()

        # Check status
        # LpStatus[1] is 'Optimal'
        self.assertEqual(solution['status'], LpStatus[1])

        # Check quantities (these might be floats, allow for small tolerance)
        # Expected solution: (x_A, x_B) = (60, 0)
        # Machine 1: 10*60 + 15*0 = 600 <= 600 (tight)
        # Machine 2: 5*60 + 8*0 = 300 <= 480
        # Revenue: 25*60 + 30*0 = 1500
        self.assertAlmostEqual(solution['Product_A'], 60.0, places=5)
        self.assertAlmostEqual(solution['Product_B'], 0.0, places=5)
        self.assertAlmostEqual(solution['Total_Revenue'], 1500.0, places=5)

    def test_only_product_b_optimal(self):
        """Test a scenario where only product B is optimal."""
        params = {
            'Price_Product_A': 10,
            'Price_Product_B': 50,  # Product B is much more profitable
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 5,  # B is very efficient on machine 1
            'Machine_1_Available_Hours': 300,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 10,  # B is less efficient on machine 2
            'Machine_2_Available_Hours': 600,
        }
        model = OptimizationModel(params)
        solution = model.solve()

        self.assertEqual(solution['status'], LpStatus[1])
        # Expected solution: (x_A, x_B) = (0, 60)
        # M1: 10*0 + 5*60 = 300 <= 300 (tight)
        # M2: 5*0 + 10*60 = 600 <= 600 (tight)
        # Revenue: 10*0 + 50*60 = 3000
        self.assertAlmostEqual(solution['Product_A'], 0.0, places=5)
        self.assertAlmostEqual(solution['Product_B'], 60.0, places=5)
        self.assertAlmostEqual(solution['Total_Revenue'], 3000.0, places=5)

    def test_zero_capacity(self):
        """Test with zero machine capacity."""
        params = {
            'Price_Product_A': 25,
            'Price_Product_B': 30,
            'Product_A_Production_Time_Machine_1': 10,
            'Product_B_Production_Time_Machine_1': 15,
            'Machine_1_Available_Hours': 0,
            'Product_A_Production_Time_Machine_2': 5,
            'Product_B_Production_Time_Machine_2': 8,
            'Machine_2_Available_Hours': 0,
        }
        model = OptimizationModel(params)
        solution = model.solve()

        # Should be optimal with 0 production
        self.assertEqual(solution['status'], LpStatus[1])
        self.assertAlmostEqual(solution['Product_A'], 0.0, places=5)
        self.assertAlmostEqual(solution['Product_B'], 0.0, places=5)
        self.assertAlmostEqual(solution['Total_Revenue'], 0.0, places=5)

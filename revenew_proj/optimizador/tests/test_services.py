from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from optimizador.services import (
    OptimizationSolution,
    ProductionOptimizationService,
    ProductionParameters,
)


VALID_PARAMS = {
    "Price_Product_A": 25,
    "Price_Product_B": 30,
    "Product_A_Production_Time_Machine_1": 10,
    "Product_B_Production_Time_Machine_1": 15,
    "Machine_1_Available_Hours": 600,
    "Product_A_Production_Time_Machine_2": 5,
    "Product_B_Production_Time_Machine_2": 8,
    "Machine_2_Available_Hours": 480,
}


class ProductionOptimizationServiceTest(SimpleTestCase):
    def test_service_returns_typed_solution_without_rendering_concerns(self):
        solution = ProductionOptimizationService().solve(VALID_PARAMS)

        self.assertIsInstance(solution, OptimizationSolution)
        self.assertEqual(solution.status, "Optimal")
        self.assertAlmostEqual(solution.product_a or 0, 60.0, places=5)
        self.assertAlmostEqual(solution.product_b or 0, 0.0, places=5)
        self.assertAlmostEqual(solution.total_revenue or 0, 1500.0, places=5)
        self.assertEqual(
            solution.as_legacy_dict(),
            {
                "status": "Optimal",
                "Product_A": solution.product_a,
                "Product_B": solution.product_b,
                "Total_Revenue": solution.total_revenue,
            },
        )

    def test_parameter_adapter_rejects_negative_values(self):
        params = dict(VALID_PARAMS)
        params["Price_Product_A"] = -1

        with self.assertRaises(ValidationError):
            ProductionParameters.from_mapping(params)

    def test_parameter_adapter_rejects_non_finite_values(self):
        for bad_value in ("nan", "inf", "-inf"):
            with self.subTest(bad_value=bad_value):
                params: dict[str, object] = dict(VALID_PARAMS)
                params["Price_Product_A"] = bad_value

                with self.assertRaises(ValidationError):
                    ProductionParameters.from_mapping(params)

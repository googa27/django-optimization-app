from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from django.core.exceptions import ValidationError
from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, PULP_CBC_CMD, value


REQUIRED_PARAMETERS = (
    "Price_Product_A",
    "Price_Product_B",
    "Product_A_Production_Time_Machine_1",
    "Product_B_Production_Time_Machine_1",
    "Machine_1_Available_Hours",
    "Product_A_Production_Time_Machine_2",
    "Product_B_Production_Time_Machine_2",
    "Machine_2_Available_Hours",
)


@dataclass(frozen=True)
class ProductionParameters:
    price_product_a: float
    price_product_b: float
    product_a_time_machine_1: float
    product_b_time_machine_1: float
    machine_1_available_hours: float
    product_a_time_machine_2: float
    product_b_time_machine_2: float
    machine_2_available_hours: float

    @classmethod
    def from_mapping(cls, params: Mapping[str, object]) -> "ProductionParameters":
        missing = [name for name in REQUIRED_PARAMETERS if name not in params]
        if missing:
            raise ValidationError(f"Missing optimization parameters: {missing}")
        try:
            values = {name: float(params[name]) for name in REQUIRED_PARAMETERS}
        except (TypeError, ValueError) as exc:
            raise ValidationError("Optimization parameters must be numeric.") from exc
        if any(not math.isfinite(value) for value in values.values()):
            raise ValidationError("Optimization parameters must be finite numbers.")
        if any(value < 0 for value in values.values()):
            raise ValidationError("Optimization parameters must be non-negative.")
        return cls(
            price_product_a=values["Price_Product_A"],
            price_product_b=values["Price_Product_B"],
            product_a_time_machine_1=values["Product_A_Production_Time_Machine_1"],
            product_b_time_machine_1=values["Product_B_Production_Time_Machine_1"],
            machine_1_available_hours=values["Machine_1_Available_Hours"],
            product_a_time_machine_2=values["Product_A_Production_Time_Machine_2"],
            product_b_time_machine_2=values["Product_B_Production_Time_Machine_2"],
            machine_2_available_hours=values["Machine_2_Available_Hours"],
        )

    def as_legacy_dict(self) -> dict[str, float]:
        return {
            "Price_Product_A": self.price_product_a,
            "Price_Product_B": self.price_product_b,
            "Product_A_Production_Time_Machine_1": self.product_a_time_machine_1,
            "Product_B_Production_Time_Machine_1": self.product_b_time_machine_1,
            "Machine_1_Available_Hours": self.machine_1_available_hours,
            "Product_A_Production_Time_Machine_2": self.product_a_time_machine_2,
            "Product_B_Production_Time_Machine_2": self.product_b_time_machine_2,
            "Machine_2_Available_Hours": self.machine_2_available_hours,
        }


@dataclass(frozen=True)
class OptimizationSolution:
    status: str
    product_a: float | None
    product_b: float | None
    total_revenue: float | None

    def as_legacy_dict(self) -> dict[str, float | str | None]:
        return {
            "status": self.status,
            "Product_A": self.product_a,
            "Product_B": self.product_b,
            "Total_Revenue": self.total_revenue,
        }


class ProductionOptimizationService:
    """Pure optimization boundary; no Django request, persistence, or rendering code."""

    def solve(self, params: ProductionParameters | Mapping[str, object]) -> OptimizationSolution:
        if not isinstance(params, ProductionParameters):
            params = ProductionParameters.from_mapping(params)

        problem = LpProblem("Production_Optimization", LpMaximize)
        product_a = LpVariable("Product_A", lowBound=0)
        product_b = LpVariable("Product_B", lowBound=0)

        problem += (
            params.price_product_a * product_a + params.price_product_b * product_b,
            "Total_Revenue",
        )
        problem += (
            params.product_a_time_machine_1 * product_a
            + params.product_b_time_machine_1 * product_b
            <= params.machine_1_available_hours,
            "Machine_1_Constraint",
        )
        problem += (
            params.product_a_time_machine_2 * product_a
            + params.product_b_time_machine_2 * product_b
            <= params.machine_2_available_hours,
            "Machine_2_Constraint",
        )

        status_code = problem.solve(PULP_CBC_CMD(msg=False))
        status = LpStatus[status_code]
        if status != "Optimal":
            return OptimizationSolution(
                status=status,
                product_a=None,
                product_b=None,
                total_revenue=None,
            )
        return OptimizationSolution(
            status=status,
            product_a=value(product_a),
            product_b=value(product_b),
            total_revenue=value(problem.objective),
        )

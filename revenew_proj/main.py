import sys

from django.core.exceptions import ValidationError

from optimizador.dataloader import DataLoader
from optimizador.results import ResultsHandler
from optimizador.services import ProductionOptimizationService, ProductionParameters


def run_optimization(csv_path: str) -> int:
    """Run the demo optimizer from a CSV file and return a process status code."""
    try:
        with open(csv_path, "rb") as file_obj:
            params = ProductionParameters.from_mapping(DataLoader(file_obj).load())
        solution = ProductionOptimizationService().solve(params)
        result = ResultsHandler(solution, params).format()
    except (OSError, ValidationError, ValueError) as exc:
        print("Error:", str(exc), file=sys.stderr)
        return 1

    if result.get("error"):
        print("Error:", result["error"], file=sys.stderr)
        return 1

    print("Optimization status:", result["status"])
    print(f"Product A: {result['Product_A']}")
    print(f"Product B: {result['Product_B']}")
    print(f"Total Revenue: ${result['Total_Revenue']:.2f}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <csv_file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(run_optimization(sys.argv[1]))

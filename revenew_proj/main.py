import sys

# Import from the app
from optimizador.dataloader import DataLoader
from optimizador.optimizer import OptimizationModel
from optimizador.results import ResultsHandler


def run_optimization(csv_path):
    """
    Command-line interface for solving the optimization problem from a CSV file.

    Usage:
        python main.py optimization_problem_data.csv
    Args:
        csv_path (str): Path to the CSV file containing production parameters.
    """

    try:
        # Open file for reading
        with open(csv_path, 'rb') as f:
            # STEP 1: Load data
            loader = DataLoader(f)
            params = loader.load()

            # STEP 2: Solve optimization
            model = OptimizationModel(params)
            solution = model.solve()

            # STEP 3: Format result
            formatter = ResultsHandler(solution)
            result = formatter.format()

            # Print to console
            if result.get("error"):
                print("❌", result["error"])
            else:
                print("Optimization status:", result["status"])
                print(f"Product A: {result['Product_A']}")
                print(f"Product B: {result['Product_B']}")
                print(f"Total Revenue: ${result['Total_Revenue']:.2f}")

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <csv_file>")
    else:
        run_optimization(sys.argv[1])

import matplotlib as mpl
import matplotlib.pyplot as plt


class ResultsHandler:
    def __init__(self, solution: dict):
        self.solution = solution

    def format(self):
        # Check if solution is feasible/optimal
        if self.solution["status"] != "Optimal":
            return {
                "status": self.solution["status"],
                "error": "The optimization problem did not return an optimal solution.",
                "Product_A": None,
                "Product_B": None,
                "Total_Revenue": None
            }

        # Round results for cleaner display
        return {
            "status": self.solution["status"],
            "Product_A": round(self.solution["Product_A"], 2),
            "Product_B": round(self.solution["Product_B"], 2),
            "Total_Revenue": round(self.solution["Total_Revenue"], 2)
        }

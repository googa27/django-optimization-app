from io import BytesIO
import base64
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')  # Use 'Agg' backend for non-GUI environments


class ResultsHandler:
    '''
    Handles the formatting of optimization results for display.
    This class takes the solution dictionary from the optimization model and formats it for easier interpretation and display in the web application.
    Attributes:
        solution (dict): The solution dictionary containing the optimization results.
    '''

    def __init__(self, solution: dict):
        self.solution = solution

    def format(self):
        '''
        Formats the optimization results for display.
        Returns:
            dict: A dictionary containing the formatted results, including:
                - status: The status of the optimization (e.g., "Optimal", "Infeasible").
                - Product_A: The optimal quantity of Product A to produce.
                - Product_B: The optimal quantity of Product B to produce.
                - Total_Revenue: The total revenue from the optimal production plan.
        '''
        if self.solution["status"] != "Optimal":
            return {
                "status": self.solution["status"],
                "error": "The optimization problem did not return an optimal solution.",
                "Product_A": None,
                "Product_B": None,
                "Total_Revenue": None,
                "plot": None
            }

        result = {
            "status": self.solution["status"],
            "Product_A": round(self.solution["Product_A"], 2),
            "Product_B": round(self.solution["Product_B"], 2),
            "Total_Revenue": round(self.solution["Total_Revenue"], 2),
        }

        # Add a bar plot (as base64 string)
        result["plot"] = self.generate_plot(result)

        return result

    def generate_plot(self, result: dict) -> str:
        '''
        Generates a bar plot of the optimization results and returns it as a base64-encoded string.
        Args:
            result (dict): The optimization result dictionary containing keys "Product_A", "Product_B", and "Total_Revenue".
        Returns:
            str: A base64-encoded string representing the bar plot image.
        '''
        # Prepare data
        labels = ["Product A", "Product B"]
        values = [result["Product_A"],
                  result["Product_B"]]

        # Create plot
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=["steelblue", "salmon"])
        ax.set_title("Optimization Result")
        ax.set_ylabel("Quantity")

        # Save to memory
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)

        # Encode to base64
        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

# class ResultsHandler:
#     '''
#     Handles the formatting of optimization results for display.
#     This class takes the solution dictionary from the optimization model and formats it
#     for easier interpretation and display in the web application.
#     Attributes:
#         solution (dict): The solution dictionary containing the optimization results.
#     '''

#     def __init__(self, solution: dict):
#         '''
#         Initializes the ResultsHandler with the optimization solution.
#         Args:
#             solution (dict): A dictionary containing the optimization results, expected to have keys
#                              like "status", "Product_A", "Product_B", and "Total_Revenue".
#         '''
#         self.solution = solution

#     def format(self):
#         '''
#         Formats the optimization results for display.
#         Returns:
#             dict: A dictionary containing the formatted results, including:
#                 - status: The status of the optimization (e.g., "Optimal", "Infeasible").
#                 - Product_A: The optimal quantity of Product A to produce.
#                 - Product_B: The optimal quantity of Product B to produce.
#                 - Total_Revenue: The total revenue from the optimal production plan.
#         '''
#         # Check if solution is feasible/optimal
#         if self.solution["status"] != "Optimal":
#             return {
#                 "status": self.solution["status"],
#                 "error": "The optimization problem did not return an optimal solution.",
#                 "Product_A": None,
#                 "Product_B": None,
#                 "Total_Revenue": None
#             }

#         # Round results for cleaner display
#         return {
#             "status": self.solution["status"],
#             "Product_A": round(self.solution["Product_A"], 2),
#             "Product_B": round(self.solution["Product_B"], 2),
#             "Total_Revenue": round(self.solution["Total_Revenue"], 2)
#         }

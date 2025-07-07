from io import BytesIO
import base64
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np  # Import numpy for numerical operations
mpl.use('Agg')  # Use 'Agg' backend for non-GUI environments


class ResultsHandler:
    '''
    Handles the formatting of optimization results for display.
    This class takes the solution dictionary from the optimization model and formats it for easier interpretation and display in the web application.
    Attributes:
        solution (dict): The solution dictionary containing the optimization results.
        params (dict): The original parameters used for the optimization.
    '''

    def __init__(self, solution: dict, params: dict):
        self.solution = solution
        self.params = params

    def format(self):
        '''
        Formats the optimization results for display.
        Returns:
            dict: A dictionary containing the formatted results, including:
                - status: The status of the optimization (e.g., "Optimal", "Infeasible").
                - Product_A: The optimal quantity of Product A to produce.
                - Product_B: The optimal quantity of Product B to produce.
                - Total_Revenue: The total revenue from the optimal production plan.
                - plot: Base64 string of the bar plot for production quantities.
                - feasible_region_plot: Base64 string of the plot showing constraints and feasible region.
        '''
        if self.solution["status"] != "Optimal":
            return {
                "status": self.solution["status"],
                "error": "The optimization problem did not return an optimal solution.",
                "Product_A": None,
                "Product_B": None,
                "Total_Revenue": None,
                "plot": None,
                "feasible_region_plot": None  # Add this for consistency
            }

        result = {
            "status": self.solution["status"],
            "Product_A": round(self.solution["Product_A"], 2),
            "Product_B": round(self.solution["Product_B"], 2),
            "Total_Revenue": round(self.solution["Total_Revenue"], 2),
        }

        # Add a bar plot (as base64 string)
        result["plot"] = self.generate_plot(result)
        # Add the feasible region plot (as base64 string)
        result["feasible_region_plot"] = self.generate_feasible_region_plot(
            self.params, self.solution)

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
        # Adjusted for better web display
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, values, color=["steelblue", "salmon"])
        ax.set_title("Optimal Production Quantities")
        ax.set_ylabel("Quantity (Units)")
        ax.set_ylim(bottom=0)  # Ensure y-axis starts at 0

        # Save to memory
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close(fig)  # Close the figure to free memory
        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{plot_base64}"

    def generate_feasible_region_plot(self, params: dict, solution: dict) -> str:
        '''
        Generates a plot showing the constraint lines, feasible region, and optimal solution.
        Args:
            params (dict): The original parameters for the optimization problem.
            solution (dict): The solution dictionary from the optimizer.
        Returns:
            str: A base64-encoded string representing the plot image.
        '''
        fig, ax = plt.subplots(
            figsize=(8, 6))  # Adjusted for better web display

        # Extract parameters
        pa1 = params["Product_A_Production_Time_Machine_1"]
        pb1 = params["Product_B_Production_Time_Machine_1"]
        cap1 = params["Machine_1_Available_Hours"]
        pa2 = params["Product_A_Production_Time_Machine_2"]
        pb2 = params["Product_B_Production_Time_Machine_2"]
        cap2 = params["Machine_2_Available_Hours"]

        # Optimal solution points
        xA_opt = solution["Product_A"]
        xB_opt = solution["Product_B"]

        # Determine axis limits based on intercepts and optimal solution
        x_intercept_m1 = cap1 / pa1 if pa1 > 0 else np.inf
        y_intercept_m1 = cap1 / pb1 if pb1 > 0 else np.inf
        x_intercept_m2 = cap2 / pa2 if pa2 > 0 else np.inf
        y_intercept_m2 = cap2 / pb2 if pb2 > 0 else np.inf

        # Max axis limit should comfortably contain all intercepts and optimal point
        max_x = max(x_intercept_m1, x_intercept_m2, xA_opt, 10) * 1.2
        max_y = max(y_intercept_m1, y_intercept_m2, xB_opt, 10) * 1.2

        x = np.linspace(0, max_x, 500)

        # Constraint 1: pa1*xA + pb1*xB <= cap1
        # xB = (cap1 - pa1*xA) / pb1
        y1 = (cap1 - pa1 * x) / pb1
        y1[y1 < 0] = np.nan  # Set negative y values to NaN so they don't plot

        # Constraint 2: pa2*xA + pb2*xB <= cap2
        # xB = (cap2 - pa2*xA) / pb2
        y2 = (cap2 - pa2 * x) / pb2
        y2[y2 < 0] = np.nan  # Set negative y values to NaN

        # Plot constraint lines
        ax.plot(
            x, y1, label=f'Machine 1: {pa1}xA + {pb1}xB <= {cap1}', color='red', linestyle='--')
        ax.plot(
            x, y2, label=f'Machine 2: {pa2}xA + {pb2}xB <= {cap2}', color='green', linestyle='--')

        # Shade the feasible region
        # The feasible region is the area where all constraints are met.
        # For <= constraints, it's below the lines and above x=0, y=0.
        # We fill the area between 0 and the minimum of y1 and y2.
        y_feasible = np.minimum(y1, y2)
        ax.fill_between(x, 0, y_feasible, where=(y_feasible >= 0),
                        color='blue', alpha=0.1, label='Feasible Region')

        # Plot the optimal solution point
        ax.plot(xA_opt, xB_opt, 'o', color='gold', markersize=10,
                label=f'Optimum: A={xA_opt:.2f}, B={xB_opt:.2f}', markeredgecolor='black')

        ax.set_xlabel('Units of Product A (xA)')
        ax.set_ylabel('Units of Product B (xB)')
        ax.set_title(
            'Feasible Region and Optimal Solution  for Production Optimization')
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()

        # Save to memory
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close(fig)  # Close the figure to free memory
        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{plot_base64}"

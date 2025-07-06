from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpStatus, value


class OptimizationModel:
    """A class to model and solve a production optimization problem using linear programming."""

    def __init__(self, params: dict):
        """Initializes the optimization model with parameters.
        Args:
            params (dict): A dictionary containing the parameters for the optimization problem.
                Expected keys include:
                - 'Price_Product_A'
                - 'Price_Product_B'
                - 'Product_A_Production_Time_Machine_1'
                - 'Product_B_Production_Time_Machine_1'
                - 'Machine_1_Available_Hours'
                - 'Product_A_Production_Time_Machine_2' (optional)
                - 'Product_B_Production_Time_Machine_2' (optional)
                - 'Machine_2_Available_Hours' (optional)
        """
        self.params = params

    def solve(self) -> dict:
        """Solves the production optimization problem using linear programming."""
        # Create the problem
        prob = LpProblem("Production_Optimization", LpMaximize)

        # Decision variables
        # Ensure that the decision variables are non-negative
        x_A = LpVariable("Product_A", lowBound=0)
        x_B = LpVariable("Product_B", lowBound=0)

        # Objective function
        price_A = self.params["Price_Product_A"]
        price_B = self.params["Price_Product_B"]
        prob += price_A * x_A + price_B * x_B, "Total_Revenue"

        # Machine 1 constraint
        a1 = self.params["Product_A_Production_Time_Machine_1"]
        b1 = self.params["Product_B_Production_Time_Machine_1"]
        cap1 = self.params["Machine_1_Available_Hours"]
        prob += a1 * x_A + b1 * x_B <= cap1, "Machine_1_Constraint"

        # Optional: Add Machine 2 constraints if available
        # if all(k in self.params for k in [
        #     "Product_A_Production_Time_Machine_2",
        #     "Product_B_Production_Time_Machine_2",
        #     "Machine_2_Available_Hours"
        # ]):
        a2 = self.params["Product_A_Production_Time_Machine_2"]
        b2 = self.params["Product_B_Production_Time_Machine_2"]
        cap2 = self.params["Machine_2_Available_Hours"]
        prob += a2 * x_A + b2 * x_B <= cap2, "Machine_2_Constraint"

        # Solve the problem
        status = prob.solve()

        # Return solution
        return {
            "status": LpStatus[status],
            "Product_A": x_A.varValue,
            "Product_B": x_B.varValue,
            "Total_Revenue": value(prob.objective)
        }

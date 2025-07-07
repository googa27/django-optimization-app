# Revenew Optimization App

This project solves a simple production optimization problem using linear programming, based on user-uploaded CSV data. It includes:

- A Django web interface for uploading data and viewing results.
- A command-line interface (`main.py`) to run the optimization directly from a CSV file.

---

## 🧰 Tech Stack

- Python 3.10
- Django 4.x
- PuLP (for solving LP)
- Bootstrap (styling)

---

## 🚀 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd <project-folder>

# Create and activate virtual environment
python -m venv rvn_venv
rvn_venv\Scripts\activate  # Windows
# or
source rvn_venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

---

# 🖥️ Run the web app
```bash
python manage.py runserver
```
Then open your browser and go to:

http://127.0.0.1:8000/optimizador/

You can now:

- Upload a CSV file (see example format in optimization_problem_data.csv)

- View the optimal production quantities and total revenue

---

# 🧪 Run Tests
To execute the unit and integration tests for the application, use Django's built-in test runner:

```Bash
python manage.py test optimizador
```

This command will run all tests located within the optimizador app, ensuring the correctness of the data loading, optimization model, and view logic.

---

# 🧪 Run from the command line (no web)

```bash
python main.py optimization_problem_data.csv
```

```yaml
Optimization status: Optimal
Product A: 4.0
Product B: 2.0
Total Revenue: $560.00
```
---

---

# ✅ CSV Format Example

| Product_A_Production_Time_Machine_1 | Product_B_Production_Time_Machine_1 | Machine_1_Available_Hours | Product_A_Production_Time_Machine_2 | Product_B_Production_Time_Machine_2 | Machine_2_Available_Hours | Price_Product_A | Price_Product_B |
|-------------------------------------|-------------------------------------|----------------------------|-------------------------------------|-------------------------------------|----------------------------|------------------|------------------|
| 1.5                                 | 1.0                                 | 8                          | 2.0                                 | 1.5                                 | 10                         | 100              | 80               |

Make sure that:
- All columns are present
- All values are numeric
- There are no negative values
- The input contains only one row
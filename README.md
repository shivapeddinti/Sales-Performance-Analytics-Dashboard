# CodeNova Task 3 – Interactive Analytics Dashboard

## Files
- `app.py` – Streamlit dashboard application
- `requirements.txt` – Python packages

## Dataset
Use the Task 1 dataset: `Copy of codenova_sales_sample.csv`.

The dashboard expects these columns:
`Order_ID, Order_Date, Product, Category, Region, Sales_Channel, Customer_Type, Quantity, Unit_Price_INR, Unit_Cost_INR, Discount_Percent, Payment_Method`

## Run on Windows 11

1. Install Python 3.10 or later from https://www.python.org/downloads/ and select **Add Python to PATH** during installation.
2. Extract this ZIP file.
3. Copy `Copy of codenova_sales_sample.csv` into the same folder as `app.py`.
4. Open Command Prompt in this folder.
5. Run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

6. The dashboard opens in your browser, usually at `http://localhost:8501`.
7. If the CSV is not in the folder, upload it using the dashboard's left sidebar.

## Calculations
- Gross Sales = Quantity × Unit Price
- Discount Amount = Gross Sales × Discount Percent
- Net Sales = Gross Sales − Discount Amount
- Total Cost = Quantity × Unit Cost
- Profit = Net Sales − Total Cost

The dashboard supports date, category, region, product, sales channel, and customer type filters.

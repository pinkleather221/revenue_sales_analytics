# Revenue Sales Analytics

This project analyzes the September 2026 electronics sales CSV in
`data/electronics_sales.csv`. The command-line program is
[`sales_analysis.py`](./sales_analysis.py); it produces a readable sales report
and checks its main calculations against pandas.

## Approach

The script loads the CSV with Python's standard-library `csv` module and keeps
each input row as a dictionary. It parses the quantity and unit-price fields,
skips rows with invalid required numbers, and calculates each valid
transaction's revenue as:

```text
revenue = quantity * unit price
```

It then calculates total revenue, revenue by product, the three highest-revenue
products, transactions worth at least KES 50,000, and mean, median, minimum,
and maximum transaction revenue. The script writes the report to
`output/sales_report.txt`, prints it, and uses pandas to independently
recalculate and compare total revenue, product totals, top products, and
statistics.

## Requirements and running the script

Use Python 3.14 or newer and install the dependencies from the project folder.
In PowerShell:

```powershell
cd C:\path\to\revenue_sales_analytics
uv sync
uv run python sales_analysis.py
```

Replace `C:\path\to\revenue_sales_analytics` with the actual project folder.
If Python and pandas are already installed in the active environment, you can
run the script directly from the project folder:

```powershell
python sales_analysis.py
```

The script searches the current directory and its parent directories for
`data/electronics_sales.csv`. It writes or replaces
`output/sales_report.txt` in the directory where it finds the project data.
The pandas verification requires pandas to be installed; `uv sync` installs
the dependency declared by this project.

## Numeric cleaning rules

The same `parse_number` function is used for quantity and unit-price input:

1. A missing value (`None`) is invalid.
2. Leading and trailing whitespace is removed and the text is converted to
   uppercase.
3. Every `KES` substring and every comma is removed. This accepts values such
   as `KES 18,999` and treats commas as thousands separators.
4. An empty string or any of `N/A`, `NONE`, `NULL`, and `-` is invalid.
5. The remaining text must be accepted by Python's `float` conversion and
   produce a finite number. Nonnumeric text such as `two`, malformed numbers,
   `NaN`, and positive or negative infinity are invalid.
6. After parsing, quantity and unit price must each be greater than zero.
   Zero or negative values make the row invalid.

If quantity is missing, unparseable, zero, or negative, the row is skipped with
the reason `invalid quantity`. Otherwise, an invalid, zero, or negative unit
price causes it to be skipped with the reason `invalid unit price`. If both
fields are invalid, the quantity reason is reported first. Invalid rows are
not included in any calculations; the script lists their sale IDs and reasons.
Valid rows retain their original columns and receive parsed numeric
`quantity`, `unit_price`, and calculated `revenue` values. Any revenue column
in the input is not used.

## Assumptions

- The input is a CSV with a header row and quantity plus unit-price columns.
  The script recognizes `quantity` or `qty`, and `unit_price`,
  `unit_price_kes`, `unit price`, or `price`.
- A period is the decimal separator, and commas are thousands separators.
  The parser does not interpret locale-specific number formats.
- Word-form numbers such as `two` are rejected rather than translated.
- Revenue is calculated from quantity and unit price; no tax, discounts,
  returns, shipping, or other adjustments are applied.
- Product ranking is by descending revenue; equal totals are ordered
  alphabetically by product name (case-insensitive). The top-N function
  defaults to three.
- The high-value threshold is inclusive: a transaction of exactly KES 50,000
  is included.
- Statistics are calculated over valid transactions only. Empty input to a
  statistics helper raises `ValueError`, and the script stops with an explicit
  error if the CSV contains no valid rows.

For the supplied data, the script reads 50 rows, uses 46, and skips four:
S-3006 and S-3035 have invalid quantities; S-3030 and S-3039 have invalid unit
prices. The formatted price in S-3029 is accepted. Expected total revenue is
KES 1,310,812.00.

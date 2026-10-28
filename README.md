# Revenue Sales Analytics

Analyze the September 2026 electronics sales export with the notebook in
[`sales_analysis.ipynb`](./sales_analysis.ipynb). The workflow uses Python's
standard library for loading, cleaning, and calculating the report, then uses
pandas to independently verify the results.

## Run

To generate the text report from the command line:

```bash
python starter.py
```

This writes `output/sales_report.txt` and prints the report plus pandas
verification results. The checks use the same cleaning rules as the custom
calculations.

To explore the analysis interactively:

1. Open `sales_analysis.ipynb` in VS Code or Jupyter from this project folder.
2. Select a Python kernel with the project dependencies installed (`uv sync`
   installs the dependencies declared in `pyproject.toml`).
3. Choose **Restart Kernel and Run All**. Running from a fresh kernel ensures
   each section has the variables created by the cells before it.

The notebook searches the current working directory and its parent folders
for `data/electronics_sales.csv`, then prints a report and a pandas verification
summary. Its calculations do not write or overwrite `output/sales_report.txt`.

## Data cleaning

- Commas and a leading `KES` marker are removed from numeric values before
  conversion, so a formatted price such as `KES 18,999` is accepted.
- Blank values, `N/A`, and nonnumeric values such as the quantity `two` are
  rejected. Quantities and unit prices must also be greater than zero.
- Rows with invalid quantities or prices are excluded and reported with their
  sale ID and reason. Valid rows include numeric quantity, unit price, and
  revenue (`quantity * unit price`).
- The pandas verification uses the same parser and positive-value rules as the
  standard-library pipeline to prevent mismatched row retention.

For the supplied CSV, 46 of 50 rows are used and four are skipped: S-3006 and
S-3035 have invalid quantities, while S-3030 and S-3039 have invalid prices.
The formatted price in S-3029 is repaired, and cleaned total revenue is
KES 1,310,812.00.

## Calculations

Revenue is grouped by product, store, and payment method. Product rankings sort
by revenue descending, with names alphabetically as a deterministic
tie-breaker. High-value transactions meet or exceed KES 50,000. Mean, median,
minimum, and maximum are calculated from valid transaction revenue; the custom
statistic functions raise `ValueError` for an empty input.

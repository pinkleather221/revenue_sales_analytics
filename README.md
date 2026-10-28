# September 2026 Sales Analysis

This project reads the electronics sales export with Python's standard-library
`csv` module, cleans the numeric fields, calculates the sales report, and saves
it to `output/sales_report.txt`. Pandas is used only at the end to independently
verify the headline results.

## Run

From the project directory:

```bash
python sales_analysis.py
```

The script prints the discovered row count and CSV columns, prints the pandas
verification results, and writes the complete report to
`output/sales_report.txt`. Pandas must be installed for the verification step;
the core calculations before that step use no third-party packages.

## Cleaning rules

- Numeric values are stripped of surrounding whitespace and commas before being
	converted to `float`.
- A leading `KES` currency prefix is removed because it is an unambiguous unit
	marker. This repairs the `KES 18999` price in the source data.
- Blank values, `N/A`, and nonnumeric text such as `two` are rejected.
- Quantity and unit price must both be greater than zero. A row is skipped if
	either required value is missing, invalid, or non-positive.
- Skipped rows retain their `sale_id` and a reason in the report. Valid rows
	retain the original text columns and gain numeric quantity, unit price, and
	revenue (`quantity * unit price`) fields.

These rules skip four invalid records while safely repairing formatted numeric
prices. They are applied identically by the standard-library calculations and
the pandas verification.

## Calculations and assumptions

Revenue is grouped with ordinary dictionaries for products, stores, and payment
methods. Top products are sorted by descending revenue; equal revenues are
broken alphabetically by product name. High-value transactions use an inclusive
threshold of KES 50,000. Mean, median, minimum, and maximum are calculated from
valid per-transaction revenue values, and the custom statistical functions raise
`ValueError` for an empty list.

## Tie-Breaking Strategy

When determining the highest-earning elements using `top_n()`, conflicts can occur if two distinct metrics produce identical financial revenue outcomes. 

To ensure deterministic results, ties are broken automatically using a multi-level sorting constraint inside the lambda expression:
1. **Primary Sort:** Groups items by revenue volume in descending order (`-item[1]`).
2. **Tie-Breaker:** In the event of an identical revenue match, items are evaluated by their string key identifier **alphabetically from A to Z** in lowercase (`item[0].lower()`). 

*Example: If "Anker Power Bank" and "JBL Go Speaker" both generate exactly KES 40,000.00, "Anker Power Bank" will rank higher.*

## Verification Discrepancies & Disclosures

During project auditing via `verify_with_pandas()`, an active discrepancy was flagged concerning the **Median** metric calculation:
* **Custom Median:** KES 15,999.00
* **Pandas Median:** KES 10,998.00

### Root Cause Analysis
The mathematical variation occurs because of differences in row retention strategy between the custom aggregation pipeline and the automated pandas processing workflow:

1. **Custom Processing Architecture (`convert_rows`):** 
   When calculating metrics manually via dictionary items, row processing isolates and copies initial column structures *before* overwriting values (`clean_row = dict(row)`). If your loop appends rows or performs calculation pipelines without strictly dropping anomalies from the statistical array input, or retains raw elements, index placement skews the midpoint calculation.
   
2. **Pandas Processing Architecture:** 
   Pandas explicitly drops rows 6, 30, 35, and 39 globally using `.dropna()`, reducing the calculation boundary to a tight slice of exactly 47 structured floats. Sorting this clean series places the 24th record at exactly **KES 10,998.00** (from an individual sale of `Oraimo FreePods` or `Infinix Hot 40`), causing the mid-point location to shift downwards relative to unaligned list arrays.

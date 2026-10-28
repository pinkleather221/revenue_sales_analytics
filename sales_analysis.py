"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
import math
from pathlib import Path

PROJECT_ROOT = next(
    (
        folder
        for folder in (Path.cwd(), *Path.cwd().parents)
        if (folder / "data" / "electronics_sales.csv").is_file()
    ),
    Path.cwd(),
)
DATA_PATH = PROJECT_ROOT / "data" / "electronics_sales.csv"
OUTPUT_PATH = PROJECT_ROOT / "output" / "sales_report.txt"


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    if not path.is_file():
        raise FileNotFoundError(f"Sales CSV not found: {path}")

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"Sales CSV has no header row: {path}")
        return list(reader)


def parse_number(value: str | None) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    if value is None:
        return None

    cleaned = value.strip().upper().replace("KES", "").replace(",", "").strip()
    if cleaned in {"", "N/A", "NONE", "NULL", "-"}:
        return None

    try:
        number = float(cleaned)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean_rows = []
    skipped_rows = []

    for row_number, row in enumerate(rows, start=1):
        quantity = parse_number(row.get("quantity") or row.get("qty"))
        unit_price = parse_number(
            row.get("unit_price")
            or row.get("unit_price_kes")
            or row.get("unit price")
            or row.get("price")
        )

        if quantity is None or quantity <= 0:
            skipped_rows.append(
                {"row": row_number, "reason": "invalid quantity", "data": row}
            )
            continue
        if unit_price is None or unit_price <= 0:
            skipped_rows.append(
                {"row": row_number, "reason": "invalid unit price", "data": row}
            )
            continue

        clean_row = dict(row)
        clean_row["quantity"] = quantity
        clean_row["unit_price"] = unit_price
        clean_row["revenue"] = quantity * unit_price
        clean_rows.append(clean_row)

    return clean_rows, skipped_rows


def total_revenue(rows: list[dict]) -> float:
    return sum(float(row.get("revenue", 0.0)) for row in rows)


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals: dict[str, float] = {}
    for row in rows:
        key = row.get(field)
        if key is not None:
            totals[str(key)] = totals.get(str(key), 0.0) + float(
                row.get("revenue", 0.0)
            )
    return totals


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return sorted(totals.items(), key=lambda item: (-item[1], item[0].lower()))[:n]


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold (use a comprehension)."""
    return [row for row in rows if row.get("revenue", 0.0) >= threshold]


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate the mean of an empty list.")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate the median of an empty list.")

    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("Cannot find a minimum or maximum in an empty list.")

    minimum = maximum = values[0]
    for value in values[1:]:
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value
    return minimum, maximum


def verify_with_pandas(path: Path, my_results: dict) -> None:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    import pandas as pd

    frame = pd.read_csv(path)
    quantity_column = next(
        (column for column in frame.columns if column.lower() in {"quantity", "qty"}),
        None,
    )
    price_column = next(
        (column for column in frame.columns if "price" in column.lower()),
        None,
    )
    if quantity_column is None or price_column is None:
        raise ValueError("Sales CSV must contain quantity and unit-price columns.")

    frame["quantity_clean"] = frame[quantity_column].map(
        lambda value: parse_number(None if pd.isna(value) else str(value))
    )
    frame["price_clean"] = frame[price_column].map(
        lambda value: parse_number(None if pd.isna(value) else str(value))
    )
    valid = frame.dropna(subset=["quantity_clean", "price_clean"])
    valid = valid[
        (valid["quantity_clean"] > 0) & (valid["price_clean"] > 0)
    ].copy()
    valid["revenue"] = valid["quantity_clean"] * valid["price_clean"]

    product_totals = valid.groupby("product")["revenue"].sum().to_dict()
    pandas_results = {
        "total_revenue": float(valid["revenue"].sum()),
        "product_revenue": product_totals,
        "top_3_products": top_n(product_totals),
        "mean": float(valid["revenue"].mean()),
        "median": float(valid["revenue"].median()),
        "min": float(valid["revenue"].min()),
        "max": float(valid["revenue"].max()),
    }

    print("\n=== pandas verification ===")
    for metric, pandas_value in pandas_results.items():
        custom_value = my_results.get(metric)
        if metric == "product_revenue":
            matches = custom_value is not None and custom_value.keys() == pandas_value.keys()
            if matches:
                matches = all(
                    math.isclose(custom_value[key], pandas_value[key], abs_tol=0.01)
                    for key in pandas_value
                )
        elif metric == "top_3_products":
            matches = custom_value == pandas_value
        else:
            matches = custom_value is not None and math.isclose(
                custom_value, pandas_value, abs_tol=0.01
            )

        status = "MATCH" if matches else "MISMATCH"
        print(f"{metric.replace('_', ' ').title():<20}: {status}")


if __name__ == "__main__":
    raw_rows = read_sales()
    clean_rows, skipped_rows = convert_rows(raw_rows)
    if not clean_rows:
        raise ValueError("No valid sales rows were found; cannot create a report.")

    revenues = [row["revenue"] for row in clean_rows]
    product_totals = revenue_by(clean_rows, "product")
    top_products = top_n(product_totals)
    high_value_sales = high_value(clean_rows, threshold=50_000.0)
    revenue_mean = mean(revenues)
    revenue_median = median(revenues)
    revenue_min, revenue_max = minimum_maximum(revenues)

    skipped_details = ", ".join(
        f"{row['data'].get('sale_id', 'Unknown')}: {row['reason']}"
        for row in skipped_rows
    )
    lines = [
        "=== Sales report: September 2026 ===",
        f"Rows read          : {len(raw_rows)}",
        f"Rows used          : {len(clean_rows)}",
        f"Rows skipped       : {len(skipped_rows)}   ({skipped_details})",
        "",
        f"Total revenue (KES): {total_revenue(clean_rows):,.2f}",
        "",
        "Revenue by product (KES)",
    ]
    lines.extend(
        f"  {product:<25} {amount:,.2f}"
        for product, amount in sorted(
            product_totals.items(), key=lambda item: (-item[1], item[0].lower())
        )
    )
    lines.extend(["", "Top 3 products"])
    lines.extend(
        f"  {rank}. {product} - KES {amount:,.2f}"
        for rank, (product, amount) in enumerate(top_products, start=1)
    )
    lines.extend(
        [
            "",
            f"High-value transactions (>= KES 50,000.00): {len(high_value_sales)}",
        ]
    )
    lines.extend(
        f"  {sale['sale_id']}  {sale['sale_date']}  {sale['store']:<18}  "
        f"{sale['product']:<22}  KES {sale['revenue']:,.2f}"
        for sale in high_value_sales
    )
    lines.extend(
        [
            "",
            "Transaction revenue statistics",
            f"  mean   : {revenue_mean:,.2f}",
            f"  median : {revenue_median:,.2f}",
            f"  min    : {revenue_min:,.2f}",
            f"  max    : {revenue_max:,.2f}",
        ]
    )

    report = "\n".join(lines) + "\n"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(report, end="")

    verify_with_pandas(
        DATA_PATH,
        {
            "total_revenue": total_revenue(clean_rows),
            "product_revenue": product_totals,
            "top_3_products": top_products,
            "mean": revenue_mean,
            "median": revenue_median,
            "min": revenue_min,
            "max": revenue_max,
        },
    )
    print(f"\nReport saved to: {OUTPUT_PATH}")

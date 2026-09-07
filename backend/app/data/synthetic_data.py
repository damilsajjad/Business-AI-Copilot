"""Deterministic synthetic retail/e-commerce dataset generator for testing and demos."""

import io
import random
from datetime import datetime, timedelta

import pandas as pd


def generate_retail_dataset(num_orders: int = 500, random_seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible realistic retail sales dataset."""
    random.seed(random_seed)

    products = [
        {"product_id": "PRD-001", "name": "Wireless Noise-Canceling Headphones", "category": "Electronics", "unit_price": 149.99},
        {"product_id": "PRD-002", "name": "Smart Fitness Watch", "category": "Electronics", "unit_price": 199.50},
        {"product_id": "PRD-003", "name": "Organic Cotton Crewneck T-Shirt", "category": "Apparel", "unit_price": 29.99},
        {"product_id": "PRD-004", "name": "Ergonomic Office Chair Cushion", "category": "Home & Office", "unit_price": 45.00},
        {"product_id": "PRD-005", "name": "Stainless Steel Thermal Water Bottle", "category": "Accessories", "unit_price": 24.99},
        {"product_id": "PRD-006", "name": "Mechanical Gaming Keyboard", "category": "Electronics", "unit_price": 89.95},
        {"product_id": "PRD-007", "name": "Ceramic Pour-Over Coffee Dripper", "category": "Kitchen", "unit_price": 34.50},
        {"product_id": "PRD-008", "name": "Waterproof Hiking Backpack 30L", "category": "Outdoors", "unit_price": 79.99},
    ]

    customers = [f"CUST-{i:04d}" for i in range(1, 65)]
    channels = ["Online Store", "Amazon Marketplace", "Direct Retail", "Wholesale Partner"]

    start_date = datetime(2024, 1, 1)
    records = []

    for order_idx in range(1, num_orders + 1):
        order_id = f"ORD-{order_idx:05d}"
        cust_id = random.choice(customers)

        # Time distribution over 365 days
        day_offset = int((order_idx / num_orders) * 360) + random.randint(0, 5)
        order_date = start_date + timedelta(days=day_offset)

        # Simulate seasonal drop in Q3 for one product
        product = random.choice(products)
        qty = random.choices([1, 2, 3, 4, 5], weights=[0.6, 0.25, 0.08, 0.05, 0.02])[0]
        discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20], weights=[0.5, 0.2, 0.15, 0.1, 0.05])[0]

        gross_amount = round(qty * product["unit_price"], 2)
        total_amount = round(gross_amount * (1 - discount), 2)

        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": cust_id,
            "product_id": product["product_id"],
            "product_name": product["name"],
            "category": product["category"],
            "quantity": qty,
            "unit_price": product["unit_price"],
            "discount_rate": discount,
            "total_revenue": total_amount,
            "sales_channel": random.choice(channels),
        })

    return pd.DataFrame(records)


def generate_retail_csv_bytes(num_orders: int = 500) -> bytes:
    """Generate CSV bytes for testing and upload verification."""
    df = generate_retail_dataset(num_orders=num_orders)
    return df.to_csv(index=False).encode("utf-8")


def generate_multi_sheet_xlsx_bytes(num_orders: int = 200) -> bytes:
    """Generate multi-sheet Excel workbook bytes with Sales and Product Catalog."""
    sales_df = generate_retail_dataset(num_orders=num_orders)
    products_df = sales_df[["product_id", "product_name", "category", "unit_price"]].drop_duplicates()

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        sales_df.to_excel(writer, sheet_name="Transactions", index=False)
        products_df.to_excel(writer, sheet_name="Products", index=False)

    return buf.getvalue()

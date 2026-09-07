"""Deterministic product and category analytics engine."""

import pandas as pd

from app.schemas.analytics import (
    CategoryBreakdownItem,
    ProductAnalytics,
    ProductPerformanceItem,
)


def calculate_product_analytics(df: pd.DataFrame) -> ProductAnalytics:
    """Analyze product rankings, category shares, and Pareto concentration."""
    if df.empty or "product_name" not in df.columns:
        return ProductAnalytics(
            top_products=[],
            bottom_products=[],
            category_breakdown=[],
            top_3_products_revenue_share_pct=0.0,
        )

    total_revenue = float(df["total_revenue"].sum())

    # 1. Product-level aggregation
    grouped_prod = df.groupby(["product_name"]).agg(
        product_id=("product_id", "first") if "product_id" in df.columns else ("product_name", "first"),
        category=("category", "first") if "category" in df.columns else ("product_name", lambda x: "General"),
        total_revenue=("total_revenue", "sum"),
        total_quantity=("quantity", "sum") if "quantity" in df.columns else ("total_revenue", "count"),
    ).reset_index()

    prod_items = []
    for _, row in grouped_prod.iterrows():
        rev = round(float(row["total_revenue"]), 2)
        qty = int(row["total_quantity"])
        share = round((rev / total_revenue * 100), 2) if total_revenue > 0 else 0.0
        avg_price = round(rev / qty, 2) if qty > 0 else 0.0

        prod_items.append(
            ProductPerformanceItem(
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                total_revenue=rev,
                total_quantity=qty,
                revenue_share_pct=share,
                average_unit_price=avg_price,
            )
        )

    sorted_by_rev = sorted(prod_items, key=lambda p: p.total_revenue, reverse=True)
    top_products = sorted_by_rev[:10]
    bottom_products = sorted(sorted_by_rev[-5:], key=lambda p: p.total_revenue) if len(sorted_by_rev) > 5 else []

    top_3_rev = sum(p.total_revenue for p in sorted_by_rev[:3])
    top_3_share = round((top_3_rev / total_revenue * 100), 2) if total_revenue > 0 else 0.0

    # 2. Category-level aggregation
    cat_items = []
    if "category" in df.columns:
        grouped_cat = df.groupby("category").agg(
            total_revenue=("total_revenue", "sum"),
            total_quantity=("quantity", "sum") if "quantity" in df.columns else ("total_revenue", "count"),
        ).reset_index()

        for _, row in grouped_cat.iterrows():
            rev = round(float(row["total_revenue"]), 2)
            qty = int(row["total_quantity"])
            share = round((rev / total_revenue * 100), 2) if total_revenue > 0 else 0.0
            cat_items.append(
                CategoryBreakdownItem(
                    category=str(row["category"]),
                    total_revenue=rev,
                    total_quantity=qty,
                    revenue_share_pct=share,
                )
            )
        cat_items.sort(key=lambda c: c.total_revenue, reverse=True)

    return ProductAnalytics(
        top_products=top_products,
        bottom_products=bottom_products,
        category_breakdown=cat_items,
        top_3_products_revenue_share_pct=top_3_share,
    )

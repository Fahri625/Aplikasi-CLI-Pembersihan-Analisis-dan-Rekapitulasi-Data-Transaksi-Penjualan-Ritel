"""Module analitik untuk pengelompokan dan rekapitulasi data penjualan."""


def summarize_by_category(transactions: list[dict]) -> dict[str, dict]:
    """Mengelompokkan dan merekapitulasi metrik penjualan per kategori produk.

    Args:
        transactions: List transaksi yang sudah bersih.

    Returns:
        Dictionary dengan key nama kategori dan value berupa statistik ringkas.
    """
    grouped: dict[str, dict] = {}

    for row in transactions:
        category = row["Product Category"]
        if category not in grouped:
            grouped[category] = {
                "transaction_count": 0,
                "total_quantity": 0,
                "total_revenue": 0.0,
            }

        grouped[category]["transaction_count"] += 1
        grouped[category]["total_quantity"] += row["Quantity"]
        grouped[category]["total_revenue"] += row["Total Amount"]

    for stats in grouped.values():
        count = stats["transaction_count"]
        stats["average_amount"] = round(stats["total_revenue"] / count, 2) if count else 0.0
        stats["total_revenue"] = round(stats["total_revenue"], 2)

    return grouped


def summarize_by_gender(transactions: list[dict]) -> dict[str, dict]:
    """Mengelompokkan total transaksi dan pendapatan berdasarkan gender pelanggan.

    Args:
        transactions: List transaksi yang sudah bersih.

    Returns:
        Dictionary statistik per gender.
    """
    grouped: dict[str, dict] = {}

    for row in transactions:
        gender = row["Gender"]
        if gender not in grouped:
            grouped[gender] = {"transaction_count": 0, "total_revenue": 0.0}

        grouped[gender]["transaction_count"] += 1
        grouped[gender]["total_revenue"] += row["Total Amount"]

    for stats in grouped.values():
        stats["total_revenue"] = round(stats["total_revenue"], 2)

    return grouped


def compute_overall_metrics(
    transactions: list[dict],
    invalid_count: int = 0,
    duplicate_count: int = 0,
) -> dict:
    """Menghitung metrik keseluruhan dataset termasuk persentase kontribusi kategori.

    Args:
        transactions: List transaksi bersih.
        invalid_count: Jumlah baris tidak valid yang disaring saat pembacaan.
        duplicate_count: Jumlah baris duplikat yang dihapus.

    Returns:
        Dictionary lengkap berisi ringkasan metrik keseluruhan dan rincian grup.
    """
    if not transactions:
        return {
            "total_valid_transactions": 0,
            "invalid_rows_skipped": invalid_count,
            "duplicate_rows_removed": duplicate_count,
            "unique_customers": 0,
            "unique_categories": [],
            "total_quantity_sold": 0,
            "total_revenue": 0.0,
            "average_transaction_value": 0.0,
            "min_transaction_value": 0.0,
            "max_transaction_value": 0.0,
            "category_revenue_share_pct": {},
            "by_category": {},
            "by_gender": {},
        }

    total_revenue = sum(row["Total Amount"] for row in transactions)
    total_quantity = sum(row["Quantity"] for row in transactions)
    amounts = [row["Total Amount"] for row in transactions]
    unique_customers = {row["Customer ID"] for row in transactions}
    unique_categories = sorted({row["Product Category"] for row in transactions})
    by_category = summarize_by_category(transactions)
    by_gender = summarize_by_gender(transactions)

    category_share_pct = {
        cat: round((stats["total_revenue"] / total_revenue) * 100, 2)
        if total_revenue > 0
        else 0.0
        for cat, stats in by_category.items()
    }

    return {
        "total_valid_transactions": len(transactions),
        "invalid_rows_skipped": invalid_count,
        "duplicate_rows_removed": duplicate_count,
        "unique_customers": len(unique_customers),
        "unique_categories": unique_categories,
        "total_quantity_sold": total_quantity,
        "total_revenue": round(total_revenue, 2),
        "average_transaction_value": round(total_revenue / len(transactions), 2),
        "min_transaction_value": min(amounts),
        "max_transaction_value": max(amounts),
        "category_revenue_share_pct": category_share_pct,
        "by_category": by_category,
        "by_gender": by_gender,
    }


def find_high_value_transactions(
    transactions: list[dict], threshold: float = 1000.0
) -> list[dict]:
    """Mengambil transaksi bernilai tinggi (>= threshold) terurut dari terbesar.

    Args:
        transactions: List transaksi bersih.
        threshold: Ambang batas Total Amount.

    Returns:
        List transaksi bernilai tinggi terurut menurun.
    """
    high_value = [row for row in transactions if row["Total Amount"] >= threshold]
    return sorted(high_value, key=lambda row: row["Total Amount"], reverse=True)

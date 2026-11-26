"""Module pemrosesan data transaksi (deduplikasi, filtering, pencarian)."""

from .exceptions import InvalidInputError


def remove_duplicate_transactions(
    transactions: list[dict],
) -> tuple[list[dict], list[int]]:
    """Menghapus transaksi duplikat berdasarkan Transaction ID menggunakan struktur set.

    Args:
        transactions: List transaksi yang mungkin mengandung ID duplikat.

    Returns:
        Tuple berisi:
        - unique_transactions: List transaksi unik (mempertahankan kemunculan pertama).
        - duplicate_ids: List Transaction ID yang terdeteksi duplikat.
    """
    seen_ids: set[int] = set()
    unique_transactions: list[dict] = []
    duplicate_ids: list[int] = []

    for row in transactions:
        tx_id = row["Transaction ID"]
        if tx_id in seen_ids:
            duplicate_ids.append(tx_id)
        else:
            seen_ids.add(tx_id)
            unique_transactions.append(row)

    return unique_transactions, duplicate_ids


def get_unique_categories(transactions: list[dict]) -> set[str]:
    """Mengambil seluruh kategori produk unik menggunakan set comprehension.

    Args:
        transactions: List transaksi.

    Returns:
        Set berisi nama kategori produk unik.
    """
    return {row["Product Category"] for row in transactions}


def filter_transactions(
    transactions: list[dict],
    category: str | None = None,
    gender: str | None = None,
    min_total: float | None = None,
) -> list[dict]:
    """Menyaring transaksi berdasarkan kategori, gender, dan nilai minimum belanja.

    Args:
        transactions: List transaksi sumber.
        category: Filter kategori produk (case-insensitive), opsional.
        gender: Filter gender pelanggan (case-insensitive), opsional.
        min_total: Batas minimum Total Amount (>= 0), opsional.

    Returns:
        List transaksi yang memenuhi seluruh kriteria filter.

    Raises:
        InvalidInputError: Jika min_total bernilai negatif.
    """
    if min_total is not None and min_total < 0:
        raise InvalidInputError("Nilai minimum total tidak boleh negatif.")

    norm_category = category.strip().lower() if category else None
    norm_gender = gender.strip().lower() if gender else None

    return [
        row
        for row in transactions
        if (norm_category is None or row["Product Category"].lower() == norm_category)
        and (norm_gender is None or row["Gender"].lower() == norm_gender)
        and (min_total is None or row["Total Amount"] >= min_total)
    ]


def search_transactions(transactions: list[dict], keyword: str) -> list[dict]:
    """Mencari transaksi berdasarkan Transaction ID, Customer ID, atau Product Category.

    Args:
        transactions: List transaksi sumber.
        keyword: Kata kunci pencarian (tidak boleh kosong).

    Returns:
        List transaksi yang cocok dengan kata kunci.

    Raises:
        InvalidInputError: Jika kata kunci kosong.
    """
    cleaned_keyword = keyword.strip().lower()
    if not cleaned_keyword:
        raise InvalidInputError("Kata kunci pencarian tidak boleh kosong.")

    return [
        row
        for row in transactions
        if cleaned_keyword in str(row["Transaction ID"]).lower()
        or cleaned_keyword in row["Customer ID"].lower()
        or cleaned_keyword in row["Product Category"].lower()
    ]

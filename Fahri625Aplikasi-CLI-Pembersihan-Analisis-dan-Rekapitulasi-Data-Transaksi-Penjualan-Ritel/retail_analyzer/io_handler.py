"""Module I/O untuk membaca file CSV serta mengekspor hasil ke CSV dan JSON."""

import csv
import json
from datetime import datetime
from pathlib import Path

from .exceptions import DataFileNotFoundError, InvalidCSVFormatError

REQUIRED_COLUMNS: set[str] = {
    "Transaction ID",
    "Date",
    "Customer ID",
    "Gender",
    "Age",
    "Product Category",
    "Quantity",
    "Price per Unit",
    "Total Amount",
}

FIELD_ORDER: list[str] = [
    "Transaction ID",
    "Date",
    "Customer ID",
    "Gender",
    "Age",
    "Product Category",
    "Quantity",
    "Price per Unit",
    "Total Amount",
]


def _parse_transaction_row(raw_row: dict[str, str]) -> dict:
    """Memvalidasi dan mengonversi satu baris mentah CSV menjadi tipe data yang tepat.

    Args:
        raw_row: Dictionary baris mentah hasil pembacaan csv.DictReader.

    Returns:
        Dictionary transaksi yang sudah tervalidasi dan terkonversi tipenya.

    Raises:
        ValueError: Jika ada kolom kosong, format tanggal salah, atau angka tidak valid.
    """
    cleaned_raw = {k: (v.strip() if isinstance(v, str) else "") for k, v in raw_row.items()}

    for col in REQUIRED_COLUMNS:
        if not cleaned_raw.get(col):
            raise ValueError(f"Kolom '{col}' kosong atau tidak tersedia")

    transaction_id = int(cleaned_raw["Transaction ID"])
    if transaction_id <= 0:
        raise ValueError("Transaction ID harus lebih besar dari 0")

    datetime.strptime(cleaned_raw["Date"], "%Y-%m-%d")

    age = int(cleaned_raw["Age"])
    if age <= 0 or age > 120:
        raise ValueError(f"Age tidak wajar: {age}")

    quantity = int(cleaned_raw["Quantity"])
    if quantity <= 0:
        raise ValueError(f"Quantity harus positif: {quantity}")

    price_per_unit = float(cleaned_raw["Price per Unit"])
    total_amount = float(cleaned_raw["Total Amount"])
    if price_per_unit < 0 or total_amount < 0:
        raise ValueError("Harga atau total tidak boleh bernilai negatif")

    return {
        "Transaction ID": transaction_id,
        "Date": cleaned_raw["Date"],
        "Customer ID": cleaned_raw["Customer ID"],
        "Gender": cleaned_raw["Gender"],
        "Age": age,
        "Product Category": cleaned_raw["Product Category"],
        "Quantity": quantity,
        "Price per Unit": price_per_unit,
        "Total Amount": total_amount,
    }


def load_transactions(filepath: str) -> tuple[list[dict], list[dict]]:
    """Membaca file CSV transaksi dan memisahkan baris valid serta baris tidak valid.

    Args:
        filepath: Path menuju file CSV input.

    Returns:
        Tuple berisi:
        - valid_rows: list[dict] transaksi yang valid.
        - invalid_rows: list[dict] berisi nomor baris, alasan error, dan data mentah.

    Raises:
        DataFileNotFoundError: Jika file tidak ditemukan atau merupakan direktori.
        InvalidCSVFormatError: Jika file kosong, bukan UTF-8, atau header tidak lengkap.
    """
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        raise DataFileNotFoundError(f"File tidak ditemukan: {filepath}")

    valid_rows: list[dict] = []
    invalid_rows: list[dict] = []

    try:
        with path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise InvalidCSVFormatError("File CSV kosong atau tidak memiliki header.")

            header_set = {name.strip() for name in reader.fieldnames if name}
            missing_columns = REQUIRED_COLUMNS - header_set
            if missing_columns:
                missing_str = ", ".join(sorted(missing_columns))
                raise InvalidCSVFormatError(
                    f"Kolom wajib tidak ditemukan pada CSV: {missing_str}"
                )

            for row_number, raw_row in enumerate(reader, start=2):
                try:
                    parsed = _parse_transaction_row(raw_row)
                    valid_rows.append(parsed)
                except ValueError as err:
                    invalid_rows.append(
                        {
                            "row_number": row_number,
                            "reason": str(err),
                            "raw_data": raw_row,
                        }
                    )
    except UnicodeDecodeError as err:
        raise InvalidCSVFormatError(f"Encoding file tidak valid (harus UTF-8): {err}") from err
    except csv.Error as err:
        raise InvalidCSVFormatError(f"Format CSV rusak: {err}") from err

    return valid_rows, invalid_rows


def save_cleaned_csv(transactions: list[dict], filepath: str) -> str:
    """Menyimpan daftar transaksi bersih ke dalam file CSV baru.

    Args:
        transactions: List dictionary transaksi yang akan disimpan.
        filepath: Path file CSV tujuan.

    Returns:
        String path absolut dari file yang berhasil disimpan.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELD_ORDER)
        writer.writeheader()
        for row in transactions:
            writer.writerow({field: row.get(field, "") for field in FIELD_ORDER})

    return str(path.resolve())


def save_summary_json(summary: dict, filepath: str) -> str:
    """Menyimpan hasil ringkasan analisis ke dalam file JSON.

    Args:
        summary: Dictionary berisi metrik rekapitulasi penjualan.
        filepath: Path file JSON tujuan.

    Returns:
        String path absolut dari file yang berhasil disimpan.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, ensure_ascii=False)

    return str(path.resolve())

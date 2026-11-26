"""Entry point CLI untuk Aplikasi Pembersihan dan Analisis Data Transaksi Ritel."""

import argparse
import sys
from pathlib import Path

from retail_analyzer import (
    InvalidInputError,
    RetailAnalyzerError,
    compute_overall_metrics,
    filter_transactions,
    get_unique_categories,
    load_transactions,
    remove_duplicate_transactions,
    save_cleaned_csv,
    save_summary_json,
    search_transactions,
)


def print_summary(summary: dict) -> None:
    """Menampilkan ringkasan hasil analisis transaksi ke layar terminal."""
    print("\n" + "=" * 60)
    print("RINGKASAN ANALISIS TRANSAKSI PENJUALAN RITEL")
    print("=" * 60)
    print(f"Transaksi Valid       : {summary['total_valid_transactions']}")
    print(f"Baris Tidak Valid     : {summary['invalid_rows_skipped']}")
    print(f"Duplikat Dihapus      : {summary['duplicate_rows_removed']}")
    print(f"Pelanggan Unik        : {summary['unique_customers']}")
    print(f"Total Barang Terjual  : {summary['total_quantity_sold']}")
    print(f"Total Pendapatan      : {summary['total_revenue']:,.2f}")
    print(f"Rata-rata Transaksi   : {summary['average_transaction_value']:,.2f}")
    print(
        f"Rentang Transaksi     : {summary['min_transaction_value']:,.2f} - "
        f"{summary['max_transaction_value']:,.2f}"
    )

    if summary["by_category"]:
        print("\n--- Rekapitulasi per Kategori ---")
        for cat, stats in sorted(summary["by_category"].items()):
            share = summary["category_revenue_share_pct"].get(cat, 0.0)
            print(
                f"  - {cat:<15} | Transaksi: {stats['transaction_count']:>4} | "
                f"Qty: {stats['total_quantity']:>4} | "
                f"Omzet: {stats['total_revenue']:>10,.2f} ({share}%)"
            )

    if summary["by_gender"]:
        print("\n--- Rekapitulasi per Gender ---")
        for gender, stats in sorted(summary["by_gender"].items()):
            print(
                f"  - {gender:<15} | Transaksi: {stats['transaction_count']:>4} | "
                f"Omzet: {stats['total_revenue']:>10,.2f}"
            )
    print("=" * 60)


def print_transactions_preview(transactions: list[dict], limit: int = 10) -> None:
    """Menampilkan cuplikan baris transaksi dalam format tabel ringkas."""
    if not transactions:
        print("\n[Info] Tidak ada data transaksi yang cocok.")
        return

    print(f"\nMenampilkan {min(len(transactions), limit)} dari {len(transactions)} transaksi:")
    print(
        f"{'ID':<6} {'Tanggal':<12} {'Customer':<10} {'Gender':<8} "
        f"{'Kategori':<14} {'Qty':>4} {'Total':>10}"
    )
    print("-" * 72)
    for row in transactions[:limit]:
        print(
            f"{row['Transaction ID']:<6} {row['Date']:<12} {row['Customer ID']:<10} "
            f"{row['Gender']:<8} {row['Product Category']:<14} "
            f"{row['Quantity']:>4} {row['Total Amount']:>10,.2f}"
        )


def run_batch(args: argparse.Namespace) -> int:
    """Menjalankan alur analisis penuh secara non-interaktif (batch mode)."""
    try:
        valid_rows, invalid_rows = load_transactions(args.input)
        unique_rows, duplicate_ids = remove_duplicate_transactions(valid_rows)

        working_rows = unique_rows
        if args.category or args.gender or args.min_total is not None:
            working_rows = filter_transactions(
                working_rows,
                category=args.category,
                gender=args.gender,
                min_total=args.min_total,
            )

        if args.search:
            working_rows = search_transactions(working_rows, args.search)

        summary = compute_overall_metrics(
            working_rows,
            invalid_count=len(invalid_rows),
            duplicate_count=len(duplicate_ids),
        )
        print_summary(summary)

        if invalid_rows:
            print("\n[Peringatan] Ditemukan baris tidak valid yang dilewati:")
            for item in invalid_rows[:5]:
                print(f"  Baris {item['row_number']}: {item['reason']}")

        out_dir = Path(args.output_dir)
        csv_path = save_cleaned_csv(working_rows, str(out_dir / "cleaned_transactions.csv"))
        json_path = save_summary_json(summary, str(out_dir / "sales_summary.json"))
        print(f"\n[Sukses] CSV bersih disimpan ke : {csv_path}")
        print(f"[Sukses] Ringkasan JSON disimpan : {json_path}")
        return 0
    except RetailAnalyzerError as err:
        print(f"[Error] {err}", file=sys.stderr)
        return 1


def run_interactive(default_input: str, default_output_dir: str) -> int:
    """Menjalankan menu interaktif berbasis command line."""
    transactions: list[dict] = []
    invalid_rows: list[dict] = []
    duplicate_ids: list[int] = []
    current_file = default_input

    print("Selamat datang di Aplikasi Analisis Transaksi Penjualan Ritel (CLI)")
    while True:
        print("\n--- MENU UTAMA ---")
        print(f"Dataset aktif: {current_file} ({len(transactions)} transaksi siap)")
        print("1. Muat & bersihkan file CSV")
        print("2. Tampilkan ringkasan & rekapitulasi")
        print("3. Filter transaksi (kategori / gender / min total)")
        print("4. Cari transaksi (ID / Customer / Kategori)")
        print("5. Ekspor hasil ke CSV dan JSON")
        print("0. Keluar")

        choice = input("Pilih menu (0-5): ").strip()

        if choice == "0":
            print("Terima kasih. Program selesai.")
            return 0

        elif choice == "1":
            user_path = input(f"Masukkan path CSV [{default_input}]: ").strip()
            target_path = user_path if user_path else default_input
            try:
                raw_valid, invalid_rows = load_transactions(target_path)
                transactions, duplicate_ids = remove_duplicate_transactions(raw_valid)
                current_file = target_path
                print(
                    f"[Sukses] Dimuat {len(transactions)} transaksi unik. "
                    f"(Dilewati: {len(invalid_rows)} baris tidak valid, "
                    f"{len(duplicate_ids)} duplikat)"
                )
            except RetailAnalyzerError as err:
                print(f"[Error] {err}")

        elif choice == "2":
            if not transactions:
                print("[Info] Belum ada data dimuat. Pilih menu 1 terlebih dahulu.")
                continue
            summary = compute_overall_metrics(
                transactions,
                invalid_count=len(invalid_rows),
                duplicate_count=len(duplicate_ids),
            )
            print_summary(summary)

        elif choice == "3":
            if not transactions:
                print("[Info] Belum ada data dimuat. Pilih menu 1 terlebih dahulu.")
                continue
            categories = sorted(get_unique_categories(transactions))
            print(f"Kategori tersedia: {', '.join(categories)}")
            cat = input("Filter kategori (kosongkan jika semua): ").strip() or None
            gen = input("Filter gender Male/Female (kosongkan jika semua): ").strip() or None
            min_str = input("Minimum total belanja (kosongkan jika tanpa batas): ").strip()

            try:
                min_val = float(min_str) if min_str else None
                filtered = filter_transactions(
                    transactions, category=cat, gender=gen, min_total=min_val
                )
                print_transactions_preview(filtered, limit=15)
            except ValueError:
                print("[Error] Minimum total harus berupa angka.")
            except InvalidInputError as err:
                print(f"[Error] {err}")

        elif choice == "4":
            if not transactions:
                print("[Info] Belum ada data dimuat. Pilih menu 1 terlebih dahulu.")
                continue
            keyword = input("Masukkan kata kunci (Transaction ID / Customer ID / Kategori): ")
            try:
                results = search_transactions(transactions, keyword)
                print_transactions_preview(results, limit=15)
            except InvalidInputError as err:
                print(f"[Error] {err}")

        elif choice == "5":
            if not transactions:
                print("[Info] Belum ada data dimuat. Pilih menu 1 terlebih dahulu.")
                continue
            out_dir = Path(default_output_dir)
            summary = compute_overall_metrics(
                transactions,
                invalid_count=len(invalid_rows),
                duplicate_count=len(duplicate_ids),
            )
            csv_path = save_cleaned_csv(transactions, str(out_dir / "cleaned_transactions.csv"))
            json_path = save_summary_json(summary, str(out_dir / "sales_summary.json"))
            print(f"[Sukses] CSV bersih : {csv_path}")
            print(f"[Sukses] Summary JSON: {json_path}")

        else:
            print("[Peringatan] Pilihan tidak valid. Silakan masukkan angka 0 sampai 5.")


def build_parser() -> argparse.ArgumentParser:
    """Membangun parser argumen CLI menggunakan argparse."""
    parser = argparse.ArgumentParser(
        description="Aplikasi CLI pembersihan, analisis, dan rekapitulasi transaksi ritel."
    )
    parser.add_argument(
        "--input",
        default="retail_sales_dataset.csv",
        help="Path ke file CSV input (default: retail_sales_dataset.csv)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Direktori penyimpanan file output CSV & JSON (default: output)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Jalankan otomatis tanpa menu interaktif dan langsung ekspor hasil.",
    )
    parser.add_argument("--category", help="Filter berdasarkan kategori produk.")
    parser.add_argument("--gender", help="Filter berdasarkan gender pelanggan.")
    parser.add_argument(
        "--min-total", type=float, default=None, help="Filter minimum Total Amount."
    )
    parser.add_argument("--search", help="Kata kunci pencarian ID/Customer/Kategori.")
    return parser


def main() -> int:
    """Fungsi utama program."""
    parser = build_parser()
    args = parser.parse_args()

    if args.batch:
        return run_batch(args)
    return run_interactive(default_input=args.input, default_output_dir=args.output_dir)


if __name__ == "__main__":
    sys.exit(main())

"""Unit test untuk memverifikasi alur normal, edge case, dan exception handling."""

import tempfile
import unittest
from pathlib import Path

from retail_analyzer import (
    DataFileNotFoundError,
    InvalidCSVFormatError,
    InvalidInputError,
    compute_overall_metrics,
    filter_transactions,
    load_transactions,
    remove_duplicate_transactions,
    save_cleaned_csv,
    save_summary_json,
    search_transactions,
)


class TestRetailAnalyzer(unittest.TestCase):
    """Kumpulan pengujian untuk package retail_analyzer."""

    def test_load_main_dataset_normal(self) -> None:
        valid_rows, invalid_rows = load_transactions("retail_sales_dataset.csv")
        self.assertEqual(len(valid_rows), 1000)
        self.assertEqual(len(invalid_rows), 0)

    def test_edge_cases_csv(self) -> None:
        valid_rows, invalid_rows = load_transactions("data/sample_edge_cases.csv")
        # Baris valid: ID 101, 102, 101 (duplikat), 107 -> 4 baris valid secara format
        self.assertEqual(len(valid_rows), 4)
        # Baris tidak valid: ID 103 (Age -5), 104 (kategori kosong), 105 (harga 'abc'), 106 (tanggal salah)
        self.assertEqual(len(invalid_rows), 4)

        unique_rows, duplicate_ids = remove_duplicate_transactions(valid_rows)
        self.assertEqual(len(unique_rows), 3)
        self.assertEqual(duplicate_ids, [101])

    def test_empty_dataset_metrics_edge_case(self) -> None:
        metrics = compute_overall_metrics([])
        self.assertEqual(metrics["total_valid_transactions"], 0)
        self.assertEqual(metrics["total_revenue"], 0.0)
        self.assertEqual(metrics["by_category"], {})

    def test_file_not_found_exception(self) -> None:
        with self.assertRaises(DataFileNotFoundError):
            load_transactions("file_tidak_ada.csv")

    def test_invalid_csv_header_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_csv = Path(tmpdir) / "bad.csv"
            bad_csv.write_text("col_a,col_b\n1,2\n", encoding="utf-8")
            with self.assertRaises(InvalidCSVFormatError):
                load_transactions(str(bad_csv))

    def test_filter_and_search_and_export(self) -> None:
        valid_rows, _ = load_transactions("retail_sales_dataset.csv")
        beauty_high = filter_transactions(valid_rows, category="Beauty", min_total=1000)
        self.assertTrue(len(beauty_high) > 0)
        self.assertTrue(all(r["Product Category"] == "Beauty" for r in beauty_high))
        self.assertTrue(all(r["Total Amount"] >= 1000 for r in beauty_high))

        found = search_transactions(valid_rows, "CUST001")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["Transaction ID"], 1)

        with self.assertRaises(InvalidInputError):
            filter_transactions(valid_rows, min_total=-10)

        with self.assertRaises(InvalidInputError):
            search_transactions(valid_rows, "   ")

        with tempfile.TemporaryDirectory() as tmpdir:
            summary = compute_overall_metrics(beauty_high)
            csv_out = save_cleaned_csv(beauty_high, str(Path(tmpdir) / "out.csv"))
            json_out = save_summary_json(summary, str(Path(tmpdir) / "out.json"))
            self.assertTrue(Path(csv_out).exists())
            self.assertTrue(Path(json_out).exists())


if __name__ == "__main__":
    unittest.main()

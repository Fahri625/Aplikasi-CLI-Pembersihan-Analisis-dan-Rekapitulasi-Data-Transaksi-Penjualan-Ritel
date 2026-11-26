"""Package retail_analyzer untuk pembersihan dan analisis data transaksi ritel."""

from .analytics import (
    compute_overall_metrics,
    find_high_value_transactions,
    summarize_by_category,
    summarize_by_gender,
)
from .exceptions import (
    DataFileNotFoundError,
    InvalidCSVFormatError,
    InvalidInputError,
    RetailAnalyzerError,
)
from .io_handler import load_transactions, save_cleaned_csv, save_summary_json
from .processor import (
    filter_transactions,
    get_unique_categories,
    remove_duplicate_transactions,
    search_transactions,
)

__all__ = [
    "RetailAnalyzerError",
    "DataFileNotFoundError",
    "InvalidCSVFormatError",
    "InvalidInputError",
    "load_transactions",
    "save_cleaned_csv",
    "save_summary_json",
    "remove_duplicate_transactions",
    "filter_transactions",
    "search_transactions",
    "get_unique_categories",
    "summarize_by_category",
    "summarize_by_gender",
    "compute_overall_metrics",
    "find_high_value_transactions",
]

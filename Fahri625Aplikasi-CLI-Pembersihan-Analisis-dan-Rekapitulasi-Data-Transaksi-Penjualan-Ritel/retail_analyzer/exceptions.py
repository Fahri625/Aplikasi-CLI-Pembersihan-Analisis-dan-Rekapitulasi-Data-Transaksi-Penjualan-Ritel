"""Custom exceptions untuk penanganan error pada aplikasi retail_analyzer."""


class RetailAnalyzerError(Exception):
    """Base exception untuk seluruh error aplikasi retail_analyzer."""


class DataFileNotFoundError(RetailAnalyzerError):
    """Dilemparkan ketika file input tidak ditemukan atau tidak bisa diakses."""


class InvalidCSVFormatError(RetailAnalyzerError):
    """Dilemparkan ketika struktur header atau format file CSV tidak valid."""


class InvalidInputError(RetailAnalyzerError):
    """Dilemparkan ketika input parameter dari pengguna tidak valid."""

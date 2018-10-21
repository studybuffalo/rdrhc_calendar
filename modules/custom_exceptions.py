"""Custom exceptions for the application."""

class ScheduleError(LookupError):
    """Exception raised for errors in extracting schedule data."""
    pass

class UploadError(ConnectionError):
    """Exception raised for errors related to API uploads."""
    pass

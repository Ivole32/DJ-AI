"""
Utility functions for filtering data dictionaries.
"""
def filter_data(data: dict, allowed_fields: list) -> dict:
    """
    Filter data to only include whitelisted fields.
    Arguments:
        data: The original data dictionary.
        allowed_fields: List of fields to include in the filtered data.
    Returns:
        Filtered data dictionary.
    """
    return {key: data.get(key) for key in allowed_fields if key in data}
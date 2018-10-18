"""General functions used across modules."""

def convert_duration_to_hours_minutes(duration):
    """Converts a duration (hours) to hours & minutes."""
    hours = int(duration)
    minutes = int((duration*60) % 60)

    return hours, minutes

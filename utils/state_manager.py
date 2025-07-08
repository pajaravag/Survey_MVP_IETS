import os
import pandas as pd
from datetime import datetime


def flatten_session_state(d, parent_key='', sep='__'):
    """
    Recursively flattens a nested session_state dictionary for CSV or Sheets export.
    Lists are joined into comma-separated strings.
    Booleans are converted to "Sí" / "No" for better readability.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_session_state(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = ", ".join(map(str, v))
        elif isinstance(v, bool):
            items[new_key] = "Sí" if v else "No"
        else:
            items[new_key] = v
    return items


def save_response_to_csv(session_state, output_dir="data/responses"):
    """
    Saves session data to:
    - A unique timestamped CSV
    - A cumulative master CSV (appended)
    """
    os.makedirs(output_dir, exist_ok=True)

    flat_data = flatten_session_state(session_state)
    df = pd.DataFrame([flat_data])

    ips_id = flat_data.get("identificacion__ips_id", "anonimo").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"BLH_{ips_id}_{timestamp}.csv"
    unique_path = os.path.join(output_dir, unique_filename)

    df.to_csv(unique_path, index=False)

    master_path = os.path.join(output_dir, "responses_master.csv")
    if os.path.exists(master_path):
        df.to_csv(master_path, mode="a", header=False, index=False)
    else:
        df.to_csv(master_path, index=False)

    return unique_path


def compute_progress(session_state, tracked_completion_flags):
    """
    Calculates progress based on the presence of completion flags.

    Args:
        session_state: Streamlit session state dictionary.
        tracked_completion_flags: List of string keys ending with '__completed'.

    Returns:
        (int, int): Tuple of (number of completed sections, percent completed).
    """
    filled = sum(1 for flag in tracked_completion_flags if session_state.get(flag, False))
    percent_complete = int((filled / len(tracked_completion_flags)) * 100) if tracked_completion_flags else 0
    return filled, percent_complete


def is_section_completed(session_state, completion_flag):
    """
    Checks whether a section is marked as completed.

    Args:
        session_state: Streamlit session state dictionary.
        completion_flag: Key like 'infraestructura_equipos__completed'.

    Returns:
        bool: True if completed, False otherwise.
    """
    return session_state.get(completion_flag, False)

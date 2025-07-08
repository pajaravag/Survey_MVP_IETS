import os
import pandas as pd
from datetime import datetime


def flatten_session_state(d, parent_key='', sep='__'):
    """
    Recursively flattens a nested session_state dictionary for CSV or Sheets export.
    Lists are joined into comma-separated strings.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_session_state(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = ", ".join(map(str, v))
        else:
            items[new_key] = v
    return items


def save_response_to_csv(session_state, output_dir="data/responses"):
    """
    Saves session data to both:
    - A unique timestamped CSV file
    - A master cumulative CSV file
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
    Calculates progress based on explicit completion flags.

    Parameters:
        session_state (dict): The Streamlit session state.
        tracked_completion_flags (list of str): List of keys like 'datos_generales__completed'.

    Returns:
        filled (int): Number of completed sections.
        percent_complete (int): Percentage of completed sections.
    """
    filled = sum(1 for flag in tracked_completion_flags if session_state.get(flag, False))
    percent_complete = int((filled / len(tracked_completion_flags)) * 100) if tracked_completion_flags else 0
    return filled, percent_complete


def is_section_completed(session_state, completion_flag):
    """
    Checks if a specific section is completed based on its exact flag.

    Parameters:
        session_state (dict): The Streamlit session state.
        completion_flag (str): The full key like 'datos_generales__completed'.

    Returns:
        bool: True if completed, False otherwise.
    """
    return session_state.get(completion_flag, False)

import os
import pandas as pd
from datetime import datetime


def flatten_session_state(d, parent_key='', sep='__'):
    """
    Fully flattens any nested structure inside session_state for safe CSV/Google Sheets export.
    Handles arbitrary nesting depth. List values are joined as comma-separated strings.
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
    Saves a single session state response to:
    - A unique timestamped file
    - A master file for all responses
    """
    os.makedirs(output_dir, exist_ok=True)

    # Flatten and convert to DataFrame
    flat_data = flatten_session_state(session_state)
    df = pd.DataFrame([flat_data])

    # Create unique filename with IPS ID and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ips_id = session_state.get("identificacion", {}).get("ips_id", "anonimo").replace(" ", "_")
    unique_filename = f"BLH_{ips_id}_{timestamp}.csv"
    unique_path = os.path.join(output_dir, unique_filename)
    df.to_csv(unique_path, index=False)

    # Append to master file
    master_path = os.path.join(output_dir, "responses_master.csv")
    if os.path.exists(master_path):
        df.to_csv(master_path, mode="a", header=False, index=False)
    else:
        df.to_csv(master_path, index=False)

    return unique_path


def compute_progress(session_state, tracked_sections):
    """
    Calculates how many sections are filled and returns a progress count and percentage.
    """
    filled = sum(1 for key in tracked_sections if key in session_state and session_state[key])
    percent_complete = int((filled / len(tracked_sections)) * 100)
    return filled, percent_complete


def is_section_completed(session_state, key):
    """
    Returns True if the given section is filled and not empty.
    """
    return key in session_state and session_state[key] not in (None, {}, [])

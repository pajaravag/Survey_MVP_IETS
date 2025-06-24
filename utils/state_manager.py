import os
import pandas as pd
from datetime import datetime


def flatten_session_state(session_state):
    """
    Flattens nested dictionaries for flat CSV export.
    """
    flat_data = {}
    for key, value in session_state.items():
        if isinstance(value, dict):
            for subkey, subval in value.items():
                if isinstance(subval, dict):  # nested dict (e.g. equipment per role)
                    for k, v in subval.items():
                        flat_data[f"{key}__{subkey}__{k}"] = v
                else:
                    flat_data[f"{key}__{subkey}"] = subval
        elif isinstance(value, list):
            flat_data[key] = ", ".join(map(str, value))
        else:
            flat_data[key] = value
    return flat_data


def save_response_to_csv(session_state, output_dir="data/responses"):
    """
    Saves the session to both a unique file and appends to a master file.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Flatten and convert to DataFrame
    flat_data = flatten_session_state(session_state)
    df = pd.DataFrame([flat_data])

    # Timestamped filename
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
    Counts how many sections are present in session_state
    and returns progress in percent.
    """
    filled = sum(1 for key in tracked_sections if key in session_state)
    percent_complete = int((filled / len(tracked_sections)) * 100)
    return filled, percent_complete

def is_section_completed(session_state, key):
    """
    Returns True if the section key exists and has non-empty data.
    """
    return key in session_state and session_state[key] != {} and session_state[key] is not None

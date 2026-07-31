from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, render_template, send_file

app = Flask(__name__)

USGS_FEED_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
)
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "earthquakes.csv"


def fetch_earthquakes() -> list[dict[str, Any]]:
    """Download and normalize earthquakes from the USGS GeoJSON feed."""
    response = requests.get(USGS_FEED_URL, timeout=15)
    response.raise_for_status()
    payload = response.json()

    earthquakes: list[dict[str, Any]] = []

    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get("coordinates", [])

        if len(coordinates) < 3:
            continue

        timestamp_ms = properties.get("time")
        event_time = None

        if timestamp_ms is not None:
            event_time = datetime.fromtimestamp(
                timestamp_ms / 1000,
                tz=timezone.utc,
            ).isoformat()

        earthquakes.append(
            {
                "id": feature.get("id"),
                "magnitude": properties.get("mag"),
                "location": properties.get("place") or "Unknown location",
                "depth_km": coordinates[2],
                "longitude": coordinates[0],
                "latitude": coordinates[1],
                "time_utc": event_time,
                "details_url": properties.get("url"),
            }
        )

    return earthquakes


def earthquakes_to_dataframe(
    earthquakes: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Convert earthquake records into a cleaned pandas DataFrame.
    """

    columns = [
        "id",
        "magnitude",
        "location",
        "depth_km",
        "longitude",
        "latitude",
        "time_utc",
        "details_url",
    ]

    dataframe = pd.DataFrame(
        earthquakes,
        columns=columns,
    )

    if dataframe.empty:
        return dataframe

    numeric_columns = [
        "magnitude",
        "depth_km",
        "longitude",
        "latitude",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe["time_utc"] = pd.to_datetime(
        dataframe["time_utc"],
        errors="coerce",
        utc=True,
    )

    return dataframe


def save_to_csv(
    earthquakes: list[dict[str, Any]],
) -> Path:
    """
    Save earthquake data using pandas.
    """

    DATA_DIR.mkdir(exist_ok=True)

    dataframe = earthquakes_to_dataframe(
        earthquakes
    )

    dataframe.to_csv(
        CSV_PATH,
        index=False,
    )

    return CSV_PATH


def safe_float(
    value: Any,
    decimals: int = 2,
) -> float | None:
    """
    Convert NumPy/pandas values into normal Python floats
    for JSON serialization.
    """

    if value is None or pd.isna(value):
        return None

    return round(
        float(value),
        decimals,
    )


def calculate_statistics(
    earthquakes: list[dict[str, Any]],
) -> dict[str, Any]:

    dataframe = earthquakes_to_dataframe(
        earthquakes
    )

    if dataframe.empty:
        return {
            "count": 0,
            "average_magnitude": None,
            "median_magnitude": None,
            "minimum_magnitude": None,
            "maximum_magnitude": None,
            "average_depth_km": None,
            "maximum_depth_km": None,
            "largest_location": None,
        }

    magnitudes = dataframe["magnitude"].dropna()
    depths = dataframe["depth_km"].dropna()

    #largest_index = magnitudes.idxmax()
    largest_location = None

    if not magnitudes.empty:
        largest_index = magnitudes.idxmax()
        largest_location = dataframe.loc[
            largest_index,
            "location",
        ]

    return {

        "count": int(len(dataframe)),

        "average_magnitude":
            safe_float(
                np.mean(magnitudes)
            ),

        "median_magnitude":
            safe_float(
                np.median(magnitudes)
            ),

        "minimum_magnitude":
            safe_float(
                np.min(magnitudes)
            ),

        "maximum_magnitude":
            safe_float(
                np.max(magnitudes)
            ),

        "average_depth_km":
            safe_float(
                np.mean(depths)
            ),

        "maximum_depth_km":
            safe_float(
                np.max(depths)
            ),

        "largest_location": largest_location,
    }

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/earthquakes")
def earthquakes_api():
    try:
        earthquakes = fetch_earthquakes()

        return jsonify(
            {
                "earthquakes": earthquakes
            }
        )

    except requests.RequestException as exc:
        return jsonify(
            {
                "error": f"Unable to contact USGS: {exc}"
            }
        ), 502


@app.get("/api/statistics")
def statistics_api():
    try:
        earthquakes = fetch_earthquakes()

        statistics = calculate_statistics(
            earthquakes
        )

        return jsonify(statistics)

    except requests.RequestException as exc:
        return jsonify(
            {
                "error": f"Unable to contact USGS: {exc}"
            }
        ), 502


@app.post("/api/download")
def download_api():
    try:
        earthquakes = fetch_earthquakes()

        csv_path = save_to_csv(
            earthquakes
        )

        return jsonify(
            {
                "message": (
                    "Earthquake data saved successfully."
                ),
                "records": len(earthquakes),
                "file": str(csv_path),
            }
        )

    except requests.RequestException as exc:
        return jsonify(
            {
                "error": f"Unable to contact USGS: {exc}"
            }
        ), 502

    except OSError as exc:
        return jsonify(
            {
                "error": f"Unable to save CSV file: {exc}"
            }
        ), 500


@app.get("/download/csv")
def download_csv():
    if not CSV_PATH.exists():
        return jsonify(
            {
                "error": (
                    "Download data first to create "
                    "the CSV file."
                )
            }
        ), 404

    return send_file(
        CSV_PATH.resolve(),
        as_attachment=True,
        download_name="earthquakes.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
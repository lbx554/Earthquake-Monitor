from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from flask import Flask, abort, jsonify, render_template, send_file, url_for

app = Flask(__name__)

USGS_FEED_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
)
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "earthquakes.csv"
GENERATED_DIR = Path("static/generated")


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

        event_id = feature.get("id")
        if not event_id:
            continue

        earthquakes.append(
            {
                "id": event_id,
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
    """Convert earthquake records into a cleaned pandas DataFrame."""
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

    dataframe = pd.DataFrame(earthquakes, columns=columns)

    if dataframe.empty:
        return dataframe

    for column in ["magnitude", "depth_km", "longitude", "latitude"]:
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


def save_to_csv(earthquakes: list[dict[str, Any]]) -> Path:
    """Save earthquake data using pandas."""
    DATA_DIR.mkdir(exist_ok=True)
    dataframe = earthquakes_to_dataframe(earthquakes)
    dataframe.to_csv(CSV_PATH, index=False)
    return CSV_PATH


def safe_float(value: Any, decimals: int = 2) -> float | None:
    """Convert NumPy/pandas values into JSON-safe Python floats."""
    if value is None or pd.isna(value):
        return None

    return round(float(value), decimals)


def calculate_statistics(
    earthquakes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate statistics for the entire current earthquake feed."""
    dataframe = earthquakes_to_dataframe(earthquakes)

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

    largest_location = None
    if not magnitudes.empty:
        largest_index = magnitudes.idxmax()
        largest_location = dataframe.loc[largest_index, "location"]

    return {
        "count": int(len(dataframe)),
        "average_magnitude": (
            safe_float(np.mean(magnitudes)) if not magnitudes.empty else None
        ),
        "median_magnitude": (
            safe_float(np.median(magnitudes)) if not magnitudes.empty else None
        ),
        "minimum_magnitude": (
            safe_float(np.min(magnitudes)) if not magnitudes.empty else None
        ),
        "maximum_magnitude": (
            safe_float(np.max(magnitudes)) if not magnitudes.empty else None
        ),
        "average_depth_km": (
            safe_float(np.mean(depths)) if not depths.empty else None
        ),
        "maximum_depth_km": (
            safe_float(np.max(depths)) if not depths.empty else None
        ),
        "largest_location": largest_location,
    }


def find_earthquake(
    earthquakes: list[dict[str, Any]],
    event_id: str,
) -> dict[str, Any] | None:
    """Find one earthquake by its USGS event ID."""
    return next(
        (earthquake for earthquake in earthquakes if earthquake["id"] == event_id),
        None,
    )


def percentile_rank(series: pd.Series, value: Any) -> float | None:
    """Return the percentage of feed values less than or equal to a value."""
    clean_series = series.dropna()

    if clean_series.empty or value is None or pd.isna(value):
        return None

    return safe_float((clean_series <= float(value)).mean() * 100)


def calculate_event_statistics(
    earthquake: dict[str, Any],
    earthquakes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare one earthquake with all events in the current USGS feed."""
    dataframe = earthquakes_to_dataframe(earthquakes)

    magnitudes = dataframe["magnitude"].dropna()
    depths = dataframe["depth_km"].dropna()

    magnitude = earthquake.get("magnitude")
    depth = earthquake.get("depth_km")

    average_magnitude = np.mean(magnitudes) if not magnitudes.empty else None
    average_depth = np.mean(depths) if not depths.empty else None

    return {
        "feed_count": int(len(dataframe)),
        "magnitude_percentile": percentile_rank(magnitudes, magnitude),
        "depth_percentile": percentile_rank(depths, depth),
        "feed_average_magnitude": safe_float(average_magnitude),
        "feed_average_depth_km": safe_float(average_depth),
        "magnitude_difference_from_average": (
            safe_float(float(magnitude) - float(average_magnitude))
            if magnitude is not None and average_magnitude is not None
            else None
        ),
        "depth_difference_from_average_km": (
            safe_float(float(depth) - float(average_depth))
            if depth is not None and average_depth is not None
            else None
        ),
    }


def generate_event_visualization(
    earthquake: dict[str, Any],
    earthquakes: list[dict[str, Any]],
) -> str:
    """Create a scatter plot highlighting one event in the current feed."""
    dataframe = earthquakes_to_dataframe(earthquakes)
    plot_data = dataframe.dropna(subset=["magnitude", "depth_km"])

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    event_id = earthquake["id"]
    safe_event_id = "".join(
        character for character in event_id if character.isalnum() or character in "-_"
    )
    filename = f"earthquake_{safe_event_id}.png"
    output_path = GENERATED_DIR / filename

    figure, axis = plt.subplots(figsize=(5.5, 3.5))

    if not plot_data.empty:
        axis.scatter(
            plot_data["magnitude"],
            plot_data["depth_km"],
            alpha=0.35,
            label="Other earthquakes",
        )

    magnitude = earthquake.get("magnitude")
    depth = earthquake.get("depth_km")

    if magnitude is not None and depth is not None:
        axis.scatter(
            [magnitude],
            [depth],
            s=180,
            marker="*",
            label="Selected earthquake",
        )

    axis.set_title("Selected Earthquake Compared with Current Feed")
    axis.set_xlabel("Magnitude")
    axis.set_ylabel("Depth (km)")
    axis.invert_yaxis()
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    return url_for("static", filename=f"generated/{filename}")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/earthquake/<event_id>")
def earthquake_detail(event_id: str):
    """Display statistics and a visualization for one earthquake."""
    try:
        earthquakes = fetch_earthquakes()
    except requests.RequestException as exc:
        return render_template(
            "earthquake_detail.html",
            earthquake=None,
            event_statistics=None,
            visualization_url=None,
            error=f"Unable to contact USGS: {exc}",
        ), 502

    earthquake = find_earthquake(earthquakes, event_id)

    if earthquake is None:
        abort(404, description="Earthquake event not found in the current feed.")

    event_statistics = calculate_event_statistics(earthquake, earthquakes)
    visualization_url = generate_event_visualization(earthquake, earthquakes)

    return render_template(
        "earthquake_detail.html",
        earthquake=earthquake,
        event_statistics=event_statistics,
        visualization_url=visualization_url,
        error=None,
    )


@app.get("/api/earthquakes")
def earthquakes_api():
    try:
        earthquakes = fetch_earthquakes()
        return jsonify({"earthquakes": earthquakes})
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to contact USGS: {exc}"}), 502


@app.get("/api/earthquakes/<event_id>")
def earthquake_detail_api(event_id: str):
    """Return one earthquake and its contextual statistics as JSON."""
    try:
        earthquakes = fetch_earthquakes()
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to contact USGS: {exc}"}), 502

    earthquake = find_earthquake(earthquakes, event_id)

    if earthquake is None:
        return jsonify({"error": "Earthquake event not found."}), 404

    return jsonify(
        {
            "earthquake": earthquake,
            "statistics": calculate_event_statistics(
                earthquake,
                earthquakes,
            ),
        }
    )


@app.get("/api/statistics")
def statistics_api():
    try:
        earthquakes = fetch_earthquakes()
        return jsonify(calculate_statistics(earthquakes))
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to contact USGS: {exc}"}), 502


@app.post("/api/download")
def download_api():
    try:
        earthquakes = fetch_earthquakes()
        csv_path = save_to_csv(earthquakes)

        return jsonify(
            {
                "message": "Earthquake data saved successfully.",
                "records": len(earthquakes),
                "file": str(csv_path),
            }
        )
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to contact USGS: {exc}"}), 502
    except OSError as exc:
        return jsonify({"error": f"Unable to save CSV file: {exc}"}), 500


@app.get("/download/csv")
def download_csv():
    if not CSV_PATH.exists():
        return jsonify(
            {"error": "Download data first to create the CSV file."}
        ), 404

    return send_file(
        CSV_PATH.resolve(),
        as_attachment=True,
        download_name="earthquakes.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)

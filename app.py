from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

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
                timestamp_ms / 1000, tz=timezone.utc
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


def save_to_csv(earthquakes: list[dict[str, Any]]) -> Path:
    """Save normalized earthquake records to a local CSV file."""
    DATA_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "id",
        "magnitude",
        "location",
        "depth_km",
        "longitude",
        "latitude",
        "time_utc",
        "details_url",
    ]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(earthquakes)

    return CSV_PATH


def calculate_statistics(earthquakes: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate basic statistics while safely ignoring missing values."""
    magnitudes = [
        item["magnitude"]
        for item in earthquakes
        if isinstance(item.get("magnitude"), (int, float))
    ]
    depths = [
        item["depth_km"]
        for item in earthquakes
        if isinstance(item.get("depth_km"), (int, float))
    ]

    largest = max(
        earthquakes,
        key=lambda item: item["magnitude"]
        if isinstance(item.get("magnitude"), (int, float))
        else float("-inf"),
        default=None,
    )

    return {
        "count": len(earthquakes),
        "average_magnitude": round(mean(magnitudes), 2) if magnitudes else None,
        "maximum_magnitude": max(magnitudes) if magnitudes else None,
        "average_depth_km": round(mean(depths), 2) if depths else None,
        "largest_location": largest["location"] if largest else None,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/earthquakes")
def earthquakes_api():
    try:
        earthquakes = fetch_earthquakes()
        return jsonify({"earthquakes": earthquakes})
    except requests.RequestException as exc:
        return jsonify({"error": f"Unable to contact USGS: {exc}"}), 502


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
        return jsonify({"error": "Download data first to create the CSV file."}), 404

    return send_file(
        CSV_PATH.resolve(),
        as_attachment=True,
        download_name="earthquakes.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)

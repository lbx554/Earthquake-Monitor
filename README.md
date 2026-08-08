# Earthquake Monitor

## Project Description

Earthquake Monitor is a Python web application that retrieves recent earthquake
information from the United States Geological Survey (USGS). The application
allows users to browse earthquakes reported around the world during the past day,
search earthquake events by location, save the collected data locally, perform
statistical analysis, and view earthquake visualizations.

The project uses Flask to provide a web interface and Python libraries including
Requests, pandas, NumPy, and Matplotlib for data retrieval, organization,
analysis, and visualization.

---

## Features

- Retrieve recent earthquake data from the USGS GeoJSON earthquake feed
- Display earthquake events from around the world
- Search earthquake records by location
- Refresh the displayed earthquake data
- View earthquake magnitude, depth, location, and time
- Save earthquake records locally in CSV format
- Download the saved CSV file
- Calculate earthquake statistics using pandas and NumPy
- View detailed information for individual earthquake events
- Generate Matplotlib visualizations of earthquake data

---

## Technologies Used

### Backend

- Python 3
- Flask
- Requests
- pandas
- NumPy
- Matplotlib

### Frontend

- HTML
- CSS
- JavaScript

### Data Source

Earthquake data is retrieved from the United States Geological Survey (USGS)
GeoJSON earthquake feed.

The application currently uses the USGS feed containing earthquakes reported
during the past day. Although USGS is a United States government agency, the
feed contains earthquake events from around the world.

---

## Project Components

### Web Interface

Earthquake Monitor uses Flask to provide an interactive web interface. The
project satisfies the interface requirements through multiple user-facing pages
and more than four interactive widgets.

#### Interface 1: Main Earthquake Monitor Page

The main page is the primary interface for viewing and interacting with recent
earthquake data.

It displays:

- Total number of recent earthquakes
- Average earthquake magnitude
- Largest earthquake magnitude
- Average earthquake depth
- A table of recent earthquake events
- Magnitude, location, depth, and time for each earthquake

Users can also search, refresh, save, and download earthquake information from
this page.

Route:

```text
/
```

#### Interface 2: Earthquake Detail Page

Selecting an earthquake from the main page opens a second user-facing
interface for that specific earthquake.

The detail page displays:

- Earthquake location
- Magnitude
- Depth
- Latitude
- Longitude
- Recorded time
- Statistical comparisons with other earthquakes in the current feed
- A Matplotlib visualization comparing the selected earthquake with other
  recent events

The page also provides navigation back to the main interface.

Route:

```text
/earthquake/<event_id>
```

For example, if an earthquake has an event ID of `ci12345678`, its page would
use a route similar to:

```text
/earthquake/ci12345678
```

The event IDs come directly from the current USGS earthquake feed.

#### Interactive Widgets

The main interface contains at least four widgets that allow the user to
gather, update, and interact with the earthquake data.

| Widget | Purpose |
| --- | --- |
| **Refresh Data button** | Retrieves and displays the latest earthquake information from the USGS feed |
| **Search field** | Filters the displayed earthquake records by location |
| **Save CSV button** | Saves the current earthquake dataset locally as `data/earthquakes.csv` |
| **Download CSV button** | Downloads the previously saved earthquake CSV file |
| **Earthquake detail links** | Allow users to select an earthquake and open its individual detail and visualization page |

Therefore, the application provides two separate user-facing interfaces and
more than the four interactive widgets required for the project.

---

### Web Data Access

The application retrieves recent earthquake information from the USGS GeoJSON
earthquake feed using Python's Requests library.

USGS returns the earthquake information in GeoJSON format. The application
extracts the information needed for each earthquake, including:

- Event ID
- Magnitude
- Location
- Depth
- Longitude
- Latitude
- Time
- USGS event URL

The feed is publicly accessible and does not require the user to manually enter
earthquake information.

---

### Data Organization

After retrieving the earthquake information, the application organizes the
records into a pandas DataFrame.

Each earthquake is stored using structured fields such as:

| Field | Description |
| --- | --- |
| `id` | Unique USGS earthquake event ID |
| `magnitude` | Magnitude of the earthquake |
| `location` | Reported earthquake location |
| `depth_km` | Depth of the earthquake in kilometers |
| `longitude` | Geographic longitude |
| `latitude` | Geographic latitude |
| `time_utc` | Time of the event in UTC |
| `details_url` | Link to additional USGS information |

Users can save the current dataset locally as:

```text
data/earthquakes.csv
```

The CSV file provides a structured local copy of the retrieved earthquake data
that can be used for later viewing or analysis.

---

### Data Analysis

The application uses pandas and NumPy to analyze the earthquake dataset.

The overall statistical analysis includes:

- Total number of earthquakes
- Average magnitude
- Median magnitude
- Largest magnitude
- Magnitude percentile
- Average earthquake depth
- Maximum earthquake depth

Individual earthquake analysis can also compare a selected event with other
earthquakes in the current feed.

This provides users with both the original earthquake records and numerical
summaries that make the data easier to interpret.

---

### Data Visualization

Matplotlib is used to generate visualizations of the earthquake data.

The application includes visualizations such as a magnitude distribution
histogram and a scatter plot comparing earthquake magnitude with earthquake
depth.

For the scatter plot:

- Each point represents one earthquake
- The X-axis represents earthquake magnitude
- The Y-axis represents earthquake depth in kilometers

Individual earthquake visualizations can also highlight the selected event so
that its magnitude and depth can be compared with other recent earthquakes.

The visualizations provide a graphical representation of the dataset in addition
to the numerical statistics.

---

## Project Structure

```text
EarthquakeMonitor/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── analysis.html
│   └── earthquake_detail.html
│
├── static/
│   ├── app.js
│   ├── style.css
│   └── generated/
│
└── data/
    └── earthquakes.csv
```

The `data/earthquakes.csv` file and generated visualization images may not exist
until the corresponding features of the application have been used.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lbx554/Earthquake-Monitor.git
cd Earthquake-Monitor
```

### 2. Create a Virtual Environment

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The required Python packages include:

- Flask
- Requests
- pandas
- NumPy
- Matplotlib

---

## Running the Application

After installing the dependencies, start the Flask application:

```bash
python app.py
```

Depending on the system configuration, you may instead use:

```bash
python3 app.py
```

Flask will start a local development server.

Open a web browser and visit:

```text
http://127.0.0.1:5000/
```

---

## How to Use

### View Earthquake Data

Open the home page to view earthquakes reported by USGS during the past day.

The table displays information including:

- Magnitude
- Location
- Depth
- Time

### Search Earthquakes

Enter a location in the search field to filter the displayed earthquake
records.

### Refresh Data

Select **Refresh Data** to retrieve and display the latest earthquake
information.

### Save Earthquake Data

Select **Save CSV** to retrieve the current earthquake records and save them
locally as:

```text
data/earthquakes.csv
```

### Download the CSV

After creating the CSV file, select **Download CSV** to download the saved
earthquake dataset.

### View an Individual Earthquake

Select an earthquake from the main interface to open its detail page.

The detail page provides additional information, statistical comparisons, and a
visualization for the selected earthquake.

---

## Application Routes

| Route | Purpose |
| --- | --- |
| `/` | Main Earthquake Monitor interface |
| `/earthquake/<event_id>` | Details and analysis for an individual earthquake |
| `/api/earthquakes` | Returns recent earthquake records as JSON |
| `/api/statistics` | Returns calculated earthquake statistics |
| `/api/earthquakes/<event_id>` | Returns data and statistics for an individual earthquake |
| `/api/download` | Retrieves and saves the current dataset as CSV |
| `/download/csv` | Downloads the saved CSV file |

---

## Dependencies

The project dependencies are listed in `requirements.txt`:

```text
Flask
requests
pandas
numpy
matplotlib
```

Install all dependencies with:

```bash
python -m pip install -r requirements.txt
```

---

## Limitations

The application currently uses the USGS earthquake feed for events reported
during the past day. Because this is live data, the earthquakes displayed by the
application will change over time.

The application also requires an internet connection when retrieving new
earthquake information from USGS.

CSV files and generated graphs are created locally when their corresponding
features are used.

---

## Author

Nagi Ebeid

- Web data access
- Data organization
- Data analysis
- Data visualization
- Application's interface
- Testing, documentation, and presentation

---

## Acknowledgments

Earthquake information is provided by the United States Geological Survey
(USGS).
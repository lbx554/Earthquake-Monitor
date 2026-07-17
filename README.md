# Earthquake Monitor

## Authors
- Nagi Ebeid

---

## Project Description

Earthquake Monitor is a Python application that retrieves real-time earthquake data from the United States Geological Survey (USGS). Users will be able to search and view recent earthquake events through a graphical interface. The application will organize the downloaded data into local files for future analysis. Statistical analysis will be performed on earthquake information such as magnitude, depth, and frequency over time. The project will also generate visualizations that help users understand earthquake patterns around the world.

---

## Project Outline / Plan

Our project will include the following components:

- Build a graphical user interface using Tkinter.
- Retrieve recent earthquake data from the USGS online earthquake feed.
- Store earthquake data in CSV format.
- Analyze earthquake statistics such as average magnitude and daily earthquake counts.
- Generate graphs that visualize earthquake trends.
- Allow users to refresh and update earthquake information.

---

## Interface Plan

The application will use a Tkinter graphical user interface consisting of two windows.

### Main Window
- Display project title
- "Download Earthquake Data" button
- "View Statistics" button
- "Generate Graph" button
- "Exit" button

### Statistics Window
- Display earthquake summary
- Average magnitude
- Largest earthquake
- Number of earthquakes
- Option to display graphs

Widgets include:
- Buttons
- Labels
- Text area
- Scrollable list
- Pop-up window

---

## Data Collection and Storage Plan

The application will retrieve earthquake data from the USGS Earthquake API using Python's requests library. Information including earthquake magnitude, location, depth, date, and time will be extracted from the returned JSON data. The collected data will then be organized into a CSV file using the pandas library. Each execution of the program can either overwrite the previous dataset or save a new timestamped file for historical analysis. Storing the data locally will allow future analysis without requiring another internet connection.

---

## Data Analysis and Visualization Plan

The stored earthquake data will be analyzed using pandas and NumPy. The program will calculate statistics including average magnitude, maximum magnitude, average depth, and the number of earthquakes recorded each day. Visualization will be created using Matplotlib. Planned graphs include a histogram of earthquake magnitudes, a scatter plot comparing magnitude and depth, and a time-series graph showing earthquake frequency over time. These visualizations will help users identify trends and patterns in recent earthquake activity.

---

## Future Improvements

- TBA

---

## License

MIT Licensee
let earthquakes = [];

const tableBody = document.querySelector("#earthquake-table");
const searchInput = document.querySelector("#search-input");
const message = document.querySelector("#message");

function formatNumber(value, decimals = 2) {
    return typeof value === "number" ? value.toFixed(decimals) : "N/A";
}

function renderEarthquakes(items) {
    tableBody.innerHTML = "";

    if (items.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4">No matching earthquakes found.</td>
            </tr>
        `;
        return;
    }

    for (const earthquake of items) {
        const row = document.createElement("tr");
        const time = earthquake.time_utc
            ? new Date(earthquake.time_utc).toLocaleString()
            : "Unknown";
        const internalDetailsUrl =
            `/earthquake/${encodeURIComponent(earthquake.id)}`;

        row.innerHTML = `
            <td class="magnitude">${formatNumber(earthquake.magnitude, 1)}</td>
            <td>
                <a href="${internalDetailsUrl}">
                    ${earthquake.location}
                </a>
            </td>
            <td>${formatNumber(earthquake.depth_km, 1)} km</td>
            <td>${time}</td>
        `;
        tableBody.appendChild(row);
    }
}

async function loadData() {
    tableBody.innerHTML = `<tr><td colspan="4">Loading…</td></tr>`;
    message.textContent = "";

    try {
        const [eventsResponse, statsResponse] = await Promise.all([
            fetch("/api/earthquakes"),
            fetch("/api/statistics"),
        ]);

        const eventsData = await eventsResponse.json();
        const statsData = await statsResponse.json();

        if (!eventsResponse.ok) {
            throw new Error(eventsData.error || "Unable to load earthquakes.");
        }
        if (!statsResponse.ok) {
            throw new Error(statsData.error || "Unable to load statistics.");
        }

        earthquakes = eventsData.earthquakes;
        renderEarthquakes(earthquakes);

        document.querySelector("#count").textContent = statsData.count;
        document.querySelector("#average-magnitude").textContent =
            formatNumber(statsData.average_magnitude);
        document.querySelector("#maximum-magnitude").textContent =
            formatNumber(statsData.maximum_magnitude, 1);
        document.querySelector("#average-depth").textContent =
            `${formatNumber(statsData.average_depth_km)} km`;
        document.querySelector("#largest-location").textContent =
            `Largest event: ${statsData.largest_location || "N/A"}`;
    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td class="error-row" colspan="4">${error.message}</td>
            </tr>
        `;
    }
}

searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const filtered = earthquakes.filter((earthquake) =>
        earthquake.location.toLowerCase().includes(query)
    );
    renderEarthquakes(filtered);
});

document.querySelector("#refresh-button").addEventListener("click", loadData);

document.querySelector("#save-button").addEventListener("click", async () => {
    message.textContent = "Saving…";

    try {
        const response = await fetch("/api/download", { method: "POST" });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to save the CSV file.");
        }

        message.textContent =
            `${data.message} ${data.records} records were written to ${data.file}.`;
    } catch (error) {
        message.textContent = error.message;
    }
});

loadData();

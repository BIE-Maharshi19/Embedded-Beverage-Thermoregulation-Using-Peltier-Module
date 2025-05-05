Chart.register(window['chartjs-plugin-annotation']);
Chart.register(ChartDataLabels);

async function submitTemp() {
  const tempInputEl = document.getElementById('targetTemp');
  const unit = document.getElementById('tempUnit').value;
  const tooltipEl = document.getElementById('tempTooltip');

  const rawValue = tempInputEl.value.trim();
  if (!rawValue) {
    tooltipEl.textContent = "Please enter a temperature.";
    tooltipEl.style.display = "block";
    return;
  }

  const tempVal = parseFloat(rawValue);
  if (isNaN(tempVal)) {
    tooltipEl.textContent = "Please enter a valid number.";
    tooltipEl.style.display = "block";
    return;
  }

  let celsiusTemp = tempVal;
  if (unit === 'F') {
    celsiusTemp = (tempVal - 32) * 5 / 9;
  }

  if (celsiusTemp < 15 || celsiusTemp > 38) {
    tooltipEl.textContent = "Temperature must be between 15°C and 38°C.";
    tooltipEl.style.display = "block";
    return;
  }

  tooltipEl.style.display = "none";

  const payload = { target_temp: celsiusTemp };
  try {
    const res = await fetch('/api/set-temp', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    alert(result.message || "Submitted successfully");
    tempInputEl.value = "";
  } catch (err) {
    console.error("Failed to send input:", err);
    alert("Error sending data");
  }
}

function updateTempPreview() {
  const tempInputEl = document.getElementById('targetTemp');
  const unit = document.getElementById('tempUnit').value;
  const previewEl = document.getElementById('tempPreview');

  const raw = tempInputEl.value.trim();
  const val = parseFloat(raw);
  if (!raw || isNaN(val)) {
    previewEl.style.display = 'none';
    return;
  }

  if (unit === 'F') {
    const c = (val - 32) * 5 / 9;
    previewEl.textContent = `Converted to Celsius: ${c.toFixed(1)}°C`;
  } else {
    const f = (val * 9) / 5 + 32;
    previewEl.textContent = `Converted to Fahrenheit: ${f.toFixed(1)}°F`;
  }
  previewEl.style.display = 'block';
}

async function fetchAndRenderChart() {
  const sessionFilter = document.getElementById("sessionFilter")?.value ?? "all";
  const modeFilter = document.getElementById("modeFilter")?.value ?? "all";

  let rawData = [];

  try {
    const res = await fetch('/api/user-inputs');
    rawData = await res.json();
    console.log("Raw Data from DB:", rawData);
  } catch (error) {
    console.error("Failed to fetch data:", error);
    return;
  }

  const allSessions = new Set();
  const sessionToModes = {};

  const drinkTempData = [];
  const stopAnnotations = [];
  const preferredTemps = { HEATING: [], COOLING: [] };
  const sessionEndTimes = {};
  const performanceBySession = {};

  rawData.forEach(entry => {
    const sessionId = entry.session_id || "unknown";
    const mode = entry.mode || "UNKNOWN";
    const timestamp = new Date(entry.timestamp);

    allSessions.add(sessionId);
    if (!sessionToModes[sessionId]) sessionToModes[sessionId] = new Set();
    sessionToModes[sessionId].add(mode);

    if (!performanceBySession[sessionId]) {
      performanceBySession[sessionId] = {
        start: null,
        startTemp: null,
        end: null,
        endTemp: null,
        mode: mode
      };
    }

    if (entry.user_action === 'SET') {
      drinkTempData.push({
        x: timestamp,
        y: entry.drink_temp,
        mode,
        session_id: sessionId
      });

      performanceBySession[sessionId].start = timestamp;
      performanceBySession[sessionId].startTemp = entry.drink_temp;
      performanceBySession[sessionId].endTemp = entry.target_temp;
      performanceBySession[sessionId].mode = mode;

      if (mode === 'HEATING' || mode === 'COOLING') {
        preferredTemps[mode].push(entry.target_temp);
      }
    }

    if (entry.user_action === 'STOP') {
      performanceBySession[sessionId].end = timestamp;
      sessionEndTimes[sessionId] = entry.timestamp;
    }
  });

  // Load Session Filter
  const sessionFilterEl = document.getElementById("sessionFilter");
  if (sessionFilterEl && sessionFilterEl.options.length <= 1) {
    allSessions.forEach(sessionId => {
      const option = document.createElement("option");
      option.value = sessionId;
      option.textContent = sessionId;
      sessionFilterEl.appendChild(option);
    });
  }

  // Update Mode Filter based on Session
  const modeFilterEl = document.getElementById("modeFilter");
  if (sessionFilter !== "all" && sessionToModes[sessionFilter]) {
    const modes = Array.from(sessionToModes[sessionFilter]);
    modeFilterEl.innerHTML = `<option value="all">All Modes</option>`;
    modes.forEach(mode => {
      const option = document.createElement("option");
      option.value = mode;
      option.textContent = mode;
      modeFilterEl.appendChild(option);
    });
  }

  Object.entries(sessionEndTimes).forEach(([sessionId, ts]) => {
    stopAnnotations.push({
      type: 'line',
      xMin: ts,
      xMax: ts,
      borderColor: '#888',
      borderDash: [4, 4],
      borderWidth: 1,
      label: {
        display: true,
        content: `STOP: ${sessionId}`,
        position: 'end',
        backgroundColor: '#888',
        color: '#fff',
        font: { size: 10 }
      }
    });
  });

  const ctx = document.getElementById('tempChart').getContext('2d');
  if (window.chart) window.chart.destroy();

  // Drink Temp Over Time Chart
  window.chart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: "Drink Temp",
          data: drinkTempData,
          parsing: false,
          borderColor: '#1d242d',
          pointBackgroundColor: drinkTempData.map(d =>
            d.mode === 'HEATING' ? '#f74b38' : d.mode === 'COOLING' ? '#3c93c4' : '#aaa'
          ),
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 5,
          pointHoverRadius: 6,
          showLine: true
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'nearest', intersect: false },
      plugins: {
        title: {
          display: true,
          text: "Drink Temp Over Time (All Sessions)",
          font: { size: 20 }
        },
        tooltip: {
          callbacks: {
            label: context => {
              const point = drinkTempData[context.dataIndex];
              return `${point.mode} | ${point.y}°C`;
            }
          }
        },
        annotation: { annotations: stopAnnotations },
        datalabels: { display: false }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'day',
            tooltipFormat: 'yyyy-MM-dd HH:mm:ss',
            displayFormats: { day: 'yyyy-MM-dd' }
          },
          title: { display: true, text: 'Session Date' }
        },
        y: {
          title: { display: true, text: 'Drink Temp (°C)' }
        }
      }
    },
    plugins: [window['chartjs-plugin-annotation']]
  });

  // Hardware Performance Chart
  const perfLabels = [];
  const perfDurations = [];
  const perfDetails = [];

  for (const session in performanceBySession) {
    const { start, end, startTemp, endTemp, mode } = performanceBySession[session];

    if (sessionFilter !== "all" && session !== sessionFilter) continue;
    if (modeFilter !== "all" && mode !== modeFilter) continue;

    if (start && end) {
      const durationMin = ((new Date(end) - new Date(start)) / 60000).toFixed(2);
      perfLabels.push(session);
      perfDurations.push(durationMin);
      perfDetails.push(`${mode}: ${startTemp}°C → ${endTemp}°C`);
    }
  }

  const perfCtx = document.getElementById('performanceChart')?.getContext('2d');
  if (perfCtx) {
    if (window.performanceChart?.destroy) window.performanceChart.destroy();
    window.performanceChart = new Chart(perfCtx, {
      type: 'bar',
      data: {
        labels: perfLabels,
        datasets: [{
          label: 'Duration (minutes)',
          data: perfDurations,
          backgroundColor: '#F5A623'
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const idx = context.dataIndex;
                return `Duration: ${context.raw} min (${perfDetails[idx]})`;
              }
            }
          },
          datalabels: {
            align: 'center',
            anchor: 'center',
            formatter: (value, context) => perfDetails[context.dataIndex],
            color: '#fff',
            font: { weight: 'bold' }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            title: { display: true, text: 'Duration (minutes)' }
          }
        }
      },
      plugins: [ChartDataLabels]
    });
  }

  // Temperature Preferences Chart
  const avg = arr => arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1) : null;

  let heating = preferredTemps.HEATING;
  let cooling = preferredTemps.COOLING;

  if (sessionFilter !== "all" || modeFilter !== "all") {
    heating = rawData.filter(d =>
      d.mode === 'HEATING' &&
      d.user_action === 'SET' &&
      (sessionFilter === "all" || d.session_id === sessionFilter)
    ).map(d => d.target_temp);

    cooling = rawData.filter(d =>
      d.mode === 'COOLING' &&
      d.user_action === 'SET' &&
      (sessionFilter === "all" || d.session_id === sessionFilter)
    ).map(d => d.target_temp);
  }

  const heatingAvg = avg(heating);
  const coolingAvg = avg(cooling);

  const prefCtx = document.getElementById('preferencesChart')?.getContext('2d');
  if (prefCtx && (heatingAvg !== null || coolingAvg !== null)) {
    if (window.preferenceChart?.destroy) window.preferenceChart.destroy();
    window.preferenceChart = new Chart(prefCtx, {
      type: 'bar',
      data: {
        labels: ['HEATING', 'COOLING'],
        datasets: [{
          label: 'Avg Target Temp (°C)',
          data: [heatingAvg ?? 0, coolingAvg ?? 0],
          backgroundColor: ['#f74b38', '#3c93c4']
        }]
      },
      options: {
        plugins: {
          title: { display: true, text: 'User Temperature Preferences' },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}°C`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Temperature (°C)' }
          }
        }
      }
    });
  }
}

window.onload = fetchAndRenderChart;

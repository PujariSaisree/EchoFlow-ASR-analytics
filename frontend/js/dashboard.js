mountLayout("/");

function renderKpis(totals) {
  const cards = [
    ["Total recordings", totals.total_recordings ?? 0, "Stored locally in SQLite"],
    ["Average duration", fmtSeconds(totals.average_duration), "Length of processed interactions"],
    ["Average WPM", fmtNumber(totals.average_wpm), "Detected speaking rate"],
    ["Average silence", fmtPercent(totals.average_silence_ratio), "Share of non-transcribed time"],
  ];
  document.getElementById("kpis").innerHTML = cards.map(([label, value, note]) => `
    <article class="card">
      <div class="kpi-label">${label}</div>
      <div class="kpi-value">${value}</div>
      <div class="kpi-note">${note}</div>
    </article>
  `).join("");
}

function lineChart(id, labels, data, color) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{ data, borderColor: color, backgroundColor: color + "22", fill: true, tension: 0.3 }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

async function loadDashboard() {
  const data = await API.overview();
  renderKpis(data.totals || {});
  const series = data.series || [];
  const labels = series.map((item) => `#${item.id}`);
  lineChart("wpmChart", labels, series.map((item) => item.wpm), "#0f6e67");
  lineChart("silenceChart", labels, series.map((item) => item.silence_ratio), "#c47b2b");
  const recent = data.recent || [];
  const root = document.getElementById("recent");
  if (!recent.length) {
    root.innerHTML = `<div class="empty">No recordings yet. Upload audio from Transcriptions to populate this overview.</div>`;
    return;
  }
  root.innerHTML = `
    <table>
      <thead>
        <tr><th>File</th><th>Duration</th><th>Words</th><th>WPM</th><th>Model</th><th>Date</th></tr>
      </thead>
      <tbody>
        ${recent.map((item) => `
          <tr>
            <td><a href="/transcriptions?id=${item.id}">${item.filename}</a></td>
            <td>${fmtSeconds(item.duration)}</td>
            <td>${item.word_count ?? "—"}</td>
            <td>${fmtNumber(item.wpm)}</td>
            <td>${item.model || "—"}</td>
            <td>${(item.created_at || "").slice(0, 19).replace("T", " ")}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

loadDashboard().catch((error) => {
  document.getElementById("recent").innerHTML = `<div class="error">${error.message}</div>`;
});

mountLayout("/speech-analytics");
let chart;

async function populatePicker() {
  const data = await API.recordings();
  const picker = document.getElementById("picker");
  const items = data.items || [];
  if (!items.length) {
    document.getElementById("kpis").innerHTML = `<div class="empty">Process a recording before viewing speech analytics.</div>`;
    return [];
  }
  picker.innerHTML = items.map((item) => `<option value="${item.id}">#${item.id} · ${item.filename}</option>`).join("");
  const current = selectedId();
  if (current) picker.value = current;
  return items;
}

async function render() {
  const id = document.getElementById("picker").value;
  if (!id) return;
  const payload = await API.recording(id);
  const rec = payload.recording;
  const a = payload.analytics || {};
  const t = payload.transcript || {};
  document.getElementById("kpis").innerHTML = [
    ["Duration", fmtSeconds(rec.duration), "How long was the interaction?"],
    ["WPM", fmtNumber(a.wpm), "How quickly was speech delivered?"],
    ["Speech ratio", fmtPercent(a.speech_ratio), "What proportion contained detected speech?"],
    ["Silence ratio", fmtPercent(a.silence_ratio), "How much of the recording contained silence?"],
    ["Questions", a.question_count ?? "—", "How frequently were questions used?"],
    ["Segments", t.segment_count ?? "—", "How fragmented was the transcript?"],
    ["Words", t.word_count ?? "—", "How much speech content was captured?"],
    ["RTF", fmtNumber(rec.rtf, 2), "How efficiently did ASR process the recording?"],
  ].map(([label, value, q]) => `
    <article class="card">
      <div class="kpi-label">${label}</div>
      <div class="kpi-value">${value}</div>
      <div class="kpi-note">${q}</div>
    </article>
  `).join("");

  document.getElementById("perf").innerHTML = `
    <p>Processing time: <strong>${fmtNumber(rec.processing_time, 2)} s</strong></p>
    <p>Real-time factor: <strong>${fmtNumber(rec.rtf, 2)}</strong></p>
    <p>Model: <strong>${rec.model || "—"}</strong></p>
    <p>Language: <strong>${rec.language || "—"}</strong></p>
  `;

  const ctx = document.getElementById("behaviorChart");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Speech", "Silence", "Questions", "Segments"],
      datasets: [{
        data: [a.speech_ratio || 0, a.silence_ratio || 0, a.question_count || 0, t.segment_count || 0],
        backgroundColor: ["#0f6e67", "#c47b2b", "#172033", "#9b3d3d"],
      }],
    },
    options: { plugins: { legend: { display: false } } },
  });
}

document.getElementById("picker").onchange = render;
populatePicker().then(render).catch((error) => {
  document.getElementById("kpis").innerHTML = `<div class="error">${error.message}</div>`;
});

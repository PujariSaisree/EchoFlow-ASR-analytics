mountLayout("/transcriptions");

const statusEl = () => document.getElementById("status");

async function loadHistory() {
  const data = await API.recordings();
  const items = data.items || [];
  const root = document.getElementById("history");
  if (!items.length) {
    root.innerHTML = `<div class="empty">No stored recordings yet.</div>`;
    return;
  }
  root.innerHTML = items.map((item) => `
    <div class="segment">
      <div><a href="/transcriptions?id=${item.id}">#${item.id}</a></div>
      <div>
        <strong>${item.filename}</strong>
        <div class="muted">${fmtSeconds(item.duration)} · ${item.word_count ?? 0} words · ${item.model || ""}</div>
      </div>
    </div>
  `).join("");
}

function renderDetail(payload) {
  const rec = payload.recording;
  const transcript = payload.transcript || {};
  const segments = payload.segments || [];
  const player = document.getElementById("player");
  if (rec.original_path) {
    player.src = `/api/recordings/${rec.id}/audio`;
    player.hidden = false;
  }
  document.getElementById("detail").innerHTML = `
    <div class="toolbar">
      <h3 style="margin:0">${rec.filename}</h3>
      <span class="badge">${rec.model || ""}</span>
      <span class="badge">${rec.language || "language unknown"}</span>
      <button class="btn ghost" id="copy">Copy</button>
      <a class="btn ghost" href="/api/recordings/${rec.id}/export?format=txt">TXT</a>
      <a class="btn ghost" href="/api/recordings/${rec.id}/export?format=json">JSON</a>
      <a class="btn ghost" href="/api/recordings/${rec.id}/export?format=srt">SRT</a>
      <a class="btn ghost" href="/api/recordings/${rec.id}/export?format=vtt">VTT</a>
      <button class="btn danger" id="remove">Delete</button>
    </div>
    <p class="muted">${fmtSeconds(rec.duration)} · ${transcript.word_count ?? 0} words · ${transcript.character_count ?? 0} characters</p>
    <h4>Full transcript</h4>
    <p id="full-text">${transcript.full_text || "No speech was detected."}</p>
    <h4>Timestamped segments</h4>
    ${segments.map((seg) => `
      <div class="segment">
        <div class="muted">${fmtNumber(seg.start_time, 2)}–${fmtNumber(seg.end_time, 2)} s</div>
        <div>${seg.text}</div>
      </div>
    `).join("") || `<div class="empty">No segments.</div>`}
  `;
  document.getElementById("copy").onclick = async () => {
    await navigator.clipboard.writeText(transcript.full_text || "");
    statusEl().textContent = "Transcript copied.";
  };
  document.getElementById("remove").onclick = async () => {
    await API.deleteRecording(rec.id);
    window.location.href = "/transcriptions";
  };
}

async function openSelected() {
  const id = selectedId();
  if (!id) return;
  const payload = await API.recording(id);
  renderDetail(payload);
}

document.getElementById("upload").onclick = async () => {
  const file = document.getElementById("file").files[0];
  if (!file) {
    statusEl().innerHTML = `<span class="error">Choose an audio file first.</span>`;
    return;
  }
  statusEl().textContent = "Validating and transcribing locally. The first model load can take longer.";
  try {
    const model = document.getElementById("model").value;
    const payload = await API.upload(file, model);
    window.location.href = `/transcriptions?id=${payload.recording.id}`;
  } catch (error) {
    statusEl().innerHTML = `<div class="error">${error.message}</div>`;
  }
};

Promise.all([loadHistory(), openSelected()]).catch((error) => {
  statusEl().innerHTML = `<div class="error">${error.message}</div>`;
});

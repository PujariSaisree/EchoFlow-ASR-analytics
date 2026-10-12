mountLayout("/model-evaluation");

async function populatePicker() {
  const data = await API.recordings();
  const items = data.items || [];
  document.getElementById("picker").innerHTML = items.map((item) => `<option value="${item.id}">#${item.id} · ${item.filename}</option>`).join("");
}

document.getElementById("run").onclick = async () => {
  const id = document.getElementById("picker").value;
  const reference = document.getElementById("reference").value;
  const root = document.getElementById("results");
  try {
    const result = await API.evaluate(id, reference);
    root.innerHTML = `
      <p>Audio duration: <strong>${fmtSeconds(result.audio_duration)}</strong></p>
      <p>Processing time: <strong>${fmtNumber(result.processing_time, 2)} s</strong></p>
      <p>RTF: <strong>${fmtNumber(result.rtf, 2)}</strong></p>
      <p>Model: <strong>${result.model || "—"}</strong></p>
      <p>WER: <strong>${result.wer === null ? (result.message || "—") : fmtNumber(result.wer, 3)}</strong></p>
      <p>CER: <strong>${result.cer === null ? (result.message || "—") : fmtNumber(result.cer, 3)}</strong></p>
    `;
  } catch (error) {
    root.innerHTML = `<div class="error">${error.message}</div>`;
  }
};

populatePicker().catch((error) => {
  document.getElementById("results").innerHTML = `<div class="error">${error.message}</div>`;
});

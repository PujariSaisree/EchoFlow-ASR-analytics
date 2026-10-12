mountLayout("/settings");

async function load() {
  const data = await API.settings();
  const select = document.getElementById("model");
  select.innerHTML = (data.allowed_models || []).map((item) => {
    const selected = item === data.default_model ? "selected" : "";
    return `<option ${selected} value="${item}">${item}</option>`;
  }).join("");
  const privacy = data.privacy || {};
  document.getElementById("privacy").innerHTML = `
    <p>Audio processing: <strong>${privacy.audio_processing}</strong></p>
    <p>Speech recognition: <strong>${privacy.asr}</strong></p>
    <p>Storage: <strong>${privacy.storage}</strong></p>
    <p>External speech APIs: <strong>${privacy.external_speech_apis ? "enabled" : "disabled"}</strong></p>
    <p class="muted">Stored locally: original upload, 16 kHz mono WAV, transcript, segments, keywords, and computed KPIs.</p>
  `;
}

document.getElementById("save").onclick = async () => {
  try {
    await API.saveSettings(document.getElementById("model").value);
    document.getElementById("status").textContent = "Default model saved.";
  } catch (error) {
    document.getElementById("status").innerHTML = `<div class="error">${error.message}</div>`;
  }
};

load().catch((error) => {
  document.getElementById("status").innerHTML = `<div class="error">${error.message}</div>`;
});

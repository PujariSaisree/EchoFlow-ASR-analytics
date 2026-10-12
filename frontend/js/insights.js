mountLayout("/business-insights");

async function populatePicker() {
  const data = await API.recordings();
  const picker = document.getElementById("picker");
  const items = data.items || [];
  picker.innerHTML = items.map((item) => `<option value="${item.id}">#${item.id} · ${item.filename}</option>`).join("");
  const current = selectedId();
  if (current) picker.value = current;
  return items;
}

async function render() {
  const id = document.getElementById("picker").value;
  if (!id) {
    document.getElementById("findings").innerHTML = `<div class="empty">No recording selected.</div>`;
    return;
  }
  const payload = await API.recording(id);
  const insights = payload.insights || {};
  const findings = insights.findings || [];
  document.getElementById("findings").innerHTML = findings.length ? findings.map((item) => `
    <div class="insight">
      <strong>${item.title}</strong>
      <p>${item.statement}</p>
      <div class="muted">${item.business_question || ""}</div>
    </div>
  `).join("") : `<div class="empty">${insights.summary || "Insufficient data."}</div>`;
  const review = insights.review_areas || [];
  document.getElementById("review").innerHTML = review.length
    ? review.map((item) => `<p>${item}</p>`).join("")
    : `<p class="muted">No additional review flags were generated from the current thresholds.</p>`;
  const keywords = payload.keywords || [];
  document.getElementById("keywords").innerHTML = keywords.length
    ? keywords.map((item) => `<span class="badge">${item.keyword} · ${item.frequency}</span> `).join("")
    : `<p class="muted">No keywords extracted.</p>`;
}

document.getElementById("picker").onchange = render;
document.getElementById("ask").onclick = async () => {
  const id = document.getElementById("picker").value;
  const question = document.getElementById("question").value;
  try {
    const result = await API.ask(id, question);
    const note = result.sufficient_data ? "" : " The available data was insufficient for a complete answer.";
    document.getElementById("answer").textContent = (result.answer || "") + note;
  } catch (error) {
    document.getElementById("answer").innerHTML = `<div class="error">${error.message}</div>`;
  }
};

populatePicker().then(render).catch((error) => {
  document.getElementById("findings").innerHTML = `<div class="error">${error.message}</div>`;
});

const API = {
  async request(path, options = {}) {
    const response = await fetch(path, options);
    const isJson = (response.headers.get("content-type") || "").includes("application/json");
    const payload = isJson ? await response.json() : await response.text();
    if (!response.ok) {
      const message = payload && payload.error ? payload.error : "The request failed.";
      throw new Error(message);
    }
    return payload;
  },
  health() { return this.request("/api/health"); },
  overview() { return this.request("/api/dashboard/overview"); },
  recordings() { return this.request("/api/recordings"); },
  recording(id) { return this.request(`/api/recordings/${id}`); },
  deleteRecording(id) {
    return this.request(`/api/recordings/${id}`, { method: "DELETE" });
  },
  upload(file, model) {
    const body = new FormData();
    body.append("file", file);
    if (model) body.append("model", model);
    return this.request("/api/recordings/upload", { method: "POST", body });
  },
  ask(id, question) {
    return this.request(`/api/recordings/${id}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  },
  evaluate(id, reference) {
    return this.request(`/api/evaluation/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reference_transcript: reference }),
    });
  },
  settings() { return this.request("/api/settings"); },
  saveSettings(default_model) {
    return this.request("/api/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ default_model }),
    });
  },
};

function fmtNumber(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

function fmtSeconds(value) {
  if (value === null || value === undefined) return "—";
  if (value < 60) return `${fmtNumber(value, 1)} s`;
  return `${fmtNumber(value / 60, 1)} min`;
}

function fmtPercent(value) {
  if (value === null || value === undefined) return "—";
  return `${fmtNumber(value * 100, 1)}%`;
}

function selectedId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

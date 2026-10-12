function mountLayout(active) {
  const template = document.getElementById("page-template");
  const pageContent = template ? template.content.cloneNode(true) : null;
  const links = [
    ["/", "Dashboard"],
    ["/transcriptions", "Transcriptions"],
    ["/speech-analytics", "Speech Analytics"],
    ["/model-evaluation", "Model Evaluation"],
    ["/business-insights", "Business Insights"],
    ["/settings", "Settings"],
  ];
  const nav = links.map(([href, label]) => {
    const isActive = href === active ? "active" : "";
    return `<a class="${isActive}" href="${href}">${label}</a>`;
  }).join("");

  document.body.innerHTML = `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="mark">Ef</div>
          <div>
            <h1>EchoFlow</h1>
            <p>Speech analytics</p>
          </div>
        </div>
        <nav class="nav">${nav}</nav>
      </aside>
      <main class="content" id="page-root"></main>
    </div>
  `;
  const root = document.getElementById("page-root");
  if (pageContent && root) root.appendChild(pageContent);
}

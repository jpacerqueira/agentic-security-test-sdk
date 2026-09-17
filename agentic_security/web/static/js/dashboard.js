const runId = window.AS_RUN_ID;
const strip = document.getElementById("phase-strip");
const reportList = document.getElementById("report-list");
const reportFrame = document.getElementById("report-frame");
const artifactList = document.getElementById("artifact-list");

function markPhase(phase, status) {
  const pill = strip.querySelector(`[data-phase="${phase}"]`);
  if (!pill) return;
  pill.classList.remove("running", "done", "open", "rejected");
  pill.classList.add(status);
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("on"));
    tab.classList.add("on");
    document.querySelectorAll(".pane").forEach((p) => p.classList.add("hidden"));
    document.getElementById(`pane-${tab.dataset.tab}`).classList.remove("hidden");
    if (tab.dataset.tab === "reports") refreshReports();
  });
});

function refreshReports() {
  fetch(`/runs/${runId}/reports`)
    .then((r) => r.json())
    .then((data) => {
      reportList.innerHTML = "";
      (data.files || []).forEach((f) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.textContent = f;
        btn.addEventListener("click", () => {
          reportFrame.src = `/runs/${runId}/files/${f}`;
        });
        li.appendChild(btn);
        reportList.appendChild(li);
      });
      if ((data.files || [])[0]) reportFrame.src = `/runs/${runId}/files/${data.files[0]}`;
    });
}

const es = new EventSource(`/runs/${runId}/events`);
es.onmessage = (msg) => {
  const ev = JSON.parse(msg.data);
  if (ev.kind === "phase_started") markPhase(ev.phase, "running");
  if (ev.kind === "gate_opened") {
    markPhase(ev.phase, "open");
    document.getElementById(`gate-${ev.payload.gate_id}`)?.classList.add("open");
  }
  if (ev.kind === "gate_resolved") {
    const card = document.getElementById(`gate-${ev.payload.gate_id}`);
    if (card) {
      card.classList.remove("open");
      card.classList.add("resolved");
    }
    markPhase(ev.phase, ev.payload.decision === "rejected" ? "rejected" : "done");
  }
  if (ev.kind === "artifact") {
    const li = document.createElement("li");
    li.innerHTML = `<a href="/runs/${runId}/files/${ev.payload.key}">${ev.payload.key}</a>`;
    artifactList.appendChild(li);
    markPhase(ev.phase, "done");
  }
  if (ev.kind === "llm_wait") markPhase("scope", "running");
  if (ev.kind === "pipeline_completed") {
    markPhase("done", "done");
    markPhase("writer", "done");
    refreshReports();
  }
};

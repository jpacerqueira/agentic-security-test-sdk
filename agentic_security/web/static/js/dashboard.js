const runId = window.AS_RUN_ID;
const skipLlm = window.AS_SKIP_LLM;
const strip = document.getElementById("phase-strip");
const reportList = document.getElementById("report-list");
const reportFrame = document.getElementById("report-frame");
const artifactList = document.getElementById("artifact-list");
const pdfBtn = document.getElementById("btn-output-pdf");

function modeLabel() {
  return skipLlm ? "Deterministic" : "LLM (Ollama / ADK LiteLLM)";
}

function setRunStatus(state, detail) {
  const el = document.getElementById("run-status");
  if (!el) return;
  el.classList.remove("running", "completed", "stopped");
  el.classList.add(state);
  const label = el.querySelector(".run-status-label");
  if (!label) return;
  if (state === "completed") label.textContent = `Completed — ${modeLabel()}`;
  else if (state === "stopped") label.textContent = `Stopped — ${detail || "rejected"}`;
  else label.textContent = `Running — ${modeLabel()}`;
}

function markPhase(phase, status) {
  const pill = strip.querySelector(`[data-phase="${phase}"]`);
  if (!pill) return;
  pill.classList.remove("running", "done", "open", "rejected");
  pill.classList.add(status);
  if (status === "running" || status === "open") {
    const pills = [...strip.querySelectorAll(".phase-pill")];
    const idx = pills.indexOf(pill);
    pills.slice(0, Math.max(0, idx)).forEach((p) => {
      if (!p.classList.contains("rejected") && !p.classList.contains("done")) {
        p.classList.remove("running", "open");
        p.classList.add("done");
      }
    });
  }
  updateProgress();
}

function updateProgress() {
  const fill = document.getElementById("run-progress-fill");
  const bar = document.getElementById("run-progress-bar");
  const count = document.getElementById("run-progress-count");
  const step = document.getElementById("run-progress-step");
  if (!strip || !fill) return;
  const pills = [...strip.querySelectorAll(".phase-pill")];
  const total = pills.length || 1;
  const done = pills.filter((p) => p.classList.contains("done") || p.classList.contains("rejected")).length;
  const current = pills.find((p) => p.classList.contains("running") || p.classList.contains("open"));
  const visual = done + (current ? 0.45 : 0);
  const pct = Math.min(100, Math.round((visual / total) * 100));
  fill.style.width = `${pct}%`;
  fill.classList.toggle("open", Boolean(current && current.classList.contains("open")));
  if (bar) bar.setAttribute("aria-valuenow", String(done));
  if (count) count.textContent = `${done} / ${total}`;
  if (step) {
    if (done === total) step.textContent = "Complete";
    else if (current) step.textContent = current.textContent.trim();
    else step.textContent = "Waiting";
  }
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
      if (pdfBtn) pdfBtn.disabled = !(data.files || []).length;
    });
}

pdfBtn?.addEventListener("click", () => {
  pdfBtn.disabled = true;
  pdfBtn.textContent = "Building A4 PDF…";
  fetch(`/runs/${runId}/output-report.pdf`)
    .then((r) => {
      if (!r.ok) throw new Error("pdf failed");
      return r.blob();
    })
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${runId}-output-report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    })
    .catch(() => {
      alert("Output report is not ready yet. Approve Gate 6 and wait for HTML reports.");
    })
    .finally(() => {
      pdfBtn.disabled = false;
      pdfBtn.textContent = "Generate output report";
    });
});

const es = new EventSource(`/runs/${runId}/events`);
es.onmessage = (msg) => {
  const ev = JSON.parse(msg.data);
  if (ev.kind === "phase_started") {
    markPhase(ev.phase, "running");
    setRunStatus("running");
  }
  if (ev.kind === "gate_opened") {
    markPhase(ev.phase, "open");
    document.getElementById(`gate-${ev.payload.gate_id}`)?.classList.add("open");
    setRunStatus("running");
  }
  if (ev.kind === "gate_resolved") {
    const card = document.getElementById(`gate-${ev.payload.gate_id}`);
    if (card) {
      card.classList.remove("open");
      card.classList.add("resolved");
    }
    markPhase(ev.phase, ev.payload.decision === "rejected" ? "rejected" : "done");
    if (ev.payload.gate_id === "gate_6" && ev.payload.decision !== "rejected") {
      refreshReports();
    }
  }
  if (ev.kind === "artifact") {
    const li = document.createElement("li");
    li.innerHTML = `<a href="/runs/${runId}/files/${ev.payload.key}">${ev.payload.key}</a>`;
    artifactList.appendChild(li);
    markPhase(ev.phase, "done");
  }
  if (ev.kind === "llm_wait") {
    markPhase("scope", "running");
    setRunStatus("running");
  }
  if (ev.kind === "pipeline_completed") {
    markPhase("done", "done");
    markPhase("writer", "done");
    setRunStatus("completed");
    refreshReports();
  }
  if (ev.kind === "pipeline_stopped") {
    setRunStatus("stopped", ev.payload?.reason || "rejected");
  }
};
updateProgress();

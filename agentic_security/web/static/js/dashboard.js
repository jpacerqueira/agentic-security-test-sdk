const runId = window.AS_RUN_ID;
const strip = document.getElementById("phase-strip");
const reportList = document.getElementById("report-list");
const reportFrame = document.getElementById("report-frame");
const artifactList = document.getElementById("artifact-list");
const pdfBtn = document.getElementById("btn-output-pdf");
const modeBox = document.getElementById("run-skip-llm");

modeBox?.addEventListener("change", () => {
  const skip = modeBox.checked;
  const body = new FormData();
  body.set("skip_llm", skip ? "true" : "false");
  fetch(`/runs/${runId}/mode`, { method: "POST", body })
    .then((r) => {
      if (!r.ok) throw new Error("mode");
      return r.json();
    })
    .then((data) => {
      modeBox.checked = !!data.skip_llm;
    })
    .catch(() => {
      modeBox.checked = !skip;
    });
});

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
      alert("Output report is not ready yet. Approve Gate 5 and wait for HTML reports.");
    })
    .finally(() => {
      pdfBtn.disabled = false;
      pdfBtn.textContent = "Generate output report";
    });
});

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
    if (ev.payload.gate_id === "gate_5" && ev.payload.decision !== "rejected") {
      refreshReports();
    }
  }
  if (ev.kind === "artifact") {
    const li = document.createElement("li");
    li.innerHTML = `<a href="/runs/${runId}/files/${ev.payload.key}">${ev.payload.key}</a>`;
    artifactList.appendChild(li);
    markPhase(ev.phase, "done");
  }
  if (ev.kind === "llm_wait") markPhase("scope", "running");
  if (ev.kind === "mode_changed") {
    if (modeBox) modeBox.checked = !!ev.payload.skip_llm;
  }
  if (ev.kind === "pipeline_completed") {
    markPhase("done", "done");
    markPhase("writer", "done");
    refreshReports();
  }
};

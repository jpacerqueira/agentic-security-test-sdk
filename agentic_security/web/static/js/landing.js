document.querySelectorAll(".plan-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".plan-card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");
    document.getElementById("plan-input").value = card.dataset.plan;
    syncGroundingField();
  });
});

const groundingField = document.getElementById("grounding-field");
const groundingBox = document.getElementById("llm-grounding-input");
const groundingHidden = document.getElementById("llm-grounding-hidden");

function syncGroundingField() {
  const ultra = document.getElementById("plan-input")?.value === "ultra-professional";
  if (groundingField) groundingField.hidden = !ultra;
  if (!ultra && groundingBox) groundingBox.checked = false;
  if (groundingHidden) groundingHidden.value = ultra && groundingBox?.checked ? "true" : "false";
}

groundingBox?.addEventListener("change", syncGroundingField);
const firstPlan = document.querySelector(".plan-card");
if (firstPlan) {
  firstPlan.classList.add("selected");
  document.getElementById("plan-input").value = firstPlan.dataset.plan;
}
syncGroundingField();

const picker = document.getElementById("demo-picker");
const sourcePath = document.getElementById("source-path");
const targetUrl = document.getElementById("target-url");
const selectedLabel = document.getElementById("selected-source");

function selectCard(card) {
  picker.querySelectorAll(".demo-card").forEach((c) => c.classList.remove("selected"));
  card.classList.add("selected");
  sourcePath.value = card.dataset.path || "";
  targetUrl.value = card.dataset.githubUrl || "";
  if (selectedLabel) {
    selectedLabel.textContent = `Selected source tree: ${card.dataset.path}`
      + (card.dataset.githubUrl ? ` (from ${card.dataset.githubUrl})` : "");
  }
}

function bindCard(card) {
  card.addEventListener("click", () => selectCard(card));
}

picker.querySelectorAll(".demo-card").forEach(bindCard);

function addExampleCard(ex) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "demo-card";
  btn.dataset.path = ex.path;
  btn.dataset.githubUrl = ex.github_url || "";
  const name = document.createElement("div");
  name.className = "demo-card-name";
  name.textContent = ex.name;
  const hint = document.createElement("p");
  hint.className = "hint";
  hint.textContent = ex.path;
  btn.append(name, hint);
  picker.prepend(btn);
  bindCard(btn);
  selectCard(btn);
}

const fetchForm = document.getElementById("github-fetch-form");
const fetchStatus = document.getElementById("github-fetch-status");
const fetchBtn = document.getElementById("github-fetch-btn");
fetchForm?.addEventListener("submit", (evt) => {
  evt.preventDefault();
  const url = document.getElementById("github-url").value.trim();
  if (!url) {
    fetchStatus.textContent = "Paste a public GitHub repository URL first.";
    return;
  }
  fetchBtn.disabled = true;
  fetchStatus.textContent = "Downloading zip from GitHub…";
  const body = new FormData();
  body.set("github_url", url);
  fetch("/examples/fetch-github", { method: "POST", body })
    .then(async (r) => {
      const data = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.error || "fetch failed");
      return data;
    })
    .then((ex) => {
      fetchStatus.textContent = `Added ${ex.path}. Click Start assessment to analyse this tree.`;
      addExampleCard(ex);
    })
    .catch((err) => {
      fetchStatus.textContent = err.message || "Could not download that repository.";
    })
    .finally(() => {
      fetchBtn.disabled = false;
    });
});

const form = document.querySelector(".demo-form");
const box = document.getElementById("skip-llm-input");
const hidden = document.getElementById("skip-llm-hidden");
const autoBox = document.getElementById("auto-approve-input");
const autoHidden = document.getElementById("auto-approve-hidden");

function syncSkipLlm() {
  if (hidden && box) hidden.value = box.checked ? "true" : "false";
}

function syncAutoApprove() {
  if (autoHidden && autoBox) autoHidden.value = autoBox.checked ? "true" : "false";
}

box?.addEventListener("change", syncSkipLlm);
autoBox?.addEventListener("change", syncAutoApprove);
syncSkipLlm();
syncAutoApprove();

form?.addEventListener("submit", (evt) => {
  syncSkipLlm();
  syncAutoApprove();
  syncGroundingField();
  if (!sourcePath.value) {
    evt.preventDefault();
    if (selectedLabel) selectedLabel.textContent = "Select a source tree card (or download a GitHub zip first).";
    return;
  }
  const skip = hidden ? hidden.value : "true";
  if (skip === "true" || form.dataset.llmConfirmed === "1") return;
  evt.preventDefault();
  const panel = form.querySelector(".llm-confirm-inline");
  const submitBtn = form.querySelector('button[type="submit"]');
  if (!panel) {
    form.dataset.llmConfirmed = "1";
    form.submit();
    return;
  }
  panel.hidden = false;
  if (submitBtn) submitBtn.hidden = true;
  const confirmBtn = panel.querySelector('[data-modal-action="confirm"]');
  const cancelBtn = panel.querySelector('[data-modal-action="cancel"]');
  const onConfirm = () => {
    panel.hidden = true;
    if (submitBtn) submitBtn.hidden = false;
    form.dataset.llmConfirmed = "1";
    confirmBtn.removeEventListener("click", onConfirm);
    cancelBtn.removeEventListener("click", onCancel);
    form.requestSubmit();
  };
  const onCancel = () => {
    panel.hidden = true;
    if (submitBtn) submitBtn.hidden = false;
    confirmBtn.removeEventListener("click", onConfirm);
    cancelBtn.removeEventListener("click", onCancel);
  };
  confirmBtn.addEventListener("click", onConfirm);
  cancelBtn.addEventListener("click", onCancel);
});

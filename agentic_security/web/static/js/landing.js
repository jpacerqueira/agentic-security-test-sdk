document.querySelectorAll(".plan-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".plan-card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");
    document.getElementById("plan-input").value = card.dataset.plan;
  });
});
document.querySelector(".plan-card")?.classList.add("selected");

document.querySelectorAll(".demo-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".demo-card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");
    document.getElementById("source-path").value = card.dataset.path;
  });
});
document.querySelector(".demo-card")?.click();

const form = document.querySelector(".demo-form");
const box = document.getElementById("skip-llm-input");
const hidden = document.getElementById("skip-llm-hidden");

function syncSkipLlm() {
  if (hidden && box) hidden.value = box.checked ? "true" : "false";
}

box?.addEventListener("change", syncSkipLlm);
syncSkipLlm();

form?.addEventListener("submit", (evt) => {
  syncSkipLlm();
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

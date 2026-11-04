"use strict";

const form = document.querySelector("#logout-form");
const button = form.querySelector("button");
const error = document.querySelector("#logout-error");
const status = document.querySelector("#logout-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (button.disabled) return;
  button.disabled = true;
  form.setAttribute("aria-busy", "true");
  error.textContent = "";
  status.textContent = "Déconnexion en cours…";
  try {
    const response = await fetch(form.action, {
      method: "POST",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "X-CSRFToken": form.elements.csrfmiddlewaretoken.value,
      },
      body: new FormData(form),
    });
    const result = await response.json();
    if (!response.ok) {
      error.textContent = result.error || "Déconnexion impossible. Réessaie.";
      error.focus();
      return;
    }
    window.location.assign(result.redirect);
  } catch {
    error.textContent = "Déconnexion non confirmée. Recharge la page puis réessaie.";
    error.focus();
  } finally {
    button.disabled = false;
    form.removeAttribute("aria-busy");
    if (error.textContent) status.textContent = "";
  }
});

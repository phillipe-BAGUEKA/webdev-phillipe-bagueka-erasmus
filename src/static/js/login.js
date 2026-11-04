"use strict";

const form = document.querySelector("#login-form");
const button = form.querySelector("button");
const error = document.querySelector("#login-error");
const status = document.querySelector("#login-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (button.disabled) return;
  button.disabled = true;
  form.setAttribute("aria-busy", "true");
  error.textContent = "";
  status.textContent = "Connexion en cours…";
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
      error.textContent = result.error || "Connexion impossible. Réessaie.";
      form.elements.password.value = "";
      error.focus();
      return;
    }
    status.textContent = "Connexion réussie. Ouverture des laboratoires…";
    window.location.assign(result.redirect);
  } catch {
    error.textContent = "Connexion interrompue. Vérifie ta connexion et réessaie.";
    error.focus();
  } finally {
    button.disabled = false;
    form.removeAttribute("aria-busy");
    if (error.textContent) status.textContent = "";
  }
});

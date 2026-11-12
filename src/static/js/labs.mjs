"use strict";

import { createBookingJourney } from "./booking.mjs?v=1";

export function createCatalogue(document, fetcher, onSelect = null) {
  const section = document.querySelector("#laboratory-catalogue");
  const status = document.querySelector("#labs-status");
  const error = document.querySelector("#labs-error");
  const list = document.querySelector("#labs-list");
  const retry = document.querySelector("#labs-retry");
  const login = document.querySelector("#labs-login");
  let loading = false;

  async function load() {
    if (loading) return;
    loading = true;
    section.setAttribute("aria-busy", "true");
    retry.disabled = true;
    error.textContent = "";
    status.textContent = "Chargement des laboratoires…";
    login.hidden = true;
    list.hidden = true;
    list.replaceChildren();
    try {
      const response = await fetcher("/api/labs", {
        method: "GET",
        credentials: "same-origin",
        mode: "same-origin",
        cache: "no-store",
        headers: { "Accept": "application/json" },
      });
      if (response.status === 401) {
        status.textContent = "";
        error.textContent = "Ta session a expiré ou n’est plus valide. Reconnecte-toi.";
        login.hidden = false;
        return;
      }
      if (!response.ok) {
        status.textContent = "";
        error.textContent = "Impossible de charger les laboratoires. Réessaie.";
        return;
      }
      const payload = await response.json();
      if (!Array.isArray(payload.laboratories) || !payload.laboratories.every(
        (lab) => lab && Number.isInteger(lab.id) && typeof lab.name === "string"
      )) {
        throw new Error("Invalid catalogue response");
      }
      for (const lab of payload.laboratories) {
        const item = document.createElement("li");
        item.textContent = lab.name;
        if (onSelect) {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = `Voir les disponibilités — ${lab.name}`;
          button.addEventListener("click", () => onSelect(lab));
          item.append(button);
        }
        list.append(item);
      }
      list.hidden = payload.laboratories.length === 0;
      status.textContent = payload.laboratories.length === 0
        ? "Aucun laboratoire n’est enregistré pour le moment."
        : `${payload.laboratories.length} laboratoire(s) affiché(s).`;
    } catch {
      status.textContent = "";
      error.textContent = "Chargement interrompu ou réponse illisible. Vérifie ta connexion et réessaie.";
    } finally {
      loading = false;
      retry.disabled = false;
      retry.hidden = !error.textContent;
      section.removeAttribute("aria-busy");
    }
  }

  retry.addEventListener("click", load);
  return { load };
}

if (typeof document !== "undefined") {
  const fetcher = window.fetch.bind(window);
  const journey = document.querySelector("#booking-journey")
    ? createBookingJourney(document, fetcher) : null;
  createCatalogue(document, fetcher, journey ? (lab) => journey.selectLaboratory(lab) : null).load();
  if (journey) journey.loadHistory();
}

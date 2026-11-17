"use strict";

const sofiaDate = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Sofia", dateStyle: "medium", timeStyle: "short",
});

export function slotLabel(slot) {
  try {
    return `${sofiaDate.format(new Date(slot.starts_at))} – ${sofiaDate.format(new Date(slot.ends_at))}`;
  } catch {
    throw new Error("Les horaires reçus sont illisibles. Réessaie la consultation.");
  }
}

export function createBookingJourney(document, fetcher) {
  const node = (id) => document.querySelector(`#${id}`);
  const root = node("booking-journey");
  const availability = node("availability");
  const title = node("availability-title");
  const day = node("booking-date");
  const dateForm = node("availability-form");
  const slots = node("slots-list");
  const status = node("availability-status");
  const historyStatus = node("history-status");
  const history = node("bookings-list");
  const feedback = node("booking-feedback");
  const login = node("booking-login");
  const confirm = node("booking-confirm");
  const selection = node("booking-selection");
  const refresh = node("history-refresh");
  const loadButton = node("availability-load");
  const aiForm = node("ai-form");
  const aiNeed = node("ai-need");
  const aiButton = node("ai-request");
  const aiStatus = node("ai-status");
  let laboratory = null;
  let selected = null;
  let selectedSource = null;
  let aiPending = false;
  let aiRevision = 0;
  let busy = false;
  let uncertain = false;
  let sessionLost = false;
  let historyLoading = false;
  let generation = 0;
  let slotButtons = [];
  let cancelButtons = [];

  function controls() {
    confirm.disabled = busy || historyLoading || uncertain || sessionLost || !selected;
    loadButton.disabled = busy || sessionLost;
    day.disabled = busy || sessionLost;
    refresh.disabled = busy || historyLoading || sessionLost;
    aiButton.disabled = aiPending || busy || historyLoading || uncertain || sessionLost || !laboratory;
    aiNeed.disabled = busy || sessionLost;
    for (const button of [...slotButtons, ...cancelButtons]) {
      button.disabled = busy || historyLoading || uncertain || sessionLost;
    }
  }

  function message(text, error = false) {
    feedback.textContent = text;
    feedback.className = error ? "error message" : "success message";
    if (error) feedback.focus();
  }

  async function request(url, method = "GET", body = undefined) {
    const headers = { Accept: "application/json" };
    if (method === "POST") {
      headers["Content-Type"] = "application/json";
      headers["X-CSRFToken"] = node("booking-csrf").value;
    }
    let response;
    try {
      response = await fetcher(url, {
        method, mode: "same-origin", credentials: "same-origin", cache: "no-store",
        headers, ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      });
    } catch {
      throw new Error("Erreur réseau. Vérifie ta connexion puis réessaie la consultation.");
    }
    if (response.status === 401) {
      sessionLost = true;
      login.hidden = false;
      invalidateAi("Ta session a expiré. Reconnecte-toi avec le lien proposé.", true);
      controls();
      throw new Error("Ta session a expiré. Reconnecte-toi avec le lien proposé.");
    }
    let payload;
    try { payload = await response.json(); }
    catch { throw new Error("Réponse illisible. Consulte à nouveau l'état actuel."); }
    return { response, payload };
  }

  function clearSelection() {
    selected = null;
    selectedSource = null;
    selection.hidden = true;
    node("booking-summary").textContent = "";
    controls();
  }

  function invalidateAi(text = "", error = false) {
    ++aiRevision;
    aiStatus.textContent = text || (aiPending ? "La réponse précédente sera ignorée. Le choix manuel reste disponible." : "");
    aiStatus.className = error ? "error message" : "message";
    if (selectedSource === "ai") clearSelection();
  }

  function selectSlot(slot, source) {
    selected = slot;
    selectedSource = source;
    selection.hidden = false;
    node("booking-summary").textContent = `${source === "ai" ? "Suggestion IA — " : ""}${slot.workstation_name} — ${slotLabel(slot)} (Europe/Sofia)`;
    controls();
    confirm.focus();
  }

  async function suggest() {
    if (aiPending || busy || historyLoading || uncertain || sessionLost || !laboratory) return;
    invalidateAi();
    const need = aiNeed.value.trim();
    if (!need || need.length > 1000) {
      aiStatus.textContent = "Décris ton besoin en 1 à 1 000 caractères.";
      aiStatus.className = "error message";
      aiNeed.focus();
      return;
    }
    if (!day.value) {
      aiStatus.textContent = "Choisis une date avant de demander une suggestion.";
      day.focus();
      return;
    }
    const revision = aiRevision;
    aiPending = true;
    controls();
    aiForm.setAttribute("aria-busy", "true");
    aiStatus.textContent = "Demande de suggestion IA en cours… Le choix manuel reste disponible.";
    try {
      const { response, payload } = await request(`/api/labs/${laboratory.id}/suggestion`, "POST", {
        date: day.value, need,
      });
      if (revision !== aiRevision) return;
      if (!response.ok) {
        const messages = {
          not_configured: "La suggestion IA est désactivée ou non configurée. Choisis manuellement.",
          quota: "Le quota de suggestion IA est atteint. Choisis manuellement.",
          provider_error: "La suggestion IA est indisponible. Choisis manuellement.",
          timeout: "La suggestion IA a dépassé le délai. Choisis manuellement.",
          invalid_output: "La réponse de suggestion IA est invalide. Choisis manuellement.",
          candidate_unavailable: "Ce créneau n'est plus disponible. Consulte les choix manuels.",
        };
        const fallback = response.status === 403
          ? "Vérification de sécurité ou autorisation refusée. Recharge la page."
          : response.status === 422 ? "Vérifie ton besoin et la date, ou choisis manuellement."
            : response.status === 504 ? messages.timeout : messages.provider_error;
        throw new Error(typeof payload?.code === "string" && Object.hasOwn(messages, payload.code)
          ? messages[payload.code] : fallback);
      }
      if (response.status === 200 && payload?.status === "no_candidates" && payload.candidate === null) {
        aiStatus.textContent = "Aucun créneau réservable pour cette recherche. Consulte les disponibilités manuelles ou change de date.";
        return;
      }
      const slot = payload?.candidate;
      if (response.status !== 200 || payload?.status !== "suggested" || !slot
          || !Number.isSafeInteger(slot.workstation_id) || slot.workstation_id <= 0
          || typeof slot.workstation_name !== "string" || !slot.workstation_name.trim()
          || typeof slot.starts_at !== "string" || !Number.isFinite(Date.parse(slot.starts_at))
          || typeof slot.ends_at !== "string" || !Number.isFinite(Date.parse(slot.ends_at))) {
        throw new Error("Réponse de suggestion IA invalide. Choisis manuellement.");
      }
      aiStatus.textContent = `Suggestion IA : ${slot.workstation_name} — ${slotLabel(slot)}. Rien n'est réservé : vérifie le poste et le créneau avant de confirmer.`;
      aiStatus.className = "success message";
      selectSlot(slot, "ai");
    } catch (error) {
      if (revision === aiRevision) {
        aiStatus.textContent = error.message;
        aiStatus.className = "error message";
      }
    } finally {
      aiPending = false;
      aiForm.removeAttribute("aria-busy");
      controls();
    }
  }

  async function loadSlots() {
    if (!laboratory || busy || sessionLost) return;
    const current = ++generation;
    invalidateAi();
    clearSelection();
    slotButtons = [];
    slots.replaceChildren();
    status.textContent = "Chargement des disponibilités…";
    availability.setAttribute("aria-busy", "true");
    try {
      const { response, payload } = await request(
        `/api/labs/${laboratory.id}/availability?date=${encodeURIComponent(day.value)}`,
      );
      if (current !== generation) return;
      if (!response.ok) throw new Error(payload.error || "Disponibilités indisponibles. Réessaie.");
      if (!Array.isArray(payload.slots)) throw new Error("Réponse illisible. Réessaie.");
      for (const slot of payload.slots) {
        const item = document.createElement("li");
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = `${slot.workstation_name} — ${slotLabel(slot)}`;
        button.addEventListener("click", () => {
          if (busy || uncertain || sessionLost) return;
          invalidateAi();
          selectSlot(slot, "manual");
        });
        slotButtons.push(button);
        item.append(button);
        slots.append(item);
      }
      status.textContent = payload.slots.length
        ? `${payload.slots.length} créneau(x) réservable(s). Choisis puis confirme.`
        : "Aucun créneau réservable pour cette date et ton compte. Choisis une autre date ou consulte tes réservations.";
      controls();
    } catch (error) {
      if (current === generation) status.textContent = error.message || "Erreur réseau. Réessaie avec Afficher les créneaux.";
    } finally {
      if (current === generation) availability.removeAttribute("aria-busy");
    }
  }

  async function loadHistory() {
    if (busy || historyLoading || sessionLost) return;
    historyLoading = true;
    controls();
    node("personal-bookings").setAttribute("aria-busy", "true");
    historyStatus.textContent = "Chargement de tes réservations…";
    history.replaceChildren();
    cancelButtons = [];
    try {
      const { response, payload } = await request("/api/bookings");
      if (!response.ok) throw new Error(payload.error || "Historique indisponible. Réessaie.");
      if (!Array.isArray(payload.bookings)) throw new Error("Historique illisible. Réessaie.");
      for (const row of payload.bookings) {
        const item = document.createElement("li");
        const text = document.createElement("p");
        const names = { future: "À venir", in_progress: "En cours", past: "Passée", cancelled: "Annulée" };
        text.textContent = `${row.laboratory_name} · ${row.workstation_name} — ${slotLabel(row)} · ${names[row.status] || row.status} · Poste ${row.is_operational ? "en service" : "hors service"}`;
        item.append(text);
        if (row.status === "future" && row.cancelled_at === null) {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = `Annuler la réservation du ${slotLabel(row)} — ${row.workstation_name}`;
          button.addEventListener("click", () => mutate("cancel", row));
          cancelButtons.push(button);
          item.append(button);
        }
        history.append(item);
      }
      uncertain = false;
      historyStatus.textContent = payload.bookings.length
        ? `${payload.bookings.length} réservation(s), historique compris.`
        : "Tu n'as aucune réservation. Choisis un laboratoire pour commencer.";
    } catch (error) {
      historyStatus.textContent = error.message || "Erreur réseau. Consulte à nouveau l'état actuel.";
    } finally {
      historyLoading = false;
      node("personal-bookings").removeAttribute("aria-busy");
      controls();
    }
  }

  async function mutate(kind, row) {
    if (busy || historyLoading || uncertain || sessionLost) return;
    busy = true;
    invalidateAi();
    ++generation;
    availability.removeAttribute("aria-busy");
    if (laboratory) status.textContent = "Disponibilités à actualiser après cette demande.";
    controls();
    root.setAttribute("aria-busy", "true");
    message(kind === "create" ? "Réservation en cours…" : "Annulation en cours…");
    let successful = false;
    try {
      const body = kind === "create"
        ? { workstation_id: row.workstation_id, starts_at: row.starts_at, ends_at: row.ends_at }
        : {};
      const { response, payload } = await request(
        kind === "create" ? "/api/bookings" : `/api/bookings/${row.id}/cancel`, "POST", body,
      );
      if (!response.ok) {
        message(response.status === 403
          ? "Vérification de sécurité ou autorisation refusée. Recharge la page avant de réessayer."
          : payload.error || "La demande a été refusée. Consulte l'état actuel.", true);
        return;
      }
      if (response.status !== (kind === "create" ? 201 : 200) || !Number.isInteger(payload.booking?.id)) {
        throw new Error("Unconfirmed mutation");
      }
      successful = true;
      clearSelection();
      message(kind === "create" ? "Réservation confirmée. Consulte Mes réservations." : "Réservation annulée ; elle reste dans ton historique.");
      feedback.focus();
    } catch {
      clearSelection();
      if (sessionLost) message("Session expirée. Reconnecte-toi avec le lien proposé.", true);
      else {
        uncertain = true;
        message("Résultat non confirmé : la demande a pu être enregistrée. Ne la renvoie pas ; consulte l'état actuel dans Mes réservations.", true);
      }
    } finally {
      busy = false;
      root.removeAttribute("aria-busy");
      controls();
    }
    if (successful) {
      await loadHistory();
      await loadSlots();
    }
  }

  dateForm.addEventListener("submit", (event) => { event.preventDefault(); return loadSlots(); });
  function changeDate() {
    ++generation;
    invalidateAi();
    availability.removeAttribute("aria-busy");
    clearSelection();
    slots.replaceChildren();
    status.textContent = "Affiche les créneaux pour la nouvelle date.";
  }
  day.addEventListener("input", changeDate);
  day.addEventListener("change", changeDate);
  aiForm.addEventListener("submit", (event) => { event.preventDefault(); return suggest(); });
  aiNeed.addEventListener("input", () => invalidateAi());
  confirm.addEventListener("click", () => selected ? mutate("create", selected) : undefined);
  node("booking-dismiss").addEventListener("click", () => { invalidateAi(); clearSelection(); });
  refresh.addEventListener("click", loadHistory);
  return {
    loadHistory, loadSlots, mutate,
    selectLaboratory(lab) {
      if (busy) return;
      laboratory = lab;
      invalidateAi();
      ++generation;
      availability.removeAttribute("aria-busy");
      availability.hidden = false;
      node("availability-nav").hidden = false;
      title.textContent = `Disponibilités — ${lab.name}`;
      status.textContent = "Choisis une date puis affiche les créneaux.";
      slots.replaceChildren();
      clearSelection();
      day.focus();
    },
  };
}

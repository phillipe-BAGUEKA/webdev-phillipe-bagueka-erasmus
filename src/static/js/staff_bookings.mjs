import { slotLabel } from "./booking.mjs?v=2";

const statusNames = {
  future: "À venir",
  in_progress: "En cours",
  past: "Passée",
  cancelled: "Annulée",
};

function bookingItem(document, booking) {
  if (!booking || typeof booking.laboratory_name !== "string"
      || typeof booking.workstation_name !== "string"
      || typeof booking.starts_at !== "string" || typeof booking.ends_at !== "string"
      || !Number.isSafeInteger(booking.owner_id) || booking.owner_id < 1
      || typeof booking.status !== "string" || !Object.hasOwn(statusNames, booking.status)) {
    throw new Error("Invalid staff booking response");
  }
  const item = document.createElement("li");
  const title = document.createElement("h3");
  const slot = document.createElement("p");
  const state = document.createElement("p");
  const owner = document.createElement("p");
  title.textContent = `${booking.laboratory_name} · ${booking.workstation_name}`;
  slot.textContent = `Créneau : ${slotLabel(booking)}`;
  state.textContent = `État : ${statusNames[booking.status]}`;
  owner.textContent = `Propriétaire : compte nº ${booking.owner_id}`;
  item.append(title, slot, state, owner);
  return item;
}

export function createStaffBookings(document, fetcher) {
  const node = (name) => document.querySelector(`#staff-bookings-${name}`);
  const status = node("status");
  const error = node("error");
  const results = node("results");
  const list = node("list");
  const retry = node("retry");
  const login = node("login");
  let loading = false;

  async function load() {
    if (loading) return;
    loading = true;
    retry.setAttribute("aria-disabled", "true");
    results.setAttribute("aria-busy", "true");
    results.tabIndex = -1;
    login.hidden = true;
    list.replaceChildren();
    error.textContent = "";
    status.textContent = "Chargement des réservations…";
    let canRetry = false;
    let feedback = status;
    try {
      const response = await fetcher("/api/staff/bookings", {
        method: "GET",
        credentials: "same-origin",
        mode: "same-origin",
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (response.status === 401 || response.status === 403) {
        status.textContent = "";
        login.hidden = response.status !== 401;
        feedback = login.hidden ? error : login;
        error.textContent = login.hidden
          ? "Cette consultation est réservée au personnel."
          : "Ta session a expiré ou n’est plus valide. Reconnecte-toi.";
        return;
      }
      if (!response.ok) throw new Error("Staff bookings request failed");
      const { bookings } = await response.json();
      if (!Array.isArray(bookings)) throw new Error("Invalid staff bookings response");
      const items = document.createDocumentFragment();
      for (const booking of bookings) items.append(bookingItem(document, booking));
      list.append(items);
      results.tabIndex = bookings.length ? 0 : -1;
      status.textContent = bookings.length
        ? `Réservations affichées : ${bookings.length}.`
        : "Aucune réservation à afficher.";
    } catch {
      status.textContent = "";
      error.textContent = "Impossible de charger les réservations. Réessaie.";
      canRetry = true;
    } finally {
      loading = false;
      results.removeAttribute("aria-busy");
      retry.removeAttribute("aria-disabled");
      if (!canRetry && document.activeElement === retry) feedback.focus();
      retry.hidden = !canRetry;
    }
  }

  retry.addEventListener("click", load);
  return { load };
}

if (typeof document !== "undefined") {
  createStaffBookings(document, window.fetch.bind(window)).load();
}

import { createBookingJourney } from "../src/static/js/booking.mjs?v=2";

export function setupJourney(fetcher) {
  const make = () => ({
    textContent: "", hidden: false, disabled: false, children: [], attributes: {},
    value: "2030-01-07", focused: false,
    set innerHTML(value) { throw new Error("HTML insertion forbidden"); },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    replaceChildren() { this.children = []; },
    append(item) { this.children.push(item); },
    addEventListener(name, handler) { this[name] = handler; },
    focus() { this.focused = true; },
  });
  const ids = ["booking-journey", "availability", "availability-title", "booking-date",
    "availability-form", "slots-list", "availability-status", "history-status", "bookings-list",
    "booking-feedback", "booking-login", "booking-confirm", "booking-selection", "history-refresh",
    "availability-load", "personal-bookings", "booking-summary", "booking-dismiss", "booking-csrf",
    "availability-nav", "laboratory-catalogue", "labs-status", "labs-error", "labs-list", "labs-retry", "labs-login",
    "ai-form", "ai-need", "ai-request", "ai-status"];
  const nodes = Object.fromEntries(ids.map((id) => [id, make()]));
  nodes["booking-csrf"].value = "isolated-test-csrf";
  nodes["ai-need"].value = "";
  const document = { querySelector: (selector) => nodes[selector.slice(1)], createElement: make };
  return { nodes, journey: createBookingJourney(document, fetcher), document };
}

export const slot = { workstation_id: 2, workstation_name: "<img src=x onerror=boom>",
  starts_at: "2030-01-07T07:00:00Z", ends_at: "2030-01-07T08:00:00Z" };
export const response = (payload, status = 200) => ({ status, ok: status < 300, json: async () => payload });
export function choose(journey) { journey.selectLaboratory({ id: 3, name: "<b>Laboratoire</b>" }); }
export function submitSuggestion(nodes, need = "Un poste pour travailler") {
  nodes["ai-need"].value = need;
  return nodes["ai-form"].submit({ preventDefault() {} });
}

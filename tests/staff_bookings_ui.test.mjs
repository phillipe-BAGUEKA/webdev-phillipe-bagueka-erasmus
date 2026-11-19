import assert from "node:assert/strict";
import test from "node:test";
import { createStaffBookings } from "../src/static/js/staff_bookings.mjs";

function pageElements() {
  const makeElement = (tag) => ({
    tag, textContent: "", hidden: false, tabIndex: -1, children: [], attributes: {},
    set innerHTML(value) { throw new Error("Bookings must be rendered as text"); },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    replaceChildren() { this.children = []; },
    append(...items) {
      for (const item of items) {
        if (item.tag === "fragment") this.children.push(...item.children);
        else this.children.push(item);
      }
    },
    addEventListener(name, callback) { this[name] = callback; },
    focus() { document.activeElement = this; },
  });
  const nodes = Object.fromEntries(
    ["status", "error", "results", "list", "retry", "login"].map((id) => [id, makeElement(id)]),
  );
  nodes.retry.hidden = true;
  nodes.login.hidden = true;
  const document = {
    activeElement: null,
    querySelector(selector) { return nodes[selector.slice("#staff-bookings-".length)]; },
    createElement(tag) {
      assert.ok(["li", "h3", "p"].includes(tag), "booking rows only contain text elements");
      return makeElement(tag);
    },
    createDocumentFragment() { return makeElement("fragment"); },
  };
  return { nodes, document };
}

function response(payload) {
  return { ok: true, status: 200, json: async () => payload };
}

const winterBooking = {
  id: 3, owner_id: 21, laboratory_name: "<b>Laboratoire nord</b>", workstation_name: "Poste A",
  starts_at: "2027-01-12T06:00:00Z", ends_at: "2027-01-12T07:00:00Z", status: "future",
};
const summerBooking = {
  id: 7, owner_id: 19, laboratory_name: "Laboratoire sud", workstation_name: "Poste B",
  starts_at: "2027-07-12T06:00:00Z", ends_at: "2027-07-12T07:00:00Z", status: "cancelled",
};

test("AC-9 loads once, then shows both owners in response order and Sofia time", async () => {
  const { nodes, document } = pageElements();
  let finish;
  let calls = 0;
  const view = createStaffBookings(document, (url, options) => {
    ++calls;
    assert.equal(url, "/api/staff/bookings");
    assert.deepEqual(options, {
      method: "GET", credentials: "same-origin", mode: "same-origin", cache: "no-store",
      headers: { Accept: "application/json" },
    });
    return new Promise((resolve) => { finish = resolve; });
  });

  const loading = view.load();
  assert.match(nodes.status.textContent, /Chargement des réservations/);
  assert.equal(nodes.results.attributes["aria-busy"], "true");
  await view.load();
  assert.equal(calls, 1);
  finish(response({ bookings: [winterBooking, summerBooking] }));
  await loading;

  const [winter, summer] = nodes.list.children;
  assert.equal(nodes.list.children.length, 2);
  assert.equal(winter.children[0].textContent, "<b>Laboratoire nord</b> · Poste A");
  assert.match(winter.children[1].textContent, /08:00.*09:00/);
  assert.equal(winter.children[2].textContent, "État : À venir");
  assert.equal(winter.children[3].textContent, "Propriétaire : compte nº 21");
  assert.equal(summer.children[0].textContent, "Laboratoire sud · Poste B");
  assert.match(summer.children[1].textContent, /09:00.*10:00/);
  assert.equal(summer.children[2].textContent, "État : Annulée");
  assert.equal(summer.children[3].textContent, "Propriétaire : compte nº 19");
  assert.equal(nodes.status.textContent, "Réservations affichées : 2.");
  assert.equal(nodes.results.tabIndex, 0);
  assert.equal(nodes.results.attributes["aria-busy"], undefined);
  assert.equal(nodes.retry.hidden, true);
});

test("AC-9 the empty result is announced without adding an empty keyboard stop", async () => {
  const { nodes, document } = pageElements();
  await createStaffBookings(document, async () => response({ bookings: [] })).load();
  assert.equal(nodes.status.textContent, "Aucune réservation à afficher.");
  assert.equal(nodes.error.textContent, "");
  assert.equal(nodes.results.tabIndex, -1);
});

for (const [name, failure] of [
  ["HTTP error", () => ({ ok: false, status: 500 })],
  ["network error", () => { throw new Error("Network down"); }],
  ["invalid response shape", () => response({ bookings: "" })],
  ["invalid booking row", () => response({ bookings: [winterBooking, { ...summerBooking, status: "__proto__" }] })],
  ["invalid date", () => response({ bookings: [{ ...winterBooking, starts_at: "bad-date" }] })],
]) {
  test(`AC-9 ${name} clears stale data and offers a repeat consultation`, async () => {
    const { nodes, document } = pageElements();
    nodes.list.children.push({ textContent: "Stale booking" });
    let calls = 0;
    await createStaffBookings(document, async () => {
      return ++calls === 1 ? failure() : response({ bookings: [winterBooking] });
    }).load();
    assert.deepEqual(nodes.list.children, []);
    assert.match(nodes.error.textContent, /Réessaie/);
    assert.equal(nodes.results.tabIndex, -1);
    assert.equal(nodes.retry.hidden, false);
    nodes.retry.focus();
    await nodes.retry.click();
    assert.equal(calls, 2);
    assert.equal(nodes.error.textContent, "");
    assert.equal(nodes.list.children.length, 1);
    assert.equal(nodes.retry.hidden, true);
    assert.equal(document.activeElement, nodes.status);
  });
}

for (const status of [401, 403]) {
  test(`AC-9 ${status} clears the list and distinguishes session and role failures`, async () => {
    const { nodes, document } = pageElements();
    nodes.list.children.push({ textContent: "Stale booking" });
    await createStaffBookings(document, async () => ({ ok: false, status })).load();
    assert.deepEqual(nodes.list.children, []);
    assert.match(nodes.error.textContent, status === 401 ? /session a expiré/ : /réservée au personnel/);
    assert.equal(nodes.login.hidden, status !== 401);
    assert.equal(nodes.retry.hidden, true);
  });
}

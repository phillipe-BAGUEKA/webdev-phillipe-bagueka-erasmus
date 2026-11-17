import assert from "node:assert/strict";
import test from "node:test";
// Match the browser's versioned import so Node measures one module instance.
import { slotLabel } from "../src/static/js/booking.mjs?v=2";
import { createCatalogue } from "../src/static/js/labs.mjs";
import { setupJourney as setup } from "./booking_ui_helpers.mjs";
const slot = { workstation_id: 2, workstation_name: "<img src=x onerror=boom>",
  starts_at: "2030-01-07T07:00:00Z", ends_at: "2030-01-07T08:00:00Z" };
const booking = { ...slot, id: 4, laboratory_name: "<script>lab</script>",
  status: "future", cancelled_at: null, is_operational: false };
const response = (payload, status = 200) => ({ status, ok: status < 300, json: async () => payload });
function choose(journey) { journey.selectLaboratory({ id: 3, name: "<b>Laboratoire</b>" }); }

test("AC-13 AC-40 AC-41 catalogue opens availability, loading and safe DOM text", async () => {
  let finish;
  const { nodes, journey, document } = setup(() => new Promise((resolve) => { finish = resolve; }));
  const catalogue = createCatalogue(document, async () => response({ laboratories: [{ id: 3, name: "<b>Lab</b>" }] }), journey.selectLaboratory);
  await catalogue.load();
  nodes["labs-list"].children[0].children[0].click();
  assert.match(nodes["availability-title"].textContent, /<b>Lab<\/b>/);
  assert.equal(nodes["booking-date"].focused, true);
  const loading = journey.loadSlots();
  assert.match(nodes["availability-status"].textContent, /Chargement/);
  finish(response({ slots: [slot] }));
  await loading;
  assert.match(nodes["slots-list"].children[0].children[0].textContent, /<img/);
  assert.equal(nodes["availability"].attributes["aria-busy"], undefined);
});

test("AC-14 Europe/Sofia display changes winter/summer offset without changing wire timestamps", () => {
  assert.match(slotLabel(slot), /09:00/);
  assert.match(slotLabel({ starts_at: "2030-07-08T07:00:00Z", ends_at: "2030-07-08T08:00:00Z" }), /10:00/);
});

test("AC-13 AC-41 empty, read HTTP failure, retry and outdated response", async () => {
  let mode = "empty";
  const { nodes, journey } = setup(async () => mode === "error"
    ? response({ error: "Date refusée" }, 422) : response({ slots: [] }));
  choose(journey);
  await journey.loadSlots();
  assert.match(nodes["availability-status"].textContent, /Aucun créneau/);
  mode = "error";
  await journey.loadSlots();
  assert.equal(nodes["availability-status"].textContent, "Date refusée");
  mode = "empty";
  await journey.loadSlots();
  assert.match(nodes["availability-status"].textContent, /Aucun/);
  let resolve;
  const pending = setup(() => new Promise((done) => { resolve = done; }));
  choose(pending.journey);
  const loading = pending.journey.loadSlots();
  pending.nodes["booking-date"].change();
  resolve(response({ slots: [slot] }));
  await loading;
  assert.equal(pending.nodes["slots-list"].children.length, 0);
});

test("AC-15 AC-41 explicit confirmation, CSRF, double click blocked, success refreshes without reload", async () => {
  const calls = [];
  let finish;
  const { nodes, journey } = setup(async (url, options) => {
    calls.push([url, options]);
    if (options.method === "POST") return new Promise((resolve) => { finish = resolve; });
    return response(url === "/api/bookings" ? { bookings: [booking] } : { slots: [slot] });
  });
  choose(journey);
  await journey.loadSlots();
  nodes["slots-list"].children[0].children[0].click();
  assert.equal(calls.filter(([, options]) => options.method === "POST").length, 0);
  assert.equal(nodes["booking-selection"].hidden, false);
  const saving = nodes["booking-confirm"].click();
  await nodes["booking-confirm"].click();
  assert.equal(nodes["booking-confirm"].disabled, true);
  const posts = calls.filter(([, options]) => options.method === "POST");
  assert.equal(posts.length, 1);
  assert.equal(posts[0][1].headers["X-CSRFToken"], "isolated-test-csrf");
  assert.deepEqual(JSON.parse(posts[0][1].body), {
    workstation_id: 2, starts_at: slot.starts_at, ends_at: slot.ends_at,
  });
  assert.equal(posts[0][1].credentials, "same-origin");
  finish(response({ booking: { id: 4 } }, 201));
  await saving;
  assert.match(nodes["booking-feedback"].textContent, /confirmée/);
  assert.equal(nodes["bookings-list"].children.length, 1);
  assert.match(nodes["bookings-list"].children[0].children[0].textContent, /hors service/);
  assert.match(nodes["bookings-list"].children[0].children[0].textContent, /<script>/);
  assert.equal(calls.length, 4);
});

for (const message of ["Conflit de poste", "Quota atteint", "Poste hors service", "Annulation trop tardive"]) {
  test(`AC-11 AC-17 AC-20 AC-26 refusal ${message} is readable, not retried`, async () => {
    let posts = 0;
    const { nodes, journey } = setup(async () => { posts++; return response({ error: message }, 409); });
    await journey.mutate("cancel", booking);
    assert.equal(nodes["booking-feedback"].textContent, message);
    assert.equal(posts, 1);
  });
}

test("AC-46 session expired and CSRF failure do not redirect or resend", async () => {
  for (const code of [401, 403]) {
    let calls = 0;
    const { nodes, journey } = setup(async () => { calls++; return response({ error: "Refus" }, code); });
    await journey.mutate("create", slot);
    assert.equal(calls, 1);
    assert.match(nodes["booking-feedback"].textContent, code === 401 ? /Session expirée/ : /sécurité/);
    if (code === 401) {
      assert.equal(nodes["booking-login"].hidden, false);
      assert.equal(nodes["history-refresh"].disabled, true);
      await journey.loadHistory();
      assert.equal(calls, 1);
    }
  }
});

test("AC-15 uncertain mutation never auto retries and requires reading current state", async () => {
  let posts = 0;
  const { nodes, journey } = setup(async (url, options) => {
    if (options.method === "POST") { posts++; throw new Error("Connection interrupted"); }
    return response({ bookings: [booking] });
  });
  await journey.mutate("create", slot);
  await journey.mutate("create", slot);
  assert.equal(posts, 1);
  assert.match(nodes["booking-feedback"].textContent, /a pu être enregistrée/);
  await journey.loadHistory();
  assert.equal(nodes["bookings-list"].children.length, 1);
  assert.equal(posts, 1);
});

test("AC-25 AC-28 history empty/future/past/cancelled and cancellation refresh", async () => {
  let cancelled = false;
  let empty = true;
  const { nodes, journey } = setup(async (url, options) => {
    if (options.method === "POST") { cancelled = true; return response({ booking: { id: 4 } }); }
    return response({ bookings: empty ? [] : [
      { ...booking, status: cancelled ? "cancelled" : "future", cancelled_at: cancelled ? "2030-01-01T00:00:00Z" : null },
      { ...booking, id: 5, status: "past" }, { ...booking, id: 6, status: "in_progress" },
    ] });
  });
  await journey.loadHistory();
  assert.match(nodes["history-status"].textContent, /aucune réservation/);
  empty = false;
  await journey.loadHistory();
  assert.equal(nodes["bookings-list"].children[0].children.length, 2);
  assert.equal(nodes["bookings-list"].children[1].children.length, 1);
  await nodes["bookings-list"].children[0].children[1].click();
  assert.match(nodes["booking-feedback"].textContent, /annulée/);
  assert.match(nodes["bookings-list"].children[0].children[0].textContent, /Annulée/);
});

test("AC-41 read network errors offer retries, no raw stack", async () => {
  const { nodes, journey } = setup(async () => { throw new Error("private network detail"); });
  choose(journey);
  await journey.loadSlots();
  await journey.loadHistory();
  assert.match(nodes["availability-status"].textContent, /réseau/);
  assert.doesNotMatch(nodes["availability-status"].textContent, /private network detail/);
  assert.equal(nodes["history-refresh"].disabled, false);
});

for (const kind of ["json", "shape"]) {
  test(`AC-15 unconfirmed successful mutation ${kind} stays uncertain without retry`, async () => {
    let calls = 0;
    const { nodes, journey } = setup(async () => {
      calls++;
      return kind === "shape" ? response({}, 201)
        : { status: 201, ok: true, json: async () => { throw new Error("private parser detail"); } };
    });
    await journey.mutate("create", slot);
    await journey.mutate("create", slot);
    assert.equal(calls, 1);
    assert.match(nodes["booking-feedback"].textContent, /non confirmé/);
    assert.doesNotMatch(nodes["booking-feedback"].textContent, /private/);
  });
}

test("AC-41 unreadable read responses and dates give a readable retry message", async () => {
  const { nodes, journey } = setup(async () => ({
    status: 200, ok: true, json: async () => { throw new Error("private parse"); },
  }));
  choose(journey);
  await journey.loadSlots();
  assert.match(nodes["availability-status"].textContent, /illisible/);
  assert.doesNotMatch(nodes["availability-status"].textContent, /private/);
  assert.throws(() => slotLabel({ starts_at: "invalid", ends_at: "invalid" }), /illisibles/);
});

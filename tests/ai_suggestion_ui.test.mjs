import assert from "node:assert/strict";
import test from "node:test";
import { setupJourney, slot, response, choose, submitSuggestion } from "./booking_ui_helpers.mjs";

test("AC-29 AC-31 need validation and explicit action only", async () => {
  const calls = [];
  const { journey, nodes } = setupJourney(async (...args) => {
    calls.push(args); return response({ status: "suggested", candidate: slot });
  });
  choose(journey);
  nodes["ai-need"].value = "desk";
  nodes["ai-need"].input();
  assert.equal(calls.length, 0);
  for (const need of [" ", "x".repeat(1001)]) {
    await submitSuggestion(nodes, need);
    assert.match(nodes["ai-status"].textContent, /1 à 1 000/);
    assert.equal(calls.length, 0);
  }
  await submitSuggestion(nodes, "  " + "x".repeat(1000) + "  ");
  assert.equal(calls.length, 1);
  const [url, options] = calls[0];
  assert.equal(url, "/api/labs/3/suggestion");
  assert.deepEqual(JSON.parse(options.body), { date: "2030-01-07", need: "x".repeat(1000) });
  assert.equal(options.headers["X-CSRFToken"], "isolated-test-csrf");
  assert.equal(options.credentials, "same-origin");
});

test("AC-32 AC-34 loading, one request, safe suggestion and explicit existing confirmation", async () => {
  let finish;
  const calls = [];
  const { journey, nodes } = setupJourney(async (url, options) => {
    calls.push([url, options]);
    if (url.endsWith("/suggestion")) return new Promise((resolve) => { finish = resolve; });
    if (options.method === "POST") return response({ booking: { id: 42 } }, 201);
    return response(url === "/api/bookings" ? { bookings: [] } : { slots: [slot] });
  });
  choose(journey);
  const pending = submitSuggestion(nodes);
  await submitSuggestion(nodes);
  assert.equal(calls.length, 1);
  assert.equal(nodes["ai-request"].disabled, true);
  assert.match(nodes["ai-status"].textContent, /en cours/);
  assert.equal(nodes["availability-load"].disabled, false);
  finish(response({ status: "suggested", candidate: slot }));
  await pending;
  assert.match(nodes["ai-status"].textContent, /Suggestion IA/);
  assert.match(nodes["booking-summary"].textContent, /Suggestion IA.*<img/);
  assert.equal(calls.filter(([url]) => url === "/api/bookings").length, 0);
  await nodes["booking-confirm"].click();
  const posts = calls.filter(([url, options]) => url === "/api/bookings" && options.method === "POST");
  assert.equal(posts.length, 1);
  assert.deepEqual(JSON.parse(posts[0][1].body), {
    workstation_id: slot.workstation_id, starts_at: slot.starts_at, ends_at: slot.ends_at,
  });
  assert.match(nodes["booking-feedback"].textContent, /confirmée/);
});

for (const [code, status, message] of [
  ["not_configured", 503, /désactivée|configurée/], ["quota", 503, /quota/i],
  ["provider_error", 503, /indisponible/], ["timeout", 504, /délai/],
  ["invalid_output", 502, /invalide/], ["candidate_unavailable", 409, /disponible/],
  [null, 403, /sécurité|autorisation/], [null, 422, /besoin|date/],
]) {
  test(`AC-33 AC-35 AC-36 readable ${code ?? status}, no retry and manual selection`, async () => {
    const calls = [];
    const { journey, nodes } = setupJourney(async (url, options) => {
      calls.push([url, options]);
      return response(url.endsWith("/suggestion")
        ? { status: "unavailable", candidate: null, code, error: "private raw server detail" }
        : { slots: [slot] }, url.endsWith("/suggestion") ? status : 200);
    });
    choose(journey);
    await submitSuggestion(nodes);
    assert.match(nodes["ai-status"].textContent, message);
    assert.doesNotMatch(nodes["ai-status"].textContent, /private raw/);
    assert.equal(calls.length, 1);
    assert.equal(nodes["ai-request"].disabled, false);
    await journey.loadSlots();
    nodes["slots-list"].children[0].children[0].click();
    assert.equal(nodes["booking-confirm"].disabled, false);
    assert.doesNotMatch(nodes["booking-summary"].textContent, /Suggestion IA/);
  });
}

for (const change of ["laboratory", "date", "need", "manual", "refresh"]) {
  test(`AC-33 stale response ignored after ${change}`, async () => {
    let finish;
    const { journey, nodes } = setupJourney(async (url) => url.endsWith("/suggestion")
      ? new Promise((resolve) => { finish = resolve; }) : response({ slots: [slot] }));
    choose(journey);
    await journey.loadSlots();
    const pending = submitSuggestion(nodes);
    if (change === "laboratory") journey.selectLaboratory({ id: 8, name: "New lab" });
    if (change === "date") { nodes["booking-date"].value = "2030-01-08"; nodes["booking-date"].input(); }
    if (change === "need") { nodes["ai-need"].value = "Changed"; nodes["ai-need"].input(); }
    if (change === "manual") nodes["slots-list"].children[0].children[0].click();
    if (change === "refresh") await journey.loadSlots();
    finish(response({ status: "suggested", candidate: slot }));
    await pending;
    assert.doesNotMatch(nodes["ai-status"].textContent, /Suggestion IA/);
    assert.doesNotMatch(nodes["booking-summary"].textContent, /Suggestion IA/);
    assert.equal(nodes["ai-request"].disabled, false);
  });
}

test("AC-30 genuine empty response and invalid responses never become AI success", async () => {
  for (const payload of [
    { status: "no_candidates", candidate: null }, {},
    { status: "suggested", candidate: { ...slot, workstation_id: "2" } },
    { status: "suggested", candidate: { ...slot, starts_at: "invalid" } },
    { status: "suggested", candidate: null },
  ]) {
    let calls = 0;
    const { journey, nodes } = setupJourney(async () => { calls++; return response(payload); });
    choose(journey);
    await submitSuggestion(nodes);
    assert.match(nodes["ai-status"].textContent, payload.status === "no_candidates" ? /Aucun/ : /invalide|illisible/);
    assert.equal(calls, 1);
    assert.equal(nodes["booking-confirm"].disabled, true);
  }
});

test("AC-35 network and unreadable JSON use safe manual fallback without retry", async () => {
  for (const mode of ["network", "json"]) {
    let calls = 0;
    const { journey, nodes } = setupJourney(async () => {
      calls++;
      if (mode === "network") throw new Error("private network secret");
      return { ok: true, status: 200, json: async () => { throw new Error("private parser secret"); } };
    });
    choose(journey);
    await submitSuggestion(nodes);
    assert.match(nodes["ai-status"].textContent, /réseau|illisible/);
    assert.doesNotMatch(nodes["ai-status"].textContent, /private/);
    assert.equal(calls, 1);
    assert.equal(nodes["availability-load"].disabled, false);
  }
});

test("AC-33 AC-34 need changes clear an offered suggestion and refusal preserves manual flow", async () => {
  const { journey, nodes } = setupJourney(async (url) => response(
    url.endsWith("/suggestion") ? { status: "suggested", candidate: slot } : { error: "Quota atteint" },
    url.endsWith("/suggestion") ? 200 : 409,
  ));
  choose(journey);
  await submitSuggestion(nodes);
  nodes["ai-need"].input();
  assert.equal(nodes["booking-confirm"].disabled, true);
  await submitSuggestion(nodes);
  await nodes["booking-confirm"].click();
  assert.match(nodes["booking-feedback"].textContent, /Quota/);
  assert.equal(nodes["availability-load"].disabled, false);
  assert.doesNotMatch(nodes["ai-status"].textContent, /Suggestion IA/);
});

test("AC-35 expired session disables suggestions and exposes existing reconnect link", async () => {
  let calls = 0;
  const { journey, nodes } = setupJourney(async () => { calls++; return response({}, 401); });
  choose(journey);
  await submitSuggestion(nodes);
  assert.match(nodes["ai-status"].textContent, /session.*expir/i);
  assert.equal(nodes["booking-login"].hidden, false);
  assert.equal(nodes["ai-request"].disabled, true);
  await submitSuggestion(nodes);
  assert.equal(calls, 1);
});

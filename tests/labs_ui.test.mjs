import assert from "node:assert/strict";
import test from "node:test";
import { createCatalogue } from "../src/static/js/labs.mjs";

function elements() {
  const makeElement = () => ({
    textContent: "", hidden: false, disabled: false, children: [], attributes: {},
    set innerHTML(value) { throw new Error("HTML insertion is forbidden"); },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    replaceChildren() { this.children = []; },
    append(item) { this.children.push(item); },
    addEventListener(name, callback) { this[name] = callback; },
  });
  const nodes = Object.fromEntries([
    "laboratory-catalogue", "labs-status", "labs-error", "labs-list", "labs-retry", "labs-login",
  ].map((id) => [id, makeElement()]));
  const document = {
    querySelector(selector) { return nodes[selector.slice(1)]; },
    createElement(tag) { assert.equal(tag, "li"); return makeElement(); },
  };
  return { nodes, document };
}

test("AC-48 loading then real names rendered as text with same-origin session", async () => {
  const { nodes, document } = elements();
  let finish;
  let calls = 0;
  const catalogue = createCatalogue(document, (url, options) => {
    calls++;
    assert.equal(url, "/api/labs");
    assert.equal(options.credentials, "same-origin");
    return new Promise((resolve) => { finish = resolve; });
  });
  const loading = catalogue.load();
  assert.match(nodes["labs-status"].textContent, /Chargement/);
  assert.equal(nodes["labs-retry"].disabled, true);
  await catalogue.load();
  assert.equal(calls, 1);
  finish({ ok: true, status: 200, json: async () => ({ laboratories: [
    { id: 2, name: "<img src=x onerror=alert(1)>" },
  ] }) });
  await loading;
  assert.equal(nodes["labs-list"].children[0].textContent, "<img src=x onerror=alert(1)>");
  assert.equal(nodes["labs-list"].hidden, false);
  assert.equal(nodes["labs-retry"].hidden, true);
});

test("AC-48 genuine empty list shows empty state", async () => {
  const { nodes, document } = elements();
  await createCatalogue(document, async () => ({
    ok: true, status: 200, json: async () => ({ laboratories: [] }),
  })).load();
  assert.match(nodes["labs-status"].textContent, /Aucun laboratoire/);
  assert.equal(nodes["labs-list"].hidden, true);
  assert.equal(nodes["labs-error"].textContent, "");
});

for (const failure of ["http", "network", "json", "shape", "unauthorized"]) {
  test(`AC-46/48 ${failure} clears stale data and allows retry`, async () => {
    const { nodes, document } = elements();
    nodes["labs-list"].children.push({ textContent: "Stale data" });
    let calls = 0;
    const catalogue = createCatalogue(document, async () => {
      calls++;
      if (calls > 1) return { ok: true, status: 200, json: async () => ({ laboratories: [] }) };
      if (failure === "network") throw new Error("Network down");
      return {
        ok: !["http", "unauthorized"].includes(failure),
        status: failure === "unauthorized" ? 401 : failure === "http" ? 500 : 200,
        json: async () => {
          if (failure === "json") throw new Error("Broken JSON");
          return { laboratories: [{ id: "wrong", name: null }] };
        },
      };
    });
    await catalogue.load();
    assert.equal(nodes["labs-list"].children.length, 0);
    assert.equal(nodes["labs-list"].hidden, true);
    assert.ok(nodes["labs-error"].textContent);
    assert.equal(nodes["labs-retry"].hidden, false);
    assert.equal(nodes["labs-login"].hidden, failure !== "unauthorized");
    await nodes["labs-retry"].click();
    assert.equal(calls, 2);
    assert.equal(nodes["labs-error"].textContent, "");
  });
}

import assert from "node:assert/strict";
import test from "node:test";
import { createStaffCatalogue } from "../src/static/js/staff_catalogue.mjs";

const endpoint = "/api/staff/catalogue";
const testCsrf = "isolated-test-csrf";

function documentFixture() {
  const make = (tag) => ({
    tag, textContent: "", hidden: false, value: "", children: [], attributes: {},
    set innerHTML(value) { throw new Error("Catalogue names must be rendered as text"); },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    replaceChildren(...items) { this.children = items; },
    append(...items) { this.children.push(...items); },
    addEventListener(name, callback) { this[name] = callback; },
    querySelector(selector) { return this.children.find((child) => child.tag === selector); },
    focus() { document.activeElement = this; },
  });
  const nodes = Object.fromEntries(["status", "error", "refresh", "login", "labs", "create-lab", "lab-name"]
    .map((name) => [name, make(name)]));
  nodes["create-lab"].elements = { csrfmiddlewaretoken: { value: testCsrf } };
  nodes["create-lab"].append(make("button"));
  nodes["create-lab"].hidden = true;
  nodes.refresh.hidden = true;
  nodes.login.hidden = true;
  const document = {
    activeElement: null,
    querySelector(selector) { return nodes[selector.slice("#staff-catalogue-".length)]; },
    createElement: make,
  };
  return { nodes, document };
}

const response = (payload, status = 200) => ({ status, ok: status < 300, json: async () => payload });
const submit = (form) => form.submit({ preventDefault() {} });
const north = { id: 4, name: "<b>Labo Nord</b>" };
const station = { id: 7, name: "Poste A", laboratory_id: north.id, is_operational: true };
const labsUrl = `${endpoint}/laboratories/${north.id}`;
const stationUrl = `${labsUrl}/workstations`;
const stateUrl = `${stationUrl}/${station.id}/state`;

test("AC-6 AC-7 AC-8 create and rename both entities via CSRF-protected requests", async () => {
  const { nodes, document } = documentFixture();
  const calls = [];
  let finishCreate;
  const renamedLab = { ...north, name: "Labo photonique" };
  const renamedStation = { id: station.id, name: "Poste laser", laboratory_id: north.id };
  const responses = [
    response({ laboratories: [] }),
    () => new Promise((resolve) => { finishCreate = resolve; }),
    response({ workstation: station }, 201),
    response({ laboratory: renamedLab }),
    response({ workstation: renamedStation }),
    response({ laboratories: [{ ...renamedLab, workstations: [{ ...station, name: renamedStation.name }] }] }),
  ];
  const catalogue = createStaffCatalogue(document, async (url, options) => {
    const next = responses[calls.length];
    calls.push([url, options]);
    return typeof next === "function" ? next() : next;
  });
  await catalogue.load();
  assert.match(nodes.status.textContent, /premier laboratoire/);
  assert.equal(nodes["create-lab"].hidden, false);

  nodes["lab-name"].value = `  ${north.name}  `;
  const saving = submit(nodes["create-lab"]);
  assert.match(nodes.status.textContent, /Enregistrement/);
  assert.equal(nodes["create-lab"].attributes["aria-busy"], "true");
  await submit(nodes["create-lab"]);
  assert.equal(calls.length, 2);
  finishCreate(response({ laboratory: north }, 201));
  await saving;
  assert.equal(nodes["create-lab"].attributes["aria-busy"], undefined);
  assert.equal(nodes["lab-name"].value, "");
  assert.match(nodes.status.textContent, /Laboratoire créé/);
  const [card] = nodes.labs.children;
  const [title, renameLab, , stations, createStation] = card.children;
  const [, addStationInput] = createStation.children;
  assert.equal(title.textContent, north.name);
  assert.equal(document.activeElement, addStationInput);
  assert.equal(createStation.children[0].htmlFor, addStationInput.id);

  addStationInput.value = station.name;
  await submit(createStation);
  assert.match(nodes.status.textContent, /Poste ajouté/);
  const [stationTitle, renameStation, state, stateButton] = stations.children[0].children;
  assert.equal(document.activeElement, stationTitle);
  assert.equal(stationTitle.textContent, station.name);
  assert.equal(state.textContent, "En service");
  assert.equal(stateButton.textContent, "Mettre hors service");

  renameLab.children[1].value = renamedLab.name;
  await submit(renameLab);
  assert.equal(title.textContent, renamedLab.name);
  assert.equal(document.activeElement, title);
  assert.match(nodes.status.textContent, /Laboratoire renommé/);
  renameStation.children[1].value = renamedStation.name;
  await submit(renameStation);
  assert.equal(stationTitle.textContent, renamedStation.name);
  assert.equal(document.activeElement, stationTitle);
  assert.equal(state.textContent, "En service");
  assert.equal(stations.children.length, 1);
  assert.equal(nodes.labs.children.length, 1);

  await catalogue.load();
  const persisted = nodes.labs.children[0];
  assert.equal(persisted.children[0].id, `staff-catalogue-title-${north.id}`);
  assert.equal(persisted.children[0].textContent, renamedLab.name);
  assert.equal(persisted.children[3].children[0].children[0].textContent, renamedStation.name);
  assert.deepEqual(calls.map(([url, options]) => [options.method, url]), [
    ["GET", endpoint], ["POST", endpoint], ["POST", stationUrl], ["PATCH", labsUrl],
    ["PATCH", `${stationUrl}/${station.id}`], ["GET", endpoint],
  ]);
  assert.deepEqual(calls.slice(1, -1).map(([, options]) => JSON.parse(options.body)), [
    { name: north.name }, { name: station.name }, { name: renamedLab.name }, { name: renamedStation.name },
  ]);
  for (const [, options] of calls.slice(1, -1)) {
    assert.equal(options.credentials, "same-origin");
    assert.equal(options.headers["X-CSRFToken"], testCsrf);
  }
});

test("AC-10 AC-12 the state action sends an explicit boolean and keeps keyboard focus", async () => {
  const { nodes, document } = documentFixture();
  const writes = [];
  let finishUpdate;
  const catalogue = createStaffCatalogue(document, async (url, options) => {
    if (options.method === "GET") {
      return response({ laboratories: [{ ...north, workstations: [station] }] });
    }
    writes.push([url, options]);
    if (writes.length === 1) return new Promise((resolve) => { finishUpdate = resolve; });
    return response({ workstation: { id: station.id, laboratory_id: north.id, is_operational: true } });
  });
  await catalogue.load();
  const [title, , state, button] = nodes.labs.children[0].children[3].children[0].children;
  assert.equal(state.textContent, "En service");
  assert.equal(button.textContent, "Mettre hors service");
  assert.equal(button.type, "button");
  assert.equal(button.attributes["aria-describedby"], `${title.id} ${state.id}`);
  button.focus();

  const disabling = button.click();
  assert.match(nodes.status.textContent, /Enregistrement/);
  assert.equal(button.attributes["aria-disabled"], "true");
  await button.click();
  assert.equal(writes.length, 1);
  assert.equal(state.textContent, "En service");
  finishUpdate(response({ workstation: { id: station.id, laboratory_id: north.id, is_operational: false } }));
  await disabling;
  assert.equal(button.attributes["aria-disabled"], undefined);
  assert.equal(state.textContent, "Hors service");
  assert.equal(button.textContent, "Remettre en service");
  assert.equal(nodes.status.textContent, "Poste mis hors service.");
  assert.equal(document.activeElement, button);

  await button.click();
  assert.equal(state.textContent, "En service");
  assert.equal(button.textContent, "Mettre hors service");
  assert.equal(nodes.status.textContent, "Poste remis en service.");
  assert.equal(document.activeElement, button);
  assert.deepEqual(writes.map(([url, options]) => [url, options.method, JSON.parse(options.body)]), [
    [stateUrl, "PATCH", { is_operational: false }], [stateUrl, "PATCH", { is_operational: true }],
  ]);
  for (const [, options] of writes) {
    assert.equal(options.credentials, "same-origin");
    assert.equal(options.headers["X-CSRFToken"], testCsrf);
  }
});

test("AC-10 an unexpected state reply requires a fresh read instead of retrying", async () => {
  const { nodes, document } = documentFixture();
  let writes = 0;
  let reads = 0;
  const catalogue = createStaffCatalogue(document, async (url, options) => {
    if (options.method === "GET") {
      const workstation = { ...station, is_operational: ++reads === 1 };
      return response({ laboratories: [{ ...north, workstations: [workstation] }] });
    }
    writes++;
    return response({ workstation: { id: station.id, laboratory_id: north.id, is_operational: "false" } });
  });
  await catalogue.load();
  const [, , state, button] = nodes.labs.children[0].children[3].children[0].children;
  await button.click();
  assert.match(nodes.error.textContent, /non confirmé/);
  assert.equal(state.textContent, "En service");
  assert.equal(nodes.refresh.hidden, false);
  await button.click();
  assert.equal(writes, 1);
  assert.equal(document.activeElement, nodes.refresh);
  await nodes.refresh.click();
  const [, , newState, newButton] = nodes.labs.children[0].children[3].children[0].children;
  assert.equal(newState.textContent, "Hors service");
  assert.equal(newButton.textContent, "Remettre en service");
  assert.equal(writes, 1);
});

test("AC-8 AC-10 renaming a workstation preserves its out-of-service display", async () => {
  const { nodes, document } = documentFixture();
  const renamedStation = { id: station.id, name: "Poste laser", laboratory_id: north.id };
  const catalogue = createStaffCatalogue(document, async (url, options) => options.method === "GET"
    ? response({ laboratories: [{ ...north, workstations: [{ ...station, is_operational: false }] }] })
    : response({ workstation: renamedStation }));
  await catalogue.load();
  const [title, rename, state, button] = nodes.labs.children[0].children[3].children[0].children;
  assert.equal(state.textContent, "Hors service");
  rename.children[1].value = renamedStation.name;
  await submit(rename);
  assert.equal(title.textContent, renamedStation.name);
  assert.equal(state.textContent, "Hors service");
  assert.equal(button.textContent, "Remettre en service");
});

test("AC-41 read failure exposes refresh and moving focus to the status when recovered", async () => {
  const { nodes, document } = documentFixture();
  let finishRead;
  let reads = 0;
  const catalogue = createStaffCatalogue(document, async () => {
    if (++reads === 1) return new Promise((resolve) => { finishRead = resolve; });
    return response({ laboratories: [{ ...north, workstations: [station] }] });
  });
  const reading = catalogue.load();
  assert.match(nodes.status.textContent, /Chargement/);
  assert.equal(nodes["create-lab"].hidden, true);
  await catalogue.load();
  assert.equal(reads, 1);
  finishRead(response({}, 500));
  await reading;
  assert.match(nodes.error.textContent, /réessayer/);
  assert.equal(nodes.refresh.hidden, false);
  assert.equal(nodes.labs.attributes["aria-busy"], undefined);
  nodes.refresh.focus();
  await nodes.refresh.click();
  assert.equal(document.activeElement, nodes.status);
  assert.equal(nodes.refresh.hidden, true);
  assert.equal(nodes.error.textContent, "");
});

test("AC-7 AC-8 conflict preserves rows and an entered name without resending", async () => {
  const { nodes, document } = documentFixture();
  let writes = 0;
  await createStaffCatalogue(document, async (url, options) => {
    if (options.method === "GET") return response({ laboratories: [{ ...north, workstations: [station] }] });
    writes++;
    return response({ error: "<b>Duplicate name</b>" }, 409);
  }).load();
  const [, , , stations, add] = nodes.labs.children[0].children;
  const input = add.children[1];
  input.value = " ";
  await submit(add);
  assert.match(nodes.error.textContent, /150 caractères/);
  assert.equal(writes, 0);
  input.value = station.name;
  await submit(add);
  assert.equal(writes, 1);
  assert.equal(input.value, station.name);
  assert.equal(stations.children.length, 1);
  assert.match(nodes.error.textContent, /existe déjà dans ce laboratoire/);
  assert.equal(document.activeElement, nodes.error);
});

for (const [outcome, reply, message] of [
  ["lost response", () => { throw new Error("Connection interrupted"); }, /non confirmé/],
  ["server error", () => response({}, 500), /non confirmé/],
  ["missing entity", () => response({}, 404), /Actualise/],
  ["wrong entity response", () => response({ laboratory: { id: 8, name: "Other lab" } }), /non confirmé/],
]) {
  test(`AC-8 ${outcome} requires a fresh read before another mutation`, async () => {
    const { nodes, document } = documentFixture();
    let writes = 0;
    await createStaffCatalogue(document, async (url, options) => {
      if (options.method === "GET") return response({ laboratories: [{ ...north, workstations: [] }] });
      writes++;
      return reply();
    }).load();
    const [heading, rename] = nodes.labs.children[0].children;
    rename.children[1].value = "New lab name";
    await submit(rename);
    assert.match(nodes.error.textContent, message);
    assert.equal(heading.textContent, north.name);
    assert.equal(nodes.refresh.hidden, false);
    await submit(rename);
    assert.equal(writes, 1);
    assert.equal(document.activeElement, nodes.refresh);
    await nodes.refresh.click();
    assert.equal(writes, 1);
  });
}

for (const code of [401, 403]) {
  test(`AC-5 catalogue write ${code} hides the editors and distinguishes access failures`, async () => {
    const { nodes, document } = documentFixture();
    await createStaffCatalogue(document, async (url, options) => options.method === "GET"
      ? response({ laboratories: [{ ...north, workstations: [] }] }) : response({}, code)).load();
    nodes["lab-name"].value = "Invalid session";
    await submit(nodes["create-lab"]);
    assert.equal(nodes["create-lab"].hidden, true);
    assert.equal(nodes.labs.children.length, 0);
    assert.match(nodes.error.textContent, code === 401 ? /session a expiré/ : /Accès refusé/);
    assert.equal(nodes.login.hidden, code !== 401);
    assert.equal(nodes.refresh.hidden, true);
  });
}

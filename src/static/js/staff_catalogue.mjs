const endpoint = "/api/staff/catalogue";

const refusalMessages = {
  400: "La demande est invalide.",
  413: "La demande est trop volumineuse.",
  415: "La demande doit être envoyée au format JSON.",
};

const nameRefusalMessages = {
  ...refusalMessages,
  409: "Ce nom de poste existe déjà dans ce laboratoire.",
  422: "Entre un nom de 1 à 150 caractères.",
};

const stateRefusalMessages = {
  ...refusalMessages,
  422: "L’état demandé pour le poste est invalide.",
};

function namedEntity(value, expectedId) {
  if (!value || !Number.isSafeInteger(value.id) || value.id < 1
      || typeof value.name !== "string" || !value.name.trim()
      || (expectedId !== undefined && value.id !== expectedId)) {
    throw new Error("Invalid catalogue entity");
  }
  return value;
}

function nameEditor(document, id, labelText, buttonText, value = "") {
  const form = document.createElement("form");
  form.className = "staff-catalogue-editor";
  form.method = "post";
  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = labelText;
  const input = document.createElement("input");
  input.id = id;
  input.type = "text";
  input.required = true;
  input.maxLength = 150;
  input.value = value;
  const button = document.createElement("button");
  button.type = "submit";
  button.textContent = buttonText;
  form.append(label, input, button);
  return { form, input, button };
}

export function createStaffCatalogue(document, fetcher) {
  const find = (suffix) => document.querySelector(`#staff-catalogue-${suffix}`);
  const status = find("status");
  const error = find("error");
  const refresh = find("refresh");
  const login = find("login");
  const labs = find("labs");
  const createLab = find("create-lab");
  const headers = { Accept: "application/json" };
  const requestOptions = { credentials: "same-origin", mode: "same-origin", cache: "no-store" };
  let busy = false;
  let current = false;

  function showError(message, focus = true) {
    status.textContent = "";
    error.textContent = message;
    if (focus) error.focus();
  }

  function showAccessError(code) {
    current = false;
    createLab.hidden = true;
    labs.replaceChildren();
    login.hidden = code !== 401;
    refresh.hidden = true;
    showError(code === 401
      ? "Ta session a expiré. Reconnecte-toi."
      : "Accès refusé. Vérifie ton rôle et recharge la page.");
  }

  function canWrite() {
    if (busy) return false;
    if (current) return true;
    refresh.focus();
    return false;
  }

  async function save(button, { method, url, payload, successText, apply, refusals }) {
    busy = true;
    button.setAttribute("aria-disabled", "true");
    error.textContent = "";
    status.textContent = "Enregistrement…";
    try {
      const response = await fetcher(url, {
        ...requestOptions,
        method,
        headers: {
          ...headers,
          "Content-Type": "application/json",
          "X-CSRFToken": createLab.elements.csrfmiddlewaretoken.value,
        },
        body: JSON.stringify(payload),
      });
      if (response.status === 401 || response.status === 403) {
        showAccessError(response.status);
        return;
      }
      if (response.status === 404) {
        current = false;
        refresh.hidden = false;
        showError("Cet élément a changé. Actualise le catalogue.");
        return;
      }
      if (Object.hasOwn(refusals, response.status)) {
        showError(refusals[response.status]);
        return;
      }
      if (!response.ok) throw new Error("Catalogue write status is uncertain");
      const result = await response.json();
      const focusTarget = apply(result);
      status.textContent = successText;
      focusTarget.focus();
    } catch {
      current = false;
      refresh.hidden = false;
      showError("Enregistrement non confirmé. Actualise le catalogue avant de modifier à nouveau.");
    } finally {
      busy = false;
      button.removeAttribute("aria-disabled");
    }
  }

  function bindEditor(editor, method, url, successText, apply) {
    editor.form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!canWrite()) return;
      const name = editor.input.value.trim();
      if (!name || name.length > 150) {
        showError(nameRefusalMessages[422]);
        return;
      }
      editor.form.setAttribute("aria-busy", "true");
      editor.input.readOnly = true;
      try {
        await save(editor.button, {
          method, url, payload: { name }, successText, apply, refusals: nameRefusalMessages,
        });
      } finally {
        editor.form.removeAttribute("aria-busy");
        editor.input.readOnly = false;
      }
    });
  }

  function workstationState(station, labId, url, title) {
    if (typeof station.is_operational !== "boolean") throw new Error("Invalid workstation state");

    const state = document.createElement("p");
    state.id = `staff-catalogue-state-${station.id}`;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "secondary";
    button.id = `staff-catalogue-action-${station.id}`;
    button.setAttribute("aria-describedby", `${title.id} ${state.id}`);

    let isOperational = station.is_operational;
    function renderState() {
      state.textContent = isOperational ? "En service" : "Hors service";
      button.textContent = isOperational ? "Mettre hors service" : "Remettre en service";
    }
    renderState();
    button.addEventListener("click", async () => {
      if (!canWrite()) return;
      const desiredState = !isOperational;
      await save(button, {
        method: "PATCH",
        url: `${url}/state`,
        payload: { is_operational: desiredState },
        successText: desiredState ? "Poste remis en service." : "Poste mis hors service.",
        refusals: stateRefusalMessages,
        apply(result) {
          const updated = result.workstation;
          if (updated?.id !== station.id || updated.laboratory_id !== labId
              || updated.is_operational !== desiredState) {
            throw new Error("Invalid workstation state response");
          }
          isOperational = updated.is_operational;
          renderState();
          return button;
        },
      });
    });
    return { state, button };
  }

  function workstationRow(labId, station) {
    namedEntity(station);
    const row = document.createElement("li");
    const title = document.createElement("h5");
    title.id = `staff-catalogue-station-title-${station.id}`;
    title.textContent = station.name;
    title.tabIndex = -1;
    const rename = nameEditor(document, `staff-catalogue-station-${station.id}`,
      "Nom du poste", "Renommer le poste", station.name);
    const url = `${endpoint}/laboratories/${labId}/workstations/${station.id}`;
    bindEditor(rename, "PATCH", url, "Poste renommé.", (result) => {
      const updated = namedEntity(result.workstation, station.id);
      if (updated.laboratory_id !== labId) throw new Error("Workstation moved");
      title.textContent = updated.name;
      rename.input.value = updated.name;
      return title;
    });
    const { state, button } = workstationState(station, labId, url, title);
    row.append(title, rename.form, state, button);
    return { row, title };
  }

  function laboratoryCard(lab, workstations) {
    namedEntity(lab);
    if (!Array.isArray(workstations)) throw new Error("Invalid workstation list");
    const card = document.createElement("section");
    card.className = "staff-catalogue-card";
    const title = document.createElement("h3");
    title.id = `staff-catalogue-title-${lab.id}`;
    title.textContent = lab.name;
    title.tabIndex = -1;
    card.setAttribute("aria-labelledby", title.id);
    const rename = nameEditor(document, `staff-catalogue-lab-${lab.id}`,
      "Nom du laboratoire", "Renommer le laboratoire", lab.name);
    const stationTitle = document.createElement("h4");
    stationTitle.textContent = "Postes";
    const stationList = document.createElement("ul");
    stationList.className = "staff-catalogue-stations";
    stationList.append(...workstations.map((station) => workstationRow(lab.id, station).row));
    const add = nameEditor(document, `staff-catalogue-new-station-${lab.id}`,
      "Nom du nouveau poste", "Ajouter le poste");
    const url = `${endpoint}/laboratories/${lab.id}`;
    bindEditor(rename, "PATCH", url, "Laboratoire renommé.", (result) => {
      const updated = namedEntity(result.laboratory, lab.id);
      title.textContent = updated.name;
      rename.input.value = updated.name;
      return title;
    });
    bindEditor(add, "POST", `${url}/workstations`, "Poste ajouté.", (result) => {
      if (result.workstation?.laboratory_id !== lab.id) throw new Error("Wrong laboratory");
      const station = workstationRow(lab.id, result.workstation);
      stationList.append(station.row);
      add.input.value = "";
      return station.title;
    });
    card.append(title, rename.form, stationTitle, stationList, add.form);
    return { card, next: add.input };
  }

  async function load() {
    if (busy) return;
    busy = true;
    current = false;
    refresh.setAttribute("aria-disabled", "true");
    labs.setAttribute("aria-busy", "true");
    login.hidden = true;
    error.textContent = "";
    status.textContent = "Chargement du catalogue…";
    try {
      const response = await fetcher(endpoint, { ...requestOptions, method: "GET", headers });
      if (response.status === 401 || response.status === 403) {
        showAccessError(response.status);
        return;
      }
      if (!response.ok) throw new Error("Catalogue read failed");
      const { laboratories } = await response.json();
      if (!Array.isArray(laboratories)) throw new Error("Invalid laboratory list");
      const cards = laboratories.map((lab) => laboratoryCard(lab, lab.workstations).card);
      labs.replaceChildren(...cards);
      current = true;
      createLab.hidden = false;
      status.textContent = cards.length ? "Catalogue chargé." : "Crée ton premier laboratoire.";
      if (document.activeElement === refresh) status.focus();
      refresh.hidden = true;
    } catch {
      refresh.hidden = false;
      showError("Impossible de charger le catalogue. Actualise-le pour réessayer.", false);
    } finally {
      busy = false;
      refresh.removeAttribute("aria-disabled");
      labs.removeAttribute("aria-busy");
    }
  }

  const newLab = { form: createLab, input: find("lab-name"), button: createLab.querySelector("button") };
  bindEditor(newLab, "POST", endpoint, "Laboratoire créé.", (result) => {
    const laboratory = laboratoryCard(result.laboratory, []);
    labs.append(laboratory.card);
    newLab.input.value = "";
    return laboratory.next;
  });
  refresh.addEventListener("click", load);
  return { load };
}

if (typeof document !== "undefined") {
  createStaffCatalogue(document, window.fetch.bind(window)).load();
}

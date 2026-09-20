(() => {
  "use strict";

  const el = (id) => document.getElementById(id);

  const cameraStatusDot = el("cameraStatusDot");
  const cameraStatusText = el("cameraStatusText");
  const clockEl = el("clock");

  const horseCountBadge = el("horseCountBadge");

  const statHorses = el("statHorses");
  const statPeople = el("statPeople");
  const statFps = el("statFps");
  const statStatus = el("statStatus");

  const trackList = el("trackList");

  // ---------------- Clock ----------------
  function tickClock() {
    clockEl.textContent = new Date().toLocaleTimeString([], { hour12: false });
  }
  tickClock();
  setInterval(tickClock, 1000);

  // ---------------- State polling ----------------
  function setCameraStatus(status, message) {
    const normalized = (status || "").toUpperCase();
    cameraStatusDot.className = "dot";
    statStatus.className = "stat-value stat-status";

    if (normalized === "ONLINE") {
      cameraStatusDot.classList.add("online");
      cameraStatusText.textContent = "Online";
      statStatus.textContent = "Online";
      statStatus.classList.add("online");
    } else if (normalized === "OFFLINE") {
      cameraStatusDot.classList.add("offline");
      cameraStatusText.textContent = "Offline";
      statStatus.textContent = "Offline";
      statStatus.classList.add("offline");
    } else {
      cameraStatusDot.classList.add("starting");
      cameraStatusText.textContent = "Starting…";
      statStatus.textContent = "Starting";
    }
    cameraStatusText.title = message || "";
    document.getElementById("cameraStatusPill").title = message || "";
  }

  function renderTracked(horses) {
    if (!horses.length) {
      trackList.innerHTML = '<div class="panel-empty">Nothing detected right now.</div>';
      return;
    }
    trackList.innerHTML = horses
      .map(
        (h) => `
        <div class="track-row">
          <span class="track-name">${h.type === "person" ? "Person" : "Horse"} #${h.id}</span>
          <span class="track-conf">${Math.round(h.confidence * 100)}%</span>
        </div>`
      )
      .join("");
  }

  async function pollState() {
    try {
      const res = await fetch("/api/state", { cache: "no-store" });
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();

      setCameraStatus(data.camera_status, data.camera_message);

      const horseCount = data.stats.horses_detected;
      const personCount = data.stats.persons_detected;
      horseCountBadge.textContent =
        `${horseCount} horse${horseCount === 1 ? "" : "s"}, ` +
        `${personCount} ${personCount === 1 ? "person" : "people"} tracked`;
      statPeople.textContent = personCount;

      statHorses.textContent = horseCount;
      statFps.textContent = data.processed_fps;

      renderTracked(data.horses);
    } catch (e) {
      // transient network hiccup - keep last known UI state
    }
  }

  pollState();
  setInterval(pollState, 500);
})();

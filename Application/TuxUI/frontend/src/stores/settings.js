import { writable, derived } from "svelte/store";

const STORAGE_KEY = "tuxtailor_settings";

const DEFAULTS = {
  theme: "mocha",         // mocha | macchiato | frappe | latte | default
  lastDarkTheme: "mocha", // remembers which dark theme was active before switching to latte
  profile: {
    expertise: "intermediate", // beginner | intermediate | advanced
    distro: "",
    systemPrompt: "",
  },
};

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch {
    return DEFAULTS;
  }
}

function createSettingsStore() {
  const { subscribe, update, set } = writable(loadFromStorage());

  function persist(value) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    } catch {}
    return value;
  }

  function setTheme(theme) {
    update((s) => {
      const isDark = theme !== "latte";
      return persist({
        ...s,
        theme,
        lastDarkTheme: isDark ? theme : s.lastDarkTheme,
      });
    });
  }

  function toggleDarkMode(dark) {
    update((s) => {
      const theme = dark ? (s.lastDarkTheme || "mocha") : "latte";
      return persist({
        ...s,
        theme,
        lastDarkTheme: dark ? (s.lastDarkTheme || "mocha") : s.lastDarkTheme,
      });
    });
  }

  function setProfile(patch) {
    update((s) => persist({ ...s, profile: { ...s.profile, ...patch } }));
  }

  return { subscribe, set, setTheme, toggleDarkMode, setProfile };
}

export const settings = createSettingsStore();

export const isDarkMode = derived(settings, ($s) => $s.theme !== "latte");

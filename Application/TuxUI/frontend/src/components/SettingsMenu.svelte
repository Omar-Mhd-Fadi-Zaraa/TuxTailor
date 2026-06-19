<script>
  import { settings, isDarkMode } from "../stores/settings.js";

  export let onClose;

  let activeTab = "appearance"; // appearance | model | profile

  // Local copies of settings — written back on "Done"
  let localTheme      = $settings.theme;
  let localDark       = $isDarkMode;
  let localBackendUrl = "http://localhost:8080";
  let localModel      = "default";
  let localExpertise  = $settings.profile.expertise;
  let localDistro     = $settings.profile.distro;
  let localPrompt     = $settings.profile.systemPrompt;

  const THEMES = [
    {
      id: "mocha",
      label: "Mocha",
      dark: true,
      swatches: ["#1e1e2e", "#cba6f7", "#cdd6f4", "#313244"],
    },
    {
      id: "macchiato",
      label: "Macchiato",
      dark: true,
      swatches: ["#24273a", "#c6a0f6", "#cad3f5", "#363a4f"],
    },
    {
      id: "frappe",
      label: "Frappé",
      dark: true,
      swatches: ["#303446", "#ca9ee6", "#c6d0f5", "#414559"],
    },
    {
      id: "latte",
      label: "Latte",
      dark: false,
      swatches: ["#eff1f5", "#8839ef", "#4c4f69", "#ccd0da"],
    },
    {
      id: "default",
      label: "Default",
      dark: true,
      swatches: ["#212121", "#10a37f", "#ececec", "#2a2a2a"],
    },
  ];

  const EXPERTISE = [
    { value: "beginner",     label: "Beginner" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced",     label: "Advanced" },
  ];

  function pickTheme(id) {
    localTheme = id;
    localDark  = id !== "latte";
    // Preview immediately
    settings.setTheme(id);
  }

  function toggleDark() {
    localDark = !localDark;
    settings.toggleDarkMode(localDark);
    localTheme = $settings.theme;
  }

  function save() {
    settings.setProfile({
      expertise:    localExpertise,
      distro:       localDistro,
      systemPrompt: localPrompt,
    });
    onClose();
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="overlay" on:click|self={onClose}>
  <div class="settings-panel">

    <!-- Header -->
    <div class="settings-header">
      <h2>Settings</h2>
      <button class="close-btn" on:click={onClose}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" class:active={activeTab === "appearance"} on:click={() => (activeTab = "appearance")}>Appearance</button>
      <button class="tab" class:active={activeTab === "model"}      on:click={() => (activeTab = "model")}>Model</button>
      <button class="tab" class:active={activeTab === "profile"}    on:click={() => (activeTab = "profile")}>Profile</button>
    </div>

    <!-- Body -->
    <div class="settings-body">

      <!-- ── Appearance tab ── -->
      {#if activeTab === "appearance"}
        <section class="settings-section">
          <h3>Mode</h3>
          <label class="toggle-row">
            <span>Light mode</span>
            <button
              class="toggle"
              class:on={!localDark}
              role="switch"
              aria-checked={!localDark}
              on:click={toggleDark}
            >
              <span class="toggle-thumb"></span>
            </button>
          </label>
        </section>

        <section class="settings-section">
          <h3>Catppuccin Theme</h3>
          <div class="theme-grid">
            {#each THEMES as t}
              <button
                class="theme-card"
                class:selected={localTheme === t.id}
                on:click={() => pickTheme(t.id)}
                title={t.label}
              >
                <div class="theme-preview">
                  {#each t.swatches as color}
                    <div class="swatch" style="background:{color}"></div>
                  {/each}
                </div>
                <span class="theme-label">{t.label}</span>
                {#if localTheme === t.id}
                  <svg class="check-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                {/if}
              </button>
            {/each}
          </div>
        </section>
      {/if}

      <!-- ── Model tab ── -->
      {#if activeTab === "model"}
        <section class="settings-section">
          <h3>Backend</h3>
          <label class="field">
            <span>URL</span>
            <input type="text" bind:value={localBackendUrl} placeholder="http://localhost:8080" />
          </label>
        </section>

        <section class="settings-section">
          <h3>Model</h3>
          <label class="field">
            <span>Model name</span>
            <input type="text" bind:value={localModel} placeholder="e.g. llama3, mistral" />
          </label>
        </section>

        <section class="settings-section">
          <h3>About</h3>
          <p class="about-text">TuxTailor — Your agentic Linux config assistant.</p>
        </section>
      {/if}

      <!-- ── Profile tab ── -->
      {#if activeTab === "profile"}
        <section class="settings-section">
          <h3>Linux Expertise</h3>
          <div class="expertise-row">
            {#each EXPERTISE as e}
              <button
                class="expertise-btn"
                class:selected={localExpertise === e.value}
                on:click={() => (localExpertise = e.value)}
              >{e.label}</button>
            {/each}
          </div>
        </section>

        <section class="settings-section">
          <h3>Distribution of Choice</h3>
          <label class="field">
            <span>Distro</span>
            <input
              type="text"
              bind:value={localDistro}
              placeholder="e.g. Arch Linux, Ubuntu, NixOS"
            />
          </label>
        </section>

        <section class="settings-section">
          <h3>Agent Behaviour</h3>
          <label class="field">
            <span>System prompt</span>
            <textarea
              class="prompt-textarea"
              bind:value={localPrompt}
              placeholder="Describe how you want the agent to act, its tone, priorities, etc."
              rows="5"
            ></textarea>
          </label>
        </section>
      {/if}
    </div>

    <!-- Footer -->
    <div class="settings-footer">
      <button class="save-btn" on:click={save}>Done</button>
    </div>

  </div>
</div>

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .settings-panel {
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    width: 460px;
    max-width: calc(100vw - 2rem);
    display: flex;
    flex-direction: column;
    max-height: 82vh;
    overflow: hidden;
  }

  /* ── Header ── */
  .settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem 0.75rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .settings-header h2 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
  }

  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.12s;
  }

  .close-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  /* ── Tabs ── */
  .tabs {
    display: flex;
    gap: 0;
    padding: 0 1.25rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .tab {
    padding: 0.55rem 0.9rem;
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: color 0.12s, border-color 0.12s;
    margin-bottom: -1px;
  }

  .tab:hover {
    color: var(--text);
  }

  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }

  /* ── Body ── */
  .settings-body {
    flex: 1;
    overflow-y: auto;
    padding: 1.1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .settings-section h3 {
    margin: 0 0 0.6rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-faint);
  }

  /* ── Mode toggle ── */
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.87rem;
    color: var(--text-muted);
    cursor: pointer;
  }

  .toggle {
    position: relative;
    width: 38px;
    height: 22px;
    border-radius: 999px;
    border: none;
    background: var(--border-strong);
    cursor: pointer;
    transition: background 0.18s;
    padding: 0;
    flex-shrink: 0;
  }

  .toggle.on {
    background: var(--accent);
  }

  .toggle-thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #fff;
    transition: left 0.18s;
    pointer-events: none;
  }

  .toggle.on .toggle-thumb {
    left: calc(100% - 19px);
  }

  /* ── Theme grid ── */
  .theme-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
  }

  .theme-card {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.3rem 0.45rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: transparent;
    cursor: pointer;
    transition: border-color 0.12s, background 0.12s;
  }

  .theme-card:hover {
    background: var(--hover-bg);
    border-color: var(--border-strong);
  }

  .theme-card.selected {
    border-color: var(--accent);
  }

  .theme-preview {
    display: flex;
    gap: 2px;
    border-radius: 4px;
    overflow: hidden;
    width: 100%;
    height: 28px;
  }

  .swatch {
    flex: 1;
  }

  .theme-label {
    font-size: 0.68rem;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .check-icon {
    position: absolute;
    top: 4px;
    right: 4px;
    color: var(--accent);
  }

  /* ── Field ── */
  .field {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .field span {
    font-size: 0.82rem;
    color: var(--text-muted);
  }

  .field input,
  .prompt-textarea {
    width: 100%;
    padding: 0.4rem 0.65rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--input-bg);
    color: var(--text);
    font-family: inherit;
    font-size: 0.87rem;
    outline: none;
    transition: border-color 0.15s;
    box-sizing: border-box;
  }

  .field input:focus,
  .prompt-textarea:focus {
    border-color: var(--accent);
  }

  .prompt-textarea {
    resize: vertical;
    line-height: 1.5;
    min-height: 100px;
  }

  /* ── Expertise ── */
  .expertise-row {
    display: flex;
    gap: 0.4rem;
  }

  .expertise-btn {
    flex: 1;
    padding: 0.4rem 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: transparent;
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.82rem;
    cursor: pointer;
    transition: border-color 0.12s, color 0.12s, background 0.12s;
  }

  .expertise-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  .expertise-btn.selected {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--hover-bg);
  }

  .about-text {
    margin: 0;
    font-size: 0.83rem;
    color: var(--text-muted);
    line-height: 1.5;
  }

  /* ── Footer ── */
  .settings-footer {
    padding: 0.75rem 1.25rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: flex-end;
    flex-shrink: 0;
  }

  .save-btn {
    padding: 0.4rem 1.1rem;
    border: none;
    border-radius: 7px;
    background: var(--accent);
    color: #fff;
    font-family: inherit;
    font-size: 0.87rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .save-btn:hover {
    opacity: 0.85;
  }
</style>

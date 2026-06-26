<script>
  import { createEventDispatcher } from "svelte";
  import { Login, Signup } from "../../wailsjs/go/main/App.js";
  import { auth } from "../stores/auth.js";
  import { settings } from "../stores/settings.js";

  const dispatch = createEventDispatcher();

  let mode = "login";
  let userName = "";
  let password = "";
  let confirmPassword = "";
  let level = "intermediate";
  let distro = "";
  let systemPrompt = "";
  let error = "";
  let loading = false;

  const LEVELS = [
    { value: "beginner", label: "Beginner" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced", label: "Advanced" },
  ];

  async function handleSubmit() {
    error = "";
    const name = userName.trim();
    if (!name || !password) {
      error = "Username and password are required.";
      return;
    }

    if (mode === "signup" && password !== confirmPassword) {
      error = "Passwords do not match.";
      return;
    }

    loading = true;
    try {
      const backendUrl = $settings.backendUrl;
      let userId;

      if (mode === "signup") {
        userId = await Signup(
          name,
          password,
          level,
          systemPrompt,
          distro,
          backendUrl
        );
        settings.setProfile({
          expertise: level,
          distro,
          systemPrompt,
        });
      } else {
        userId = await Login(name, password, backendUrl);
      }

      auth.login(userId, name);
      dispatch("authenticated", { userId, userName: name });
    } catch (e) {
      error = e?.message || String(e);
    } finally {
      loading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="auth-screen">
  <div class="auth-card">
    <div class="auth-header">
      <h1>TuxTailor</h1>
      <p>Your agentic Linux configuration assistant</p>
    </div>

    <div class="mode-tabs">
      <button
        class="mode-tab"
        class:active={mode === "login"}
        on:click={() => { mode = "login"; error = ""; }}
      >Log in</button>
      <button
        class="mode-tab"
        class:active={mode === "signup"}
        on:click={() => { mode = "signup"; error = ""; }}
      >Sign up</button>
    </div>

    <form class="auth-form" on:submit|preventDefault={handleSubmit}>
      <label class="field">
        <span>Username</span>
        <input
          type="text"
          bind:value={userName}
          autocomplete="username"
          on:keydown={handleKeydown}
          disabled={loading}
        />
      </label>

      <label class="field">
        <span>Password</span>
        <input
          type="password"
          bind:value={password}
          autocomplete={mode === "signup" ? "new-password" : "current-password"}
          on:keydown={handleKeydown}
          disabled={loading}
        />
      </label>

      {#if mode === "signup"}
        <label class="field">
          <span>Confirm password</span>
          <input
            type="password"
            bind:value={confirmPassword}
            autocomplete="new-password"
            on:keydown={handleKeydown}
            disabled={loading}
          />
        </label>

        <div class="field">
          <span>Linux expertise</span>
          <div class="level-row">
            {#each LEVELS as item}
              <button
                type="button"
                class="level-btn"
                class:selected={level === item.value}
                on:click={() => (level = item.value)}
                disabled={loading}
              >{item.label}</button>
            {/each}
          </div>
        </div>

        <label class="field">
          <span>Distribution of choice</span>
          <input
            type="text"
            bind:value={distro}
            placeholder="e.g. Arch Linux, Ubuntu"
            disabled={loading}
          />
        </label>

        <label class="field">
          <span>System prompt</span>
          <textarea
            bind:value={systemPrompt}
            rows="4"
            placeholder="How should the agent behave?"
            disabled={loading}
          ></textarea>
        </label>
      {/if}

      {#if error}
        <p class="error">{error}</p>
      {/if}

      <button class="submit-btn" type="submit" disabled={loading}>
        {#if loading}
          {mode === "signup" ? "Creating account…" : "Logging in…"}
        {:else}
          {mode === "signup" ? "Create account" : "Log in"}
        {/if}
      </button>
    </form>
  </div>
</div>

<style>
  .auth-screen {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    background: var(--main-bg);
  }

  .auth-card {
    width: 100%;
    max-width: 420px;
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
  }

  .auth-header {
    text-align: center;
    margin-bottom: 1.25rem;
  }

  .auth-header h1 {
    margin: 0 0 0.35rem;
    font-size: 1.5rem;
    color: var(--text);
  }

  .auth-header p {
    margin: 0;
    font-size: 0.88rem;
    color: var(--text-muted);
  }

  .mode-tabs {
    display: flex;
    gap: 0.35rem;
    margin-bottom: 1.25rem;
    padding: 0.2rem;
    background: var(--input-bg);
    border-radius: 8px;
  }

  .mode-tab {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.45rem 0;
    border-radius: 6px;
    cursor: pointer;
  }

  .mode-tab.active {
    background: var(--panel-bg);
    color: var(--text);
  }

  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .field span {
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  .field input,
  .field textarea {
    width: 100%;
    padding: 0.45rem 0.65rem;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--input-bg);
    color: var(--text);
    font-family: inherit;
    font-size: 0.88rem;
    outline: none;
    box-sizing: border-box;
  }

  .field input:focus,
  .field textarea:focus {
    border-color: var(--accent);
  }

  .field textarea {
    resize: vertical;
    min-height: 90px;
    line-height: 1.5;
  }

  .level-row {
    display: flex;
    gap: 0.35rem;
  }

  .level-btn {
    flex: 1;
    padding: 0.4rem 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: transparent;
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.78rem;
    cursor: pointer;
  }

  .level-btn.selected {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--hover-bg);
  }

  .error {
    margin: 0;
    font-size: 0.82rem;
    color: #f87171;
    line-height: 1.4;
  }

  .submit-btn {
    margin-top: 0.25rem;
    padding: 0.55rem 1rem;
    border: none;
    border-radius: 8px;
    background: var(--accent);
    color: #fff;
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
  }

  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

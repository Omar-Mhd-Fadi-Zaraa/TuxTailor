<script>
  import { createEventDispatcher } from "svelte";
  import { UpdateChat } from "../../wailsjs/go/main/App.js";
  import { chats } from "../stores/chats.js";
  import { settings } from "../stores/settings.js";

  export let chatId;

  const dispatch = createEventDispatcher();

  $: chat = $chats.find((c) => c.id === chatId) ?? null;

  let localTitle = "";
  let localSystemPrompt = "";
  let initializedFor = null;
  let error = "";
  let saving = false;

  $: if (chat && chatId !== initializedFor) {
    initializedFor = chatId;
    localTitle = chat.title;
    localSystemPrompt = chat.systemPrompt || "";
  }

  function close() {
    dispatch("close");
  }

  async function save() {
    if (!chat || saving) return;

    const title = localTitle.trim() || "New Chat";
    const systemPrompt = localSystemPrompt.trim();
    saving = true;
    error = "";

    try {
      chats.updateChatMeta(chat.id, { title, systemPrompt });

      if (chat.backendId !== null) {
        await UpdateChat(
          chat.backendId,
          title,
          systemPrompt,
          $settings.backendUrl
        );
      }

      close();
    } catch (e) {
      error = e?.message || String(e);
    } finally {
      saving = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === "Escape") {
      e.preventDefault();
      close();
    }
  }

  function stopPropagation(e) {
    e.stopPropagation();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="overlay" on:click|self={close}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal" role="dialog" aria-label="Edit chat" on:click={stopPropagation}>
    <div class="modal-header">
      <h2>Edit chat</h2>
      <button class="close-btn" on:click={close} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <div class="modal-body">
      {#if chat?.backendId === null}
        <p class="hint">This chat will be saved to the server when you send the first message.</p>
      {/if}

      <label class="field">
        <span>Title</span>
        <input type="text" bind:value={localTitle} disabled={saving} />
      </label>

      <label class="field">
        <span>Chat system prompt</span>
        <textarea
          bind:value={localSystemPrompt}
          rows="6"
          placeholder="Optional instructions for this chat only"
          disabled={saving}
        ></textarea>
      </label>

      {#if error}
        <p class="error">{error}</p>
      {/if}
    </div>

    <div class="modal-footer">
      <button class="cancel-btn" on:click={close} disabled={saving}>Cancel</button>
      <button class="save-btn" on:click={save} disabled={saving}>
        {saving ? "Saving…" : "Save"}
      </button>
    </div>
  </div>
</div>

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    z-index: 110;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal {
    width: 460px;
    max-width: calc(100vw - 2rem);
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem 0.75rem;
    border-bottom: 1px solid var(--border);
  }

  .modal-header h2 {
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
  }

  .close-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  .modal-body {
    padding: 1.1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  .hint {
    margin: 0;
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.45;
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
    line-height: 1.5;
    min-height: 120px;
  }

  .error {
    margin: 0;
    font-size: 0.82rem;
    color: #f87171;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    border-top: 1px solid var(--border);
  }

  .cancel-btn,
  .save-btn {
    padding: 0.4rem 1rem;
    border-radius: 7px;
    font-family: inherit;
    font-size: 0.87rem;
    font-weight: 600;
    cursor: pointer;
  }

  .cancel-btn {
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
  }

  .save-btn {
    border: none;
    background: var(--accent);
    color: #fff;
  }

  .save-btn:disabled,
  .cancel-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

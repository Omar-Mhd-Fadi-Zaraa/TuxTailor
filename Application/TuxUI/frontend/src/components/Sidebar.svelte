<script>
  import { chats, activeChatId } from "../stores/chats.js";

  export let onOpenSettings;

  function handleNewChat() {
    const id = $chats.length > 0 ? null : null;
    const newId = chats.newChat();
    activeChatId.set(newId);
  }

  function handleDeleteChat(e, chatId) {
    e.stopPropagation();
    chats.deleteChat(chatId);
    if ($activeChatId === chatId) {
      const remaining = $chats.filter((c) => c.id !== chatId);
      activeChatId.set(remaining.length > 0 ? remaining[remaining.length - 1].id : null);
    }
  }
</script>

<aside class="sidebar">
  <div class="sidebar-header">
    <button class="icon-btn" title="Settings" on:click={onOpenSettings}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    </button>
    <span class="app-name">TuxTailor</span>
  </div>

  <div class="chat-list">
    {#if $chats.length === 0}
      <p class="empty-hint">No chats yet.</p>
    {/if}
    {#each [...$chats].reverse() as chat (chat.id)}
      <button
        class="chat-item"
        class:active={$activeChatId === chat.id}
        on:click={() => activeChatId.set(chat.id)}
      >
        <span class="chat-item-title">{chat.title}</span>
        <button
          class="delete-btn"
          title="Delete"
          on:click={(e) => handleDeleteChat(e, chat.id)}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </button>
    {/each}
  </div>

  <div class="sidebar-footer">
    <button class="new-chat-btn" on:click={handleNewChat}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      New Chat
    </button>
  </div>
</aside>

<style>
  .sidebar {
    width: 240px;
    flex-shrink: 0;
    background: var(--sidebar-bg);
    display: flex;
    flex-direction: column;
    height: 100vh;
    border-right: 1px solid var(--border);
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.9rem 0.75rem;
    border-bottom: 1px solid var(--border);
  }

  .app-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .icon-btn {
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
    flex-shrink: 0;
    transition: background 0.12s, color 0.12s;
  }

  .icon-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  .chat-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.4rem 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .empty-hint {
    font-size: 0.78rem;
    color: var(--text-faint);
    text-align: center;
    padding: 1rem 0;
    margin: 0;
  }

  .chat-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.45rem 0.6rem;
    border: none;
    background: transparent;
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    font-size: 0.83rem;
    transition: background 0.1s, color 0.1s;
    gap: 0.4rem;
  }

  .chat-item:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  .chat-item.active {
    background: var(--active-bg);
    color: var(--text);
  }

  .chat-item-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .delete-btn {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border: none;
    background: transparent;
    color: var(--text-faint);
    border-radius: 3px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.1s, background 0.1s;
    padding: 0;
  }

  .chat-item:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  .sidebar-footer {
    padding: 0.6rem 0.75rem;
    border-top: 1px solid var(--border);
  }

  .new-chat-btn {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    border-radius: 7px;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.83rem;
    transition: background 0.12s, color 0.12s, border-color 0.12s;
  }

  .new-chat-btn:hover {
    background: var(--hover-bg);
    color: var(--text);
    border-color: var(--border-strong);
  }
</style>

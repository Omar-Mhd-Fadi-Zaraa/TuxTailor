<script>
  import { onMount, onDestroy } from "svelte";
  import { chats, activeChatId } from "../stores/chats.js";
  import { auth } from "../stores/auth.js";
  import ChatEditModal from "./ChatEditModal.svelte";

  export let onOpenSettings;
  export let onLogout;

  let editingChatId = null;

  function handleNewChat() {
    const newId = chats.newLocalChat();
    activeChatId.set(newId);
  }

  function handleDeleteChat(e, chatId) {
    e.stopPropagation();
    chats.deleteChat(chatId);
    if ($activeChatId === chatId) {
      const remaining = $chats.filter((c) => c.id !== chatId);
      activeChatId.set(remaining.length > 0 ? remaining[remaining.length - 1].id : null);
    }
    if (editingChatId === chatId) {
      editingChatId = null;
    }
  }

  function openEditChat(e, chatId) {
    e.stopPropagation();
    activeChatId.set(chatId);
    editingChatId = chatId;
  }

  function handleKeydown(e) {
    if (editingChatId) return;
    if (e.key === "F2" && $activeChatId) {
      e.preventDefault();
      editingChatId = $activeChatId;
    }
  }

  onMount(() => {
    window.addEventListener("keydown", handleKeydown);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeydown);
  });
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
    <button class="icon-btn logout-btn" title="Log out" on:click={onLogout}>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
        <polyline points="16 17 21 12 16 7"/>
        <line x1="21" y1="12" x2="9" y2="12"/>
      </svg>
    </button>
  </div>

  <div class="user-line" title={$auth.userName}>
    {$auth.userName}
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
          class="menu-btn"
          title="Edit chat (F2)"
          on:click={(e) => openEditChat(e, chat.id)}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="5" cy="12" r="2"/>
            <circle cx="12" cy="12" r="2"/>
            <circle cx="19" cy="12" r="2"/>
          </svg>
        </button>
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

{#if editingChatId}
  <ChatEditModal chatId={editingChatId} on:close={() => (editingChatId = null)} />
{/if}

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
    flex: 1;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .user-line {
    padding: 0.45rem 0.85rem;
    font-size: 0.78rem;
    color: var(--text-faint);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
    gap: 0.35rem;
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

  .menu-btn,
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

  .chat-item:hover .menu-btn,
  .chat-item:hover .delete-btn {
    opacity: 1;
  }

  .menu-btn:hover,
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

  .new-chat-btn:hover:not(:disabled) {
    background: var(--hover-bg);
    color: var(--text);
    border-color: var(--border-strong);
  }

  .new-chat-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>

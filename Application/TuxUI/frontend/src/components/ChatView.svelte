<script>
  import { onMount, onDestroy, tick } from "svelte";
  import { EventsOn, EventsOff } from "../../wailsjs/runtime/runtime.js";
  import { StreamMessage } from "../../wailsjs/go/main/App.js";
  import { chats, activeChatId, activeChat, ensureActiveChat } from "../stores/chats.js";
  import MessageItem from "./MessageItem.svelte";

  let input = "";
  let loading = false;
  let messageListEl;

  // Track the in-flight assistant message id so events can target it
  let pendingMsgId = null;
  let pendingChatId = null;

  async function scrollToBottom() {
    await tick();
    if (messageListEl) {
      messageListEl.scrollTop = messageListEl.scrollHeight;
    }
  }

  async function send() {
    const query = input.trim();
    if (!query || loading) return;

    const chatId = ensureActiveChat();
    input = "";
    loading = true;

    chats.addUserMessage(chatId, query);
    const msgId = chats.startAssistantMessage(chatId);
    pendingMsgId = msgId;
    pendingChatId = chatId;

    await scrollToBottom();

    StreamMessage(chatId, msgId, query);
  }

  function handleKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  // ── Wails event listeners ──────────────────────────────────────────────────

  function onChunk(data) {
    if (!data || data.chatId !== pendingChatId || data.msgId !== pendingMsgId) return;
    chats.appendChunk(data.chatId, data.msgId, data.type, data.content);
    scrollToBottom();
  }

  function onMedia(data) {
    if (!data || data.chatId !== pendingChatId || data.msgId !== pendingMsgId) return;
    chats.appendMedia(data.chatId, data.msgId, data.mediaType, data.url, data.alt);
    scrollToBottom();
  }

  function onConfirmation(data) {
    if (!data || data.chatId !== pendingChatId || data.msgId !== pendingMsgId) return;
    chats.appendConfirmation(data.chatId, data.msgId, data.prompt, data.options);
    scrollToBottom();
  }

  function onDone(data) {
    if (!data || data.chatId !== pendingChatId || data.msgId !== pendingMsgId) return;
    chats.finishStream(data.chatId, data.msgId);
    loading = false;
    pendingMsgId = null;
    pendingChatId = null;
    scrollToBottom();
  }

  function onError(data) {
    if (!data || data.chatId !== pendingChatId || data.msgId !== pendingMsgId) return;
    chats.markError(data.chatId, data.msgId, data.message);
    loading = false;
    pendingMsgId = null;
    pendingChatId = null;
    scrollToBottom();
  }

  onMount(() => {
    EventsOn("chat:chunk", onChunk);
    EventsOn("chat:media", onMedia);
    EventsOn("chat:confirmation", onConfirmation);
    EventsOn("chat:done", onDone);
    EventsOn("chat:error", onError);
  });

  onDestroy(() => {
    EventsOff("chat:chunk");
    EventsOff("chat:media");
    EventsOff("chat:confirmation");
    EventsOff("chat:done");
    EventsOff("chat:error");
  });

  // Auto-scroll when active chat changes
  $: if ($activeChat) scrollToBottom();
</script>

<div class="chat-view">
  {#if $activeChat === null}
    <div class="no-chat">
      <p>Select a chat or create a new one.</p>
    </div>
  {:else}
    <div class="message-list" bind:this={messageListEl}>
      {#if $activeChat.messages.length === 0}
        <div class="empty-state">
          <p>Ask me anything about your Linux configuration.</p>
        </div>
      {:else}
        <div class="messages-inner">
          {#each $activeChat.messages as msg (msg.id)}
            <MessageItem message={msg} chatId={$activeChat.id} />
          {/each}
        </div>
      {/if}
    </div>

    <div class="input-area">
      <div class="input-wrap">
        <textarea
          class="chat-input"
          placeholder="Message TuxTailor…"
          rows="1"
          bind:value={input}
          on:keydown={handleKeydown}
          disabled={loading}
        ></textarea>
        <button
          class="send-btn"
          on:click={send}
          disabled={loading || !input.trim()}
          title="Send"
        >
          {#if loading}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
          {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="19" x2="12" y2="5"/>
              <polyline points="5 12 12 5 19 12"/>
            </svg>
          {/if}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .chat-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .no-chat {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-faint);
    font-size: 0.88rem;
  }

  /* ── Message list ── */
  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: 2rem 1rem 1rem;
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-faint);
    font-size: 0.9rem;
    text-align: center;
    user-select: none;
  }

  .messages-inner {
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  /* ── Input area ── */
  .input-area {
    padding: 0.75rem 1rem 1rem;
    background: var(--main-bg);
  }

  .input-wrap {
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    background: var(--input-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.45rem 0.5rem 0.45rem 0.85rem;
    transition: border-color 0.15s;
  }

  .input-wrap:focus-within {
    border-color: var(--border-strong);
  }

  .chat-input {
    flex: 1;
    resize: none;
    border: none;
    background: transparent;
    color: var(--text);
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.55;
    outline: none;
    max-height: 10rem;
    overflow-y: auto;
    padding: 0.2rem 0;
  }

  .chat-input::placeholder {
    color: var(--text-faint);
  }

  .chat-input:disabled {
    opacity: 0.5;
  }

  .send-btn {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    background: var(--accent);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: opacity 0.15s;
    padding: 0;
  }

  .send-btn:hover:not(:disabled) {
    opacity: 0.85;
  }

  .send-btn:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }
</style>

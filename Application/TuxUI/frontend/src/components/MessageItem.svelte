<script>
  import { chats } from "../stores/chats.js";
  import { SendConfirmation } from "../../wailsjs/go/main/App.js";
  import Markdown from "./Markdown.svelte";

  export let message;
  export let chatId;

  function toggleThinking(partIndex) {
    chats.toggleThinking(chatId, message.id, partIndex);
  }

  async function handleConfirm(partIndex, option) {
    chats.resolveConfirmation(chatId, message.id, partIndex, option);
    try {
      await SendConfirmation(chatId, message.id, option);
    } catch (e) {
      console.error("SendConfirmation failed:", e);
    }
  }
</script>

<div class="message {message.role}" class:error={message.error}>
  {#if message.role === "assistant"}
    <div class="avatar assistant-avatar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
      </svg>
    </div>
  {/if}

  <div class="message-body">
    {#each message.parts as part, i}
      {#if part.type === "text"}
        {#if message.role === "assistant"}
          <div class="text-part markdown-part">
            <Markdown source={part.content} />
          </div>
        {:else}
          <div class="text-part">{part.content}</div>
        {/if}

      {:else if part.type === "thinking"}
        <div class="thinking-block" class:collapsed={part.collapsed}>
          <button class="thinking-toggle" on:click={() => toggleThinking(i)}>
            <svg
              class="chevron"
              class:rotated={!part.collapsed}
              width="12" height="12" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
            >
              <polyline points="6 9 12 15 18 9"/>
            </svg>
            <span>Thinking</span>
            {#if message.streaming && !part.collapsed}
              <span class="thinking-dots"><span/><span/><span/></span>
            {/if}
          </button>
          {#if !part.collapsed}
            <div class="thinking-content">{part.content}</div>
          {/if}
        </div>

      {:else if part.type === "media"}
        <div class="media-part">
          {#if part.mediaType === "image"}
            <img src={part.url} alt={part.alt || "image"} class="media-image" />
          {:else if part.mediaType === "audio"}
            <!-- svelte-ignore a11y-media-has-caption -->
            <audio controls src={part.url} class="media-audio" />
          {:else if part.mediaType === "video"}
            <!-- svelte-ignore a11y-media-has-caption -->
            <video controls src={part.url} class="media-video" />
          {/if}
        </div>

      {:else if part.type === "confirmation"}
        <div class="confirmation-block">
          <p class="confirmation-prompt">{part.prompt}</p>
          <div class="confirmation-options">
            {#if part.resolved !== null}
              <span class="resolved-choice">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                {part.resolved}
              </span>
            {:else}
              {#each part.options as option}
                <button
                  class="confirm-btn"
                  on:click={() => handleConfirm(i, option)}
                >{option}</button>
              {/each}
            {/if}
          </div>
        </div>
      {/if}
    {/each}

    {#if message.streaming && message.parts.length === 0}
      <div class="typing-indicator"><span/><span/><span/></div>
    {/if}
  </div>
</div>

<style>
  .message {
    display: flex;
    gap: 0.75rem;
    padding: 0.6rem 0;
    width: 100%;
  }

  .message.user {
    flex-direction: row-reverse;
  }

  /* ── Avatar ── */
  .avatar {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
  }

  .assistant-avatar {
    background: var(--accent);
    color: #fff;
  }

  /* ── Message body ── */
  .message-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 0;
    max-width: 100%;
  }

  .message.user .message-body {
    align-items: flex-end;
    max-width: 72%;
  }

  .message.assistant .message-body {
    align-items: flex-start;
    max-width: 100%;
  }

  /* ── Text ── */
  .text-part {
    font-size: 0.9rem;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .markdown-part {
    white-space: normal;
    width: 100%;
  }

  .message.user .text-part {
    background: var(--user-msg-bg);
    color: var(--user-msg-text);
    padding: 0.5rem 0.85rem;
    border-radius: 16px 16px 4px 16px;
  }

  .message.assistant .text-part {
    color: var(--text);
  }

  .message.error .text-part {
    color: #f87171;
  }

  /* ── Thinking block ── */
  .thinking-block {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    background: var(--thinking-bg);
  }

  .thinking-toggle {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    width: 100%;
    padding: 0.45rem 0.7rem;
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.78rem;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    letter-spacing: 0.02em;
    transition: color 0.1s;
  }

  .thinking-toggle:hover {
    color: var(--text);
  }

  .chevron {
    transition: transform 0.2s;
    flex-shrink: 0;
  }

  .chevron.rotated {
    transform: rotate(180deg);
  }

  .thinking-content {
    padding: 0.5rem 0.75rem 0.65rem;
    font-size: 0.8rem;
    line-height: 1.6;
    color: var(--thinking-text);
    font-family: "Menlo", "Monaco", "Consolas", monospace;
    white-space: pre-wrap;
    border-top: 1px solid var(--border);
  }

  /* Thinking streaming dots */
  .thinking-dots {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    margin-left: 2px;
  }

  .thinking-dots span {
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--text-faint);
    animation: dot-pulse 1.2s infinite ease-in-out;
  }

  .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
  .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

  /* ── Media ── */
  .media-part {
    max-width: 100%;
  }

  .media-image {
    max-width: 480px;
    width: 100%;
    border-radius: 8px;
    display: block;
  }

  .media-audio {
    width: 100%;
    max-width: 380px;
    accent-color: var(--accent);
  }

  .media-video {
    max-width: 480px;
    width: 100%;
    border-radius: 8px;
  }

  /* ── Confirmation ── */
  .confirmation-block {
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    background: var(--thinking-bg);
  }

  .confirmation-prompt {
    margin: 0 0 0.6rem;
    font-size: 0.87rem;
    color: var(--text);
    line-height: 1.5;
  }

  .confirmation-options {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }

  .confirm-btn {
    padding: 0.35rem 0.85rem;
    border: 1px solid var(--accent);
    border-radius: 6px;
    background: transparent;
    color: var(--accent);
    font-family: inherit;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
  }

  .confirm-btn:hover {
    background: var(--accent);
    color: #fff;
  }

  .resolved-choice {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.82rem;
    color: var(--text-muted);
    padding: 0.35rem 0;
  }

  /* ── Generic typing indicator (no parts yet) ── */
  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 0.2rem 0;
  }

  .typing-indicator span {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--text-faint);
    animation: dot-pulse 1.2s infinite ease-in-out;
  }

  .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
  .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

  @keyframes dot-pulse {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30%            { transform: translateY(-4px); opacity: 1; }
  }
</style>

import { writable, derived, get } from "svelte/store";

let _nextId = 1;
const uid = () => String(_nextId++);

/**
 * Part shapes:
 *   { type: "text",         content: string }
 *   { type: "thinking",     content: string, collapsed: boolean }
 *   { type: "media",        mediaType: "audio"|"video"|"image", url: string, alt?: string }
 *   { type: "confirmation", prompt: string, options: string[], resolved: string|null }
 *
 * Message shape:
 *   { id, role: "user"|"assistant", parts: Part[], streaming: boolean }
 *
 * Chat shape:
 *   { id, title: string, messages: Message[], createdAt: number }
 */

function createChatsStore() {
  const { subscribe, update, set } = writable([]);

  function newChat() {
    const id = uid();
    update((chats) => [
      ...chats,
      { id, title: "New Chat", messages: [], createdAt: Date.now() },
    ]);
    return id;
  }

  function deleteChat(chatId) {
    update((chats) => chats.filter((c) => c.id !== chatId));
  }

  function addUserMessage(chatId, text) {
    const msgId = uid();
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        const messages = [
          ...c.messages,
          {
            id: msgId,
            role: "user",
            parts: [{ type: "text", content: text }],
            streaming: false,
          },
        ];
        // Use first user message as chat title if still default
        const title =
          c.title === "New Chat" ? text.slice(0, 40) || "New Chat" : c.title;
        return { ...c, title, messages };
      })
    );
    return msgId;
  }

  function startAssistantMessage(chatId) {
    const msgId = uid();
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: [
            ...c.messages,
            { id: msgId, role: "assistant", parts: [], streaming: true },
          ],
        };
      })
    );
    return msgId;
  }

  function appendChunk(chatId, msgId, type, content) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            const parts = [...m.parts];
            const last = parts[parts.length - 1];
            // Merge into the last part of the same type if it exists
            if (last && last.type === type && type !== "confirmation") {
              parts[parts.length - 1] = {
                ...last,
                content: last.content + content,
              };
            } else {
              const newPart =
                type === "thinking"
                  ? { type, content, collapsed: false }
                  : { type, content };
              parts.push(newPart);
            }
            return { ...m, parts };
          }),
        };
      })
    );
  }

  function appendMedia(chatId, msgId, mediaType, url, alt) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            return {
              ...m,
              parts: [...m.parts, { type: "media", mediaType, url, alt }],
            };
          }),
        };
      })
    );
  }

  function appendConfirmation(chatId, msgId, prompt, options) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            return {
              ...m,
              parts: [
                ...m.parts,
                { type: "confirmation", prompt, options, resolved: null },
              ],
            };
          }),
        };
      })
    );
  }

  function resolveConfirmation(chatId, msgId, partIndex, option) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            const parts = m.parts.map((p, i) =>
              i === partIndex ? { ...p, resolved: option } : p
            );
            return { ...m, parts };
          }),
        };
      })
    );
  }

  function finishStream(chatId, msgId) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            // Collapse all thinking blocks once stream is done
            const parts = m.parts.map((p) =>
              p.type === "thinking" ? { ...p, collapsed: true } : p
            );
            return { ...m, parts, streaming: false };
          }),
        };
      })
    );
  }

  function toggleThinking(chatId, msgId, partIndex) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            const parts = m.parts.map((p, i) =>
              i === partIndex ? { ...p, collapsed: !p.collapsed } : p
            );
            return { ...m, parts };
          }),
        };
      })
    );
  }

  function markError(chatId, msgId, errorText) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          messages: c.messages.map((m) => {
            if (m.id !== msgId) return m;
            return {
              ...m,
              streaming: false,
              parts: [
                ...m.parts,
                { type: "text", content: `Error: ${errorText}` },
              ],
              error: true,
            };
          }),
        };
      })
    );
  }

  return {
    subscribe,
    set,
    newChat,
    deleteChat,
    addUserMessage,
    startAssistantMessage,
    appendChunk,
    appendMedia,
    appendConfirmation,
    resolveConfirmation,
    finishStream,
    toggleThinking,
    markError,
  };
}

export const chats = createChatsStore();

export const activeChatId = writable(null);

export const activeChat = derived(
  [chats, activeChatId],
  ([$chats, $activeChatId]) =>
    $chats.find((c) => c.id === $activeChatId) ?? null
);

// Convenience: ensure there's always at least one chat and it's active
export function ensureActiveChat() {
  const current = get(activeChatId);
  const all = get(chats);
  if (current && all.find((c) => c.id === current)) return current;
  const id = chats.newChat();
  activeChatId.set(id);
  return id;
}

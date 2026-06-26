import { writable, derived, get } from "svelte/store";

let _nextMsgId = 1;
let _nextLocalId = 1;
const uid = () => String(_nextMsgId++);
const localId = () => `local-${_nextLocalId++}`;

/**
 * Chat shape:
 *   { id, backendId, title, systemPrompt, messages, createdAt }
 *   backendId is null until the first message is sent
 */

function createChatsStore() {
  const { subscribe, update, set } = writable([]);

  function newLocalChat() {
    const id = localId();
    update((chats) => [
      ...chats,
      {
        id,
        backendId: null,
        title: "New Chat",
        systemPrompt: "",
        messages: [],
        createdAt: Date.now(),
      },
    ]);
    return id;
  }

  function registerChat(backendChatId, title, systemPrompt = "") {
    const id = String(backendChatId);
    update((chats) => {
      if (chats.some((c) => c.id === id)) {
        return chats.map((c) =>
          c.id === id ? { ...c, title, systemPrompt, backendId: backendChatId } : c
        );
      }
      return [
        ...chats,
        {
          id,
          backendId: backendChatId,
          title: title || "New Chat",
          systemPrompt: systemPrompt || "",
          messages: [],
          createdAt: Date.now(),
        },
      ];
    });
    return id;
  }

  function promoteChat(localChatId, backendChatId, title, systemPrompt) {
    const newId = String(backendChatId);
    let promoted = false;
    update((chats) =>
      chats.map((c) => {
        if (c.id !== localChatId) return c;
        promoted = true;
        return {
          ...c,
          id: newId,
          backendId: backendChatId,
          title,
          systemPrompt: systemPrompt ?? c.systemPrompt,
        };
      })
    );
    return promoted ? newId : localChatId;
  }

  function deleteChat(chatId) {
    update((chats) => chats.filter((c) => c.id !== chatId));
  }

  function updateChatMeta(chatId, { title, systemPrompt }) {
    update((chats) =>
      chats.map((c) => {
        if (c.id !== chatId) return c;
        return {
          ...c,
          ...(title !== undefined ? { title } : {}),
          ...(systemPrompt !== undefined ? { systemPrompt } : {}),
        };
      })
    );
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

  function clear() {
    set([]);
  }

  return {
    subscribe,
    set,
    newLocalChat,
    registerChat,
    promoteChat,
    deleteChat,
    updateChatMeta,
    addUserMessage,
    startAssistantMessage,
    appendChunk,
    appendMedia,
    appendConfirmation,
    resolveConfirmation,
    finishStream,
    toggleThinking,
    markError,
    clear,
  };
}

export const chats = createChatsStore();

export const activeChatId = writable(null);

export const activeChat = derived(
  [chats, activeChatId],
  ([$chats, $activeChatId]) =>
    $chats.find((c) => c.id === $activeChatId) ?? null
);

export function ensureActiveChat() {
  const current = get(activeChatId);
  const all = get(chats);
  if (current && all.find((c) => c.id === current)) return current;
  if (all.length > 0) {
    const id = all[all.length - 1].id;
    activeChatId.set(id);
    return id;
  }
  const id = chats.newLocalChat();
  activeChatId.set(id);
  return id;
}

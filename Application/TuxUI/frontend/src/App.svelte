<script>
  import { get } from "svelte/store";
  import Sidebar from "./components/Sidebar.svelte";
  import ChatView from "./components/ChatView.svelte";
  import SettingsMenu from "./components/SettingsMenu.svelte";
  import AuthView from "./components/AuthView.svelte";
  import { FetchUserChats } from "../wailsjs/go/main/App.js";
  import { activeChatId, chats } from "./stores/chats.js";
  import { settings } from "./stores/settings.js";
  import { auth, isAuthenticated } from "./stores/auth.js";

  let settingsOpen = false;

  $: {
    const theme = $settings.theme;
    document.body.className = theme === "default" ? "" : `theme-${theme}`;
  }

  async function loadUserChatsFromBackend(userId) {
    chats.clear();
    try {
      const payload = await FetchUserChats(userId, get(settings).backendUrl);
      if (payload && Object.keys(payload).length > 0) {
        chats.loadUserChats(payload);
      }
    } catch (e) {
      console.error("Failed to load user chats:", e);
    }
  }

  async function bootstrapChats() {
    if (get(chats).length > 0) {
      if (!get(activeChatId)) {
        activeChatId.set(get(chats)[get(chats).length - 1].id);
      }
      return;
    }

    const id = chats.newLocalChat();
    activeChatId.set(id);
  }

  async function handleAuthenticated(event) {
    const userId = event.detail?.userId ?? get(auth).userId;
    if (userId) {
      await loadUserChatsFromBackend(userId);
    }
    await bootstrapChats();
  }

  async function handleLogout() {
    chats.clear();
    activeChatId.set(null);
    auth.logout();
  }
</script>

{#if $isAuthenticated}
  <div class="layout">
    <Sidebar
      onOpenSettings={() => (settingsOpen = true)}
      onLogout={handleLogout}
    />
    <ChatView />
  </div>

  {#if settingsOpen}
    <SettingsMenu
      onClose={() => (settingsOpen = false)}
      onLogout={handleLogout}
    />
  {/if}
{:else}
  <AuthView on:authenticated={handleAuthenticated} />
{/if}

<style>
  .layout {
    display: flex;
    height: 100vh;
    width: 100%;
    overflow: hidden;
    background: var(--main-bg);
  }
</style>

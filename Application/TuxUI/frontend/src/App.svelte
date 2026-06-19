<script>
  import { onMount } from "svelte";
  import Sidebar from "./components/Sidebar.svelte";
  import ChatView from "./components/ChatView.svelte";
  import SettingsMenu from "./components/SettingsMenu.svelte";
  import { activeChatId, chats } from "./stores/chats.js";
  import { settings } from "./stores/settings.js";

  let settingsOpen = false;

  // Apply theme class to body whenever the setting changes
  $: {
    const theme = $settings.theme;
    document.body.className = theme === "default" ? "" : `theme-${theme}`;
  }

  onMount(() => {
    if ($chats.length === 0) {
      const id = chats.newChat();
      activeChatId.set(id);
    }
  });
</script>

<div class="layout">
  <Sidebar onOpenSettings={() => (settingsOpen = true)} />
  <ChatView />
</div>

{#if settingsOpen}
  <SettingsMenu onClose={() => (settingsOpen = false)} />
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

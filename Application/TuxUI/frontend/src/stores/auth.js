import { writable, derived, get } from "svelte/store";

function createAuthStore() {
  const { subscribe, set } = writable({ userId: null, userName: "" });

  function login(userId, userName) {
    const next = { userId, userName: userName.trim() };
    set(next);
    return next;
  }

  function logout() {
    const next = { userId: null, userName: "" };
    set(next);
    return next;
  }

  return { subscribe, set, login, logout };
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, ($auth) => Boolean($auth.userId));

export function getUserId() {
  return get(auth).userId;
}

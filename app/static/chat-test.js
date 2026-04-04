const storageKey = 'chatTesterState';

const state = {
  socket: null,
  token: '',
  me: null,
  chats: [],
  activeChat: null,
  messages: [],
  lastReadMessage: null,
};

const els = {
  baseUrl: document.querySelector('#baseUrl'),
  email: document.querySelector('#email'),
  password: document.querySelector('#password'),
  token: document.querySelector('#token'),
  recipientGuid: document.querySelector('#recipientGuid'),
  connectionBadge: document.querySelector('#connectionBadge'),
  currentUserCard: document.querySelector('#currentUserCard'),
  chatList: document.querySelector('#chatList'),
  messages: document.querySelector('#messages'),
  activeChatTitle: document.querySelector('#activeChatTitle'),
  activeChatMeta: document.querySelector('#activeChatMeta'),
  messageInput: document.querySelector('#messageInput'),
  logOutput: document.querySelector('#logOutput'),
  loginBtn: document.querySelector('#loginBtn'),
  loadProfileBtn: document.querySelector('#loadProfileBtn'),
  connectBtn: document.querySelector('#connectBtn'),
  disconnectBtn: document.querySelector('#disconnectBtn'),
  loadChatsBtn: document.querySelector('#loadChatsBtn'),
  loadMessagesBtn: document.querySelector('#loadMessagesBtn'),
  sendBtn: document.querySelector('#sendBtn'),
  typingBtn: document.querySelector('#typingBtn'),
  markReadBtn: document.querySelector('#markReadBtn'),
  clearLogBtn: document.querySelector('#clearLogBtn'),
  createChatBtn: document.querySelector('#createChatBtn'),
  copyUserGuidBtn: document.querySelector('#copyUserGuidBtn'),
};

function normalizeBaseUrl(url) {
  if (!url) {
    return `${window.location.protocol}//${window.location.host}`;
  }
  return url.replace(/\/$/, '');
}

function wsUrlFromBaseUrl(baseUrl, token) {
  const wsProtocol = baseUrl.startsWith('https://') ? 'wss://' : 'ws://';
  const host = baseUrl.replace(/^https?:\/\//, '');
  return `${wsProtocol}${host}/api/v1/ws/?token=${encodeURIComponent(token)}`;
}

function persistState() {
  const payload = {
    baseUrl: els.baseUrl.value.trim(),
    email: els.email.value.trim(),
    token: els.token.value.trim(),
    recipientGuid: els.recipientGuid.value.trim(),
    activeChatGuid: state.activeChat?.chat_guid || null,
  };
  localStorage.setItem(storageKey, JSON.stringify(payload));
}

function restoreState() {
  const raw = localStorage.getItem(storageKey);
  if (!raw) {
    els.baseUrl.value = `${window.location.protocol}//${window.location.host}`;
    return;
  }

  try {
    const parsed = JSON.parse(raw);
    els.baseUrl.value =
      parsed.baseUrl || `${window.location.protocol}//${window.location.host}`;
    els.email.value = parsed.email || '';
    els.token.value = parsed.token || '';
    els.recipientGuid.value = parsed.recipientGuid || '';
  } catch {
    els.baseUrl.value = `${window.location.protocol}//${window.location.host}`;
  }
}

function setBadge(status, label) {
  els.connectionBadge.textContent = label;
  els.connectionBadge.className = `badge badge-${status}`;
}

function log(label, payload) {
  const ts = new Date().toLocaleTimeString('vi-VN', { hour12: false });
  const line =
    payload === undefined
      ? `[${ts}] ${label}`
      : `[${ts}] ${label}\n${typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2)}`;
  els.logOutput.textContent = `${line}\n\n${els.logOutput.textContent}`;
}

function safeParse(data) {
  if (typeof data !== 'string') {
    return data;
  }
  try {
    return JSON.parse(data);
  } catch {
    return data;
  }
}

function authHeaders() {
  const token = els.token.value.trim();
  if (!token) {
    throw new Error('Thiếu access token');
  }
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

async function apiFetch(path, options = {}) {
  const baseUrl = normalizeBaseUrl(els.baseUrl.value.trim());
  persistState();
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...authHeaders(),
    },
  });
  const data = await response.json();
  if (data.is_success === false) {
    throw new Error(data.message || data.message_en || 'Request failed');
  }
  return data.data ?? data;
}

function renderCurrentUser() {
  if (!state.me) {
    els.currentUserCard.className = 'info-card empty';
    els.currentUserCard.textContent = 'Chưa tải thông tin user.';
    return;
  }

  els.currentUserCard.className = 'info-card';
  els.currentUserCard.innerHTML = [
    `<strong>${state.me.name || state.me.username || 'Unknown'}</strong>`,
    `<div>${state.me.email || ''}</div>`,
    `<div><small>GUID: ${state.me.guid}</small></div>`,
    `<div><small>Roles: ${(state.me.roles || []).join(', ') || '-'}</small></div>`,
    `<div><small>Permissions: ${(state.me.permissions || []).length}</small></div>`,
  ].join('');
}

function chatDisplayName(chat) {
  if (!chat) {
    return 'Unknown chat';
  }
  const users = Array.isArray(chat.users) ? chat.users : [];
  const friend = users.find((user) => user.guid !== state.me?.guid) || users[0];
  if (!friend) {
    return chat.chat_guid || chat.guid;
  }
  return `${friend.name} · @${friend.username}`;
}

function resolveProfilePicUrl(profilePic) {
  if (!profilePic) {
    return '/static/knitting.png';
  }
  if (
    profilePic.startsWith('http://') ||
    profilePic.startsWith('https://') ||
    profilePic.startsWith('/')
  ) {
    return profilePic;
  }

  return `/uploads/${profilePic.replace(/^uploads\//, '')}`;
}

function setActiveChat(chatGuid) {
  state.activeChat =
    state.chats.find((chat) => chat.chat_guid === chatGuid) || null;
  state.messages = [];
  state.lastReadMessage = null;
  renderChats();
  renderMessages();
  if (!state.activeChat) {
    els.activeChatTitle.textContent = 'Chưa chọn chat';
    els.activeChatMeta.textContent =
      'Chọn một chat để xem lịch sử và gửi message.';
    persistState();
    return;
  }

  els.activeChatTitle.textContent = chatDisplayName(state.activeChat);
  els.activeChatMeta.textContent = `chat_guid: ${state.activeChat.chat_guid} | unread: ${state.activeChat.new_messages_count}`;
  persistState();
}

function renderChats() {
  if (!state.chats.length) {
    els.chatList.className = 'chat-list empty';
    els.chatList.textContent = 'Chưa có chat nào được tải.';
    return;
  }

  els.chatList.className = 'chat-list';
  els.chatList.innerHTML = state.chats
    .map((chat) => {
      const isActive = state.activeChat?.chat_guid === chat.chat_guid;
      return `
      <button class="chat-item ${isActive ? 'active' : ''}" data-chat-guid="${chat.chat_guid}">
        <div class="chat-item-title">
          <strong>${chatDisplayName(chat)}</strong>
          <span class="meta-chip">${chat.new_messages_count} new</span>
        </div>
        <small>${chat.chat_guid}</small>
      </button>
    `;
    })
    .join('');

  els.chatList.querySelectorAll('.chat-item').forEach((button) => {
    button.addEventListener('click', () =>
      setActiveChat(button.dataset.chatGuid),
    );
  });
}

function renderMessages() {
  if (!state.activeChat) {
    els.messages.className = 'messages empty';
    els.messages.textContent = 'Chưa có dữ liệu message.';
    return;
  }

  if (!state.messages.length) {
    els.messages.className = 'messages empty';
    els.messages.textContent =
      'Chat này chưa có message hoặc bạn chưa load lịch sử.';
    return;
  }

  els.messages.className = 'messages';
  els.messages.innerHTML = state.messages
    .map((message) => {
      const mine = message.user_guid === state.me?.guid;
      const displayName = mine
        ? 'You'
        : escapeHtml(message.name || message.username || 'User');
      const avatarUrl = resolveProfilePicUrl(message.profile_pic);
      const avatarAlt = escapeHtml(message.name || message.username || 'User');
      return `
      <div class="message-row ${mine ? 'mine' : ''}">
        <img
          class="message-avatar"
          src="${avatarUrl}"
          alt="${avatarAlt}"
          onerror="this.onerror=null;this.src='/static/knitting.png';"
        />
        <article class="message-bubble">
          <div class="message-meta">
            <strong>${displayName}</strong>
            <small>${new Date(message.created).toLocaleString('vi-VN')}</small>
          </div>
          <p class="message-text">${escapeHtml(message.content || '')}</p>
          <small>${message.message_guid}${message.is_read ? ' | read' : ''}</small>
        </article>
      </div>
    `;
    })
    .join('');
  els.messages.scrollTop = els.messages.scrollHeight;
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function upsertIncomingMessage(message) {
  const index = state.messages.findIndex(
    (item) => item.message_guid === message.message_guid,
  );
  if (index >= 0) {
    state.messages[index] = { ...state.messages[index], ...message };
  } else if (
    !state.activeChat ||
    state.activeChat.chat_guid === message.chat_guid
  ) {
    state.messages.push(message);
  }

  state.messages.sort((a, b) => new Date(a.created) - new Date(b.created));
  renderMessages();
}

function applyMessageReadEvent(event) {
  state.messages = state.messages.map((message) => {
    if (message.user_guid === event.user_guid) {
      return message;
    }

    if (
      new Date(message.created) <= new Date(event.last_read_message_created_at)
    ) {
      return { ...message, is_read: true };
    }

    return message;
  });
  renderMessages();
}

function handleSocketPayload(payload) {
  if (typeof payload === 'string') {
    log('WS raw', payload);
    return;
  }

  log('WS in', payload);

  if (payload.status === 'error') {
    return;
  }

  if (payload.type === 'new') {
    upsertIncomingMessage(payload);
    return;
  }

  if (payload.type === 'message_read') {
    applyMessageReadEvent(payload);
    return;
  }

  if (payload.type === 'user_typing') {
    els.activeChatMeta.textContent = `${chatDisplayName(state.activeChat)} | ${payload.user_guid} is typing...`;
    return;
  }

  if (payload.type === 'new_chat_created') {
    loadChats().catch((error) => log('Load chats failed', error.message));
    return;
  }

  if (payload.type === 'chat_deleted') {
    if (state.activeChat?.chat_guid === payload.chat_guid) {
      setActiveChat(null);
    }
    loadChats().catch((error) => log('Load chats failed', error.message));
  }
}

async function login() {
  const baseUrl = normalizeBaseUrl(els.baseUrl.value.trim());
  const email = els.email.value.trim();
  const password = els.password.value;

  if (!email || !password) {
    throw new Error('Thiếu email hoặc password');
  }

  const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (data.is_success === false) {
    throw new Error(data.message || data.message_en || 'Login failed');
  }

  els.token.value = data.data.access_token;
  state.token = data.data.access_token;
  persistState();
  log('Login success', { email });
}

async function loadProfile() {
  state.me = await apiFetch('/api/v1/users/me');
  renderCurrentUser();
  log('Loaded current user', state.me);
}

async function loadChats() {
  const data = await apiFetch('/api/v1/chat/chats/direct');
  state.chats = data.chats || [];
  renderChats();

  const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
  const preferredGuid = state.activeChat?.chat_guid || saved.activeChatGuid;
  if (preferredGuid) {
    setActiveChat(preferredGuid);
  }

  if (!state.activeChat && state.chats[0]) {
    setActiveChat(state.chats[0].chat_guid);
  }
  log('Loaded chats', data);
}

async function loadMessages() {
  if (!state.activeChat) {
    throw new Error('Chưa chọn chat');
  }

  const data = await apiFetch(
    `/api/v1/chat/${state.activeChat.chat_guid}/messages?size=50`,
  );
  state.messages = data.messages || [];
  state.lastReadMessage = data.last_read_message || null;
  renderMessages();
  log('Loaded messages', data);
}

async function createChat() {
  const recipientUserGuid = els.recipientGuid.value.trim();
  if (!recipientUserGuid) {
    throw new Error('Thiếu recipient GUID');
  }

  const data = await apiFetch('/api/v1/chat/direct', {
    method: 'POST',
    body: JSON.stringify({ recipient_user_guid: recipientUserGuid }),
  });
  log('Created chat', data);
  await loadChats();
}

function ensureSocketOpen() {
  if (!state.socket || state.socket.readyState !== WebSocket.OPEN) {
    throw new Error('WebSocket chưa kết nối');
  }
}

async function connectSocket() {
  const token = els.token.value.trim();
  if (!token) {
    throw new Error('Thiếu access token');
  }

  if (!state.me) {
    await loadProfile();
  }

  const baseUrl = normalizeBaseUrl(els.baseUrl.value.trim());
  const url = wsUrlFromBaseUrl(baseUrl, token);

  if (state.socket && state.socket.readyState === WebSocket.OPEN) {
    state.socket.close();
  }

  setBadge('idle', 'Connecting');
  state.socket = new WebSocket(url);
  log('WS connect', url);

  state.socket.addEventListener('open', () => {
    setBadge('open', 'Open');
    log('WS open');
  });

  state.socket.addEventListener('message', (event) => {
    const parsed = safeParse(event.data);
    handleSocketPayload(parsed);
  });

  state.socket.addEventListener('close', (event) => {
    setBadge('closed', `Closed ${event.code}`);
    log('WS close', { code: event.code, reason: event.reason });
  });

  state.socket.addEventListener('error', () => {
    setBadge('error', 'Error');
    log('WS error');
  });
}

function disconnectSocket() {
  if (state.socket) {
    state.socket.close();
  }
}

function sendSocketMessage(payload) {
  ensureSocketOpen();
  state.socket.send(JSON.stringify(payload));
  log('WS out', payload);
}

function sendTyping() {
  if (!state.activeChat || !state.me) {
    throw new Error('Thiếu chat hoặc current user');
  }

  sendSocketMessage({
    type: 'user_typing',
    chat_guid: state.activeChat.chat_guid,
    user_guid: state.me.guid,
  });
}

function sendMessage() {
  if (!state.activeChat || !state.me) {
    throw new Error('Thiếu chat hoặc current user');
  }

  const content = els.messageInput.value.trim();
  if (!content) {
    throw new Error('Message rỗng');
  }

  sendSocketMessage({
    type: 'new_message',
    chat_guid: state.activeChat.chat_guid,
    user_guid: state.me.guid,
    content,
  });
  els.messageInput.value = '';
}

function markLastRead() {
  if (!state.activeChat || !state.messages.length) {
    throw new Error('Không có message để mark read');
  }

  const target = state.messages[state.messages.length - 1];
  sendSocketMessage({
    type: 'message_read',
    chat_guid: state.activeChat.chat_guid,
    message_guid: target.message_guid,
  });
}

async function withAction(action, fn) {
  try {
    await fn();
  } catch (error) {
    log(`${action} failed`, error.message || String(error));
  }
}

function bindEvents() {
  [els.baseUrl, els.email, els.token, els.recipientGuid].forEach((input) => {
    input.addEventListener('change', persistState);
  });

  els.loginBtn.addEventListener('click', () => withAction('Login', login));
  els.loadProfileBtn.addEventListener('click', () =>
    withAction('Load profile', loadProfile),
  );
  els.connectBtn.addEventListener('click', () =>
    withAction('Connect WS', connectSocket),
  );
  els.disconnectBtn.addEventListener('click', disconnectSocket);
  els.loadChatsBtn.addEventListener('click', () =>
    withAction('Load chats', loadChats),
  );
  els.loadMessagesBtn.addEventListener('click', () =>
    withAction('Load messages', loadMessages),
  );
  els.sendBtn.addEventListener('click', () =>
    withAction('Send message', async () => sendMessage()),
  );
  els.typingBtn.addEventListener('click', () =>
    withAction('Send typing', async () => sendTyping()),
  );
  els.markReadBtn.addEventListener('click', () =>
    withAction('Mark read', async () => markLastRead()),
  );
  els.createChatBtn.addEventListener('click', () =>
    withAction('Create chat', createChat),
  );
  els.clearLogBtn.addEventListener('click', () => {
    els.logOutput.textContent = '';
  });
  els.copyUserGuidBtn.addEventListener('click', async () => {
    if (!state.me?.guid) {
      log('Copy GUID failed', 'Chưa có current user');
      return;
    }
    await navigator.clipboard.writeText(state.me.guid);
    log('Copied current user guid', state.me.guid);
  });
}

function init() {
  restoreState();
  renderCurrentUser();
  renderChats();
  renderMessages();
  setBadge('idle', 'Idle');
  bindEvents();
  log('Ready', 'Mở /chat-test, login, load chats rồi connect websocket.');
}

init();

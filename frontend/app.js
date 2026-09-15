/**
 * Lab 2 frontend: login / register + file list only.
 * File bodies are intentionally not loaded.
 */

const API_BASE = 'http://127.0.0.1:8000';

let authToken = null;
let files = [];
let currentFileName = null;
let statusTimer = null;

function errorDetail(data, fallback) {
    if (!data) {
        return fallback;
    }
    if (typeof data.detail === 'string') {
        return data.detail;
    }
    return fallback;
}

async function apiRequest(path, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    if (authToken) {
        headers.Authorization = `Bearer ${authToken}`;
    }

    let response;
    try {
        response = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers
        });
    } catch (error) {
        throw new Error(`Cannot reach ${API_BASE}. Is the backend running?`);
    }

    const text = await response.text();
    let data = null;
    if (text) {
        try {
            data = JSON.parse(text);
        } catch (error) {
            data = null;
        }
    }

    if (response.status === 401 && path !== '/login' && path !== '/register') {
        returnToLogin(errorDetail(data, 'Session expired. Please sign in again.'));
        throw new Error(errorDetail(data, 'Unauthorized'));
    }

    if (!response.ok) {
        throw new Error(errorDetail(data, `HTTP ${response.status}`));
    }
    return data;
}

function loginOnApi(username, password) {
    return apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
}

function registerOnApi(username, password) {
    return apiRequest('/register', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
}

function listFilesFromApi() {
    return apiRequest('/files');
}

function showLoginError(message) {
    const el = document.getElementById('login-error');
    if (!message) {
        el.hidden = true;
        el.textContent = '';
        return;
    }
    el.hidden = false;
    el.textContent = message;
}

function returnToLogin(message) {
    authToken = null;
    document.getElementById('app-shell').hidden = true;
    document.getElementById('login-screen').hidden = false;
    showLoginError(message || '');
    document.getElementById('login-password').value = '';
    document.getElementById('login-username').focus();
}

function showStatus(message, isError) {
    const el = document.getElementById('status-message');
    el.textContent = message;
    el.classList.toggle('error', Boolean(isError));
    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => {
        el.textContent = '';
        el.classList.remove('error');
    }, 4000);
}

function renderFileList() {
    const listEl = document.getElementById('file-list');
    listEl.innerHTML = '';
    files.forEach((file) => {
        const item = document.createElement('li');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'file-item';
        button.dataset.fileName = file.name;
        button.textContent = file.name;
        if (file.name === currentFileName) {
            button.classList.add('active');
        }
        button.addEventListener('click', () => selectFile(file.name));
        item.appendChild(button);
        listEl.appendChild(item);
    });
}

function selectFile(fileName) {
    currentFileName = fileName;
    document.getElementById('editor-label').textContent = fileName;
    document.getElementById('editor-placeholder').textContent =
        'File contents are not available in this lab.';
    renderFileList();
    showStatus(`Selected ${fileName}`);
}

async function refreshFileList() {
    files = await listFilesFromApi();
    renderFileList();
    if (files.length === 0) {
        currentFileName = null;
        document.getElementById('editor-label').textContent = 'No file selected';
        return;
    }
    const names = files.map((file) => file.name);
    const keep = names.includes(currentFileName) ? currentFileName : names[0];
    selectFile(keep);
}

async function enterAppAfterLogin() {
    document.getElementById('login-screen').hidden = true;
    document.getElementById('app-shell').hidden = false;
    showLoginError('');
    try {
        await refreshFileList();
        showStatus('Signed in');
    } catch (error) {
        console.error(error);
        files = [];
        renderFileList();
        showStatus(error.message, true);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const button = document.getElementById('login-btn');
    button.disabled = true;
    showLoginError('');
    try {
        const result = await loginOnApi(username, password);
        authToken = result.token;
        await enterAppAfterLogin();
    } catch (error) {
        authToken = null;
        showLoginError(error.message || 'Sign in failed');
    } finally {
        button.disabled = false;
    }
}

async function handleRegister() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const button = document.getElementById('register-btn');
    button.disabled = true;
    showLoginError('');
    try {
        await registerOnApi(username, password);
        const result = await loginOnApi(username, password);
        authToken = result.token;
        await enterAppAfterLogin();
        showStatus('Registered and signed in');
    } catch (error) {
        authToken = null;
        showLoginError(error.message || 'Register failed');
    } finally {
        button.disabled = false;
    }
}

async function handleRefresh() {
    try {
        await refreshFileList();
        showStatus('File list refreshed');
    } catch (error) {
        console.error(error);
        showStatus(error.message, true);
    }
}

function bindUi() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-btn').addEventListener('click', handleRegister);
    document.getElementById('refresh-btn').addEventListener('click', handleRefresh);
}

function init() {
    bindUi();
    document.getElementById('login-screen').hidden = false;
    document.getElementById('app-shell').hidden = true;
    document.getElementById('login-username').focus();
}

init();

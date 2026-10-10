import assert from 'node:assert/strict';
import { build } from 'esbuild';

// Run the real client/interceptors with in-memory storage and an Axios adapter.
// No network, credentials or participant records are used.
const storage = () => {
  const values = new Map();
  return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, String(value)), removeItem: key => values.delete(key) };
};
globalThis.localStorage = storage();
globalThis.sessionStorage = storage();
globalThis.window = { location: { href: '' } };
const bundled = await build({
  stdin: { contents: "export { default as api } from './src/lib/api'; export { useAuthStore as store } from './src/stores/authStore'; export { default as axios } from 'axios';", resolveDir: process.cwd() },
  bundle: true, write: false, platform: 'browser', format: 'esm',
  define: { 'import.meta.env.VITE_API_URL': '"http://synthetic.invalid"', 'process.env.NODE_ENV': '"test"' },
});
const { api, store, axios } = await import(`data:text/javascript;base64,${Buffer.from(bundled.outputFiles[0].text).toString('base64')}`);
const login = () => store.getState().login({ id: 1, role: 'staff' }, 'old', 'refresh');
const unauthorized = config => Promise.reject({ config, response: { status: 401 } });
let refreshes = 0;
let release;
axios.post = async () => {
  refreshes++;
  await new Promise(resolve => { release = resolve; });
  return { data: { access_token: 'new', refresh_token: 'rotated' } };
};
api.defaults.adapter = config => config.headers.Authorization === 'Bearer new'
  ? Promise.resolve({ status: 200, data: { ok: true }, config }) : unauthorized(config);
login();
const requests = [api.get('/one'), api.get('/two'), api.get('/three')];
await new Promise(resolve => setImmediate(resolve));
assert.equal(refreshes, 1);
release();
assert.ok((await Promise.all(requests)).every(result => result.status === 200));
assert.equal(store.getState().accessToken, 'new');
assert.equal(localStorage.getItem('refreshToken'), 'rotated');

// Invalid refresh clears both persisted tokens and the in-memory login state.
login();
axios.post = async () => { throw new Error('Expired refresh'); };
await assert.rejects(api.get('/expired'));
assert.equal(store.getState().isAuthenticated, false);
assert.equal(localStorage.getItem('accessToken'), null);
assert.equal(window.location.href, '/admin/login');

// A rejected login must not trigger refresh or redirect loops.
window.location.href = '';
await assert.rejects(api.post('/auth/login', {}));
assert.equal(window.location.href, '');

// A delayed refresh must not overwrite or sign out a newer login.
login();
axios.post = async () => {
  await new Promise(resolve => { release = resolve; });
  return { data: { access_token: 'stale', refresh_token: 'stale-refresh' } };
};
const pending = api.get('/switch-user');
await new Promise(resolve => setImmediate(resolve));
store.getState().login({ id: 2, role: 'admin' }, 'second-user', 'second-refresh');
release();
await assert.rejects(pending);
assert.equal(store.getState().user.id, 2);
assert.equal(store.getState().accessToken, 'second-user');
assert.equal(window.location.href, '');
console.log('Auth refresh checks passed: concurrency, state synchronization, expired refresh, login failure.');

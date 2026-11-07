// Health status on the home page (spec 0001, AC-4..AC-8). fetch is stubbed; no server runs.
import { test, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';

import { showHealth } from '../public/js/health-status.js';

const html = await readFile(new URL('../public/index.html', import.meta.url), 'utf8');
let dom;

function openPage() {
  dom = new JSDOM(html);
  return dom.window.document;
}

afterEach(() => {
  dom?.window.close(); // an open window keeps timers alive and hangs node --test
  dom = undefined;
});

const jsonResponse = (status, body) => ({ status, json: async () => body });
const statusText = (document) => document.getElementById('health-status').textContent;

test('shows loading text while the health request is pending', async () => {
  const document = openPage();
  let answer;
  const pending = new Promise((resolve) => { answer = resolve; });

  const shown = showHealth(document.getElementById('health-status'), () => pending);

  assert.equal(statusText(document), 'Durum kontrol ediliyor…');
  answer(jsonResponse(200, { status: 'ok', database: 'ok' }));
  await shown;
});

test('shows system running on an ok response', async () => {
  const document = openPage();
  await showHealth(document.getElementById('health-status'),
    async () => jsonResponse(200, { status: 'ok', database: 'ok' }));

  assert.equal(statusText(document), 'Sistem çalışıyor');
});

test('shows database unreachable on an unavailable response', async () => {
  const document = openPage();
  await showHealth(document.getElementById('health-status'),
    async () => jsonResponse(503, { status: 'unavailable', database: 'unavailable' }));

  assert.equal(statusText(document), 'Veritabanına erişilemiyor');
});

test('shows server unreachable on network error', async () => {
  const document = openPage();
  await showHealth(document.getElementById('health-status'),
    async () => { throw new TypeError('Failed to fetch'); });

  assert.equal(statusText(document), 'Sunucuya ulaşılamıyor');
});

test('shows server unreachable on 5xx', async () => {
  const document = openPage();
  await showHealth(document.getElementById('health-status'),
    async () => jsonResponse(500, { detail: 'Internal Server Error' }));

  assert.equal(statusText(document), 'Sunucuya ulaşılamıyor');
});

test('shows server unreachable on non-JSON body', async () => {
  const document = openPage();
  await showHealth(document.getElementById('health-status'),
    async () => ({ status: 200, json: async () => { throw new SyntaxError('Unexpected token <'); } }));

  assert.equal(statusText(document), 'Sunucuya ulaşılamıyor');
});

test('page language is Turkish and status lives in a live region', () => {
  const document = openPage();
  const region = document.getElementById('health-status');

  assert.equal(document.documentElement.lang, 'tr');
  assert.equal(region.getAttribute('role'), 'status');
  assert.equal(region.getAttribute('aria-live'), 'polite');
});

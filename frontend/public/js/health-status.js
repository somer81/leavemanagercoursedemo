// Health status of the system, as the home page shows it (spec 0001).

export const MESSAGES = {
  loading: 'Durum kontrol ediliyor…',
  ok: 'Sistem çalışıyor',
  unavailable: 'Veritabanına erişilemiyor',
  unreachable: 'Sunucuya ulaşılamıyor',
};

// Resolves to 'ok' | 'unavailable' | 'unreachable'; never throws.
export async function loadHealth(fetchFn) {
  let response;
  let body;
  try {
    response = await fetchFn('/api/health', { headers: { Accept: 'application/json' } });
    body = await response.json();
  } catch {
    return 'unreachable';
  }
  if (response.status === 200 && body?.status === 'ok') return 'ok';
  if (response.status === 503 && body?.status === 'unavailable') return 'unavailable';
  return 'unreachable';
}

// textContent only — never innerHTML (docs/security.md).
export function renderHealth(element, state) {
  element.textContent = MESSAGES[state];
  element.dataset.state = state;
}

export async function showHealth(element, fetchFn) {
  renderHealth(element, 'loading');
  renderHealth(element, await loadHealth(fetchFn));
}

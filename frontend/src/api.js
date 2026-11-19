let token = '';
export const setToken = (value) => {
  token = value;
};
export async function api(path, options = {}) {
  const response = await fetch('/api' + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    cache: 'no-store',
  });
  if (!response.ok) {
    const error = new Error(
      response.status === 403
        ? 'access_denied'
        : response.status === 409
          ? 'state_conflict'
          : 'request_failed',
    );
    error.status = response.status;
    throw error;
  }
  return response.json();
}
export const post = (path, body) =>
  api(path, { method: 'POST', body: JSON.stringify(body) });
export async function providerRead(id, provider, scopes) {
  const session = await post('/demo/session', {
    persona: 'provider',
    provider_id: provider,
  });
  return api(
    `/providers/referrals/${id}/summary?scopes=${encodeURIComponent(scopes.join(','))}`,
    { headers: { Authorization: `Bearer ${session.token}` } },
  );
}
let clinicianToken = '';
export async function operations(path, options = {}) {
  if (!clinicianToken)
    clinicianToken = (await post('/demo/session', { persona: 'clinician' })).token;
  return api(path, {
    ...options,
    headers: { Authorization: `Bearer ${clinicianToken}`, ...options.headers },
  });
}

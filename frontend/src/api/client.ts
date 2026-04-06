import { ProcessResponse } from '../types';

const TIMEOUT_MS = 90_000;
const API_BASE = import.meta.env.VITE_API_URL ?? '';

export async function processVideo(url: string): Promise<ProcessResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}/api/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
      throw new Error(error.detail ?? `HTTP ${response.status}`);
    }

    return response.json() as Promise<ProcessResponse>;
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timed out after 90 seconds. Please try again.');
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

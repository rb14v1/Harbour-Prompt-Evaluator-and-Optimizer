const rawApiUrl = (import.meta.env.VITE_API_URL || '').trim().replace(/\/+$/, '');

export const API_BASE = rawApiUrl && !/^https?:\/\//.test(rawApiUrl) ? `https://${rawApiUrl}` : rawApiUrl;

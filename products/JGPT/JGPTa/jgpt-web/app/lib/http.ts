export async function postJsonWithTimeout(url: string, body: any, timeoutMs = 120000) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    return r;
  } finally {
    clearTimeout(t);
  }
}

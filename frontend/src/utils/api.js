const BASE = import.meta.env.VITE_API_URL || "";

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

export async function detectPiece(imageFile, operatorId) {
  const fd = new FormData();
  fd.append("image", imageFile);
  fd.append("operator_id", operatorId);
  const res = await fetch(`${BASE}/api/detect/`, { method: "POST", body: fd });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

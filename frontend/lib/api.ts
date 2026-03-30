function normalizeApiBase(rawBase: string): string {
  const trimmed = rawBase.replace(/\/+$/, "");
  if (trimmed.endsWith("/api")) {
    return trimmed.slice(0, -4);
  }
  return trimmed;
}

const API_BASE = normalizeApiBase(process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/backend");
const AUTH_TOKEN_KEY = "docquest_access_token";

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  username: string;
};

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getAuthToken();
  return {
    ...(extra ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function readError(response: Response): Promise<string> {
  const text = await response.text();
  return text || `Request failed with status ${response.status}`;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json();
}

export async function signup(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json();
}

export type UploadResponse = {
  document_id: string;
  filename: string;
  size_bytes: number;
  indexed_at: string;
};

export type QueryResponse = {
  answer: string;
  document_id: string;
  conversation_id: string;
};

export type ConversationSummary = {
  id: string;
  document_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview?: string | null;
};

export type ConversationDetail = {
  id: string;
  document_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }>;
};

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/v1/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json();
}

export async function askQuestion(
  documentId: string,
  question: string,
  conversationId?: string | null
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/v1/chat/query`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ document_id: documentId, question, conversation_id: conversationId ?? null })
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json();
}

export async function listConversations(documentId?: string | null): Promise<ConversationSummary[]> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const response = await fetch(`${API_BASE}/api/v1/conversations${query}`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE}/api/v1/conversations/${conversationId}`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json();
}

export async function createConversation(documentId: string, title?: string): Promise<ConversationSummary> {
  const response = await fetch(`${API_BASE}/api/v1/conversations`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ document_id: documentId, title: title ?? null })
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json();
}

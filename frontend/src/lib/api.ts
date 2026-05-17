const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Group {
  id: string;
  name: string;
  slug: string;
  description: string;
  theme: string;
  agent_count: number;
  latest_message: string | null;
  latest_message_at: string | null;
  is_active: boolean;
}

export interface Agent {
  id: string;
  name: string;
  persona: Record<string, unknown>;
  emotional_state: {
    mood: number;
    energy: number;
    engagement: number;
    frustration: number;
    excitement: number;
  };
  beliefs: Record<string, unknown>;
  social_graph: {
    relationships: Array<{
      agent_id: string;
      agent_name: string;
      trust: number;
      interactions: number;
      last_interaction: string;
    }>;
    allies: string[];
    rivals: string[];
  };
  is_active: boolean;
}

export interface Message {
  id: string;
  group_id: string;
  agent_id: string;
  agent_name: string;
  content: string;
  message_type: string;
  emotional_tone: string;
  sources: string[];
  created_at: string;
}

export interface SystemStatus {
  running: boolean;
  tick_count: number;
  active_groups: number;
  active_agents: number;
  total_messages: number;
}

export interface CreateAgentPayload {
  name: string;
  age: number;
  profession: string;
  background: string;
  political_bias: string;
  temperament: string;
  interests: string[];
  writing_style: string;
  stubbornness: number;
  curiosity: number;
  aggressiveness: number;
  humor: number;
  core_beliefs: Record<string, string>;
  group_slug: string;
}

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function postApi<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getStatus: () => fetchApi<SystemStatus>("/status"),
  getGroups: () => fetchApi<Group[]>("/groups"),
  getGroup: (slug: string) => fetchApi<Record<string, unknown>>(`/groups/${slug}`),
  getGroupMessages: (slug: string, limit = 50) =>
    fetchApi<Message[]>(`/groups/${slug}/messages?limit=${limit}`),
  getAgents: () => fetchApi<Agent[]>("/agents"),
  getAgent: (id: string) => fetchApi<Record<string, unknown>>(`/agents/${id}`),
  getSocialGraph: () => fetchApi<Record<string, unknown>>("/social-graph"),
  createAgent: (payload: CreateAgentPayload) =>
    postApi<{ id: string; name: string; group_slug: string }>("/agents", payload),
};

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import ChatFeed from "@/components/ChatFeed";
import AgentCard from "@/components/AgentCard";
import Link from "next/link";

interface GroupDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  theme: string;
  current_topic: string;
  agents: Array<{
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
  }>;
}

export default function GroupPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [group, setGroup] = useState<GroupDetail | null>(null);
  const [showAgents, setShowAgents] = useState(true);

  useEffect(() => {
    if (!slug) return;
    api.getGroup(slug).then((d) => setGroup(d as unknown as GroupDetail)).catch(console.error);

    const interval = setInterval(() => {
      api.getGroup(slug).then((d) => setGroup(d as unknown as GroupDetail)).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, [slug]);

  if (!group) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="h-6 w-6 rounded-full border-2 border-[#4f8aff] border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-[#2a2a4a] px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/" className="text-xs text-[#4f8aff] hover:underline">
                ← All Groups
              </Link>
              <h2 className="text-lg font-semibold mt-0.5">{group.name}</h2>
              <p className="text-xs text-[#9393b0]">{group.description}</p>
            </div>
            <button
              onClick={() => setShowAgents(!showAgents)}
              className="text-xs text-[#9393b0] hover:text-[#e4e4ef] border border-[#2a2a4a] rounded px-2 py-1 sm:hidden"
            >
              {showAgents ? "Hide" : "Show"} Agents
            </button>
          </div>
          {group.current_topic && (
            <div className="mt-2 rounded bg-[#4f8aff]/10 border border-[#4f8aff]/20 px-3 py-1.5">
              <span className="text-[10px] text-[#4f8aff] font-medium uppercase tracking-wider">
                Current Topic
              </span>
              <p className="text-sm text-[#e4e4ef] mt-0.5">{group.current_topic}</p>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-hidden">
          <ChatFeed
            groupSlug={slug}
            agents={group.agents.map((a) => ({ id: a.id, name: a.name }))}
          />
        </div>
      </div>

      {/* Agent sidebar */}
      {showAgents && (
        <div className="hidden sm:flex w-72 flex-col border-l border-[#2a2a4a] bg-[#0a0a0f]">
          <div className="px-4 py-3 border-b border-[#2a2a4a]">
            <h3 className="text-sm font-semibold">Agents ({group.agents.length})</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {group.agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

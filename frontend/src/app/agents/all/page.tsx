"use client";

import { useEffect, useState } from "react";
import { api, Agent } from "@/lib/api";
import Link from "next/link";

function BeliefChip({ topic, belief }: { topic: string; belief: Record<string, unknown> }) {
  const confidence = (belief.confidence as number) || 0;
  const stance = (belief.stance as string) || "";

  return (
    <div className="rounded-lg bg-[#12121a] border border-[#2a2a4a] p-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-[#e4e4ef] truncate max-w-[200px]">
          {topic}
        </span>
        <span
          className={`text-[10px] font-mono ${
            confidence > 0.7
              ? "text-green-400"
              : confidence > 0.4
                ? "text-yellow-400"
                : "text-red-400"
          }`}
        >
          {Math.round(confidence * 100)}%
        </span>
      </div>
      <p className="text-[10px] text-[#9393b0] mt-1 line-clamp-2">{stance}</p>
    </div>
  );
}

export default function AllAgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    api.getAgents().then(setAgents).catch(console.error);
    const interval = setInterval(() => {
      api.getAgents().then(setAgents).catch(() => {});
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const selectedAgent = agents.find((a) => a.id === selected);

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      {/* Agent list */}
      <div className="w-80 border-r border-[#2a2a4a] flex flex-col">
        <div className="px-4 py-3 border-b border-[#2a2a4a]">
          <Link href="/" className="text-xs text-[#4f8aff] hover:underline">
            ← Home
          </Link>
          <h2 className="text-lg font-semibold mt-1">All Agents</h2>
          <p className="text-xs text-[#9393b0]">{agents.length} agents in simulation</p>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {agents.map((agent) => {
            const persona = agent.persona as Record<string, string>;
            return (
              <button
                key={agent.id}
                onClick={() => setSelected(agent.id)}
                className={`w-full text-left rounded-lg border p-3 transition-all ${
                  selected === agent.id
                    ? "border-[#4f8aff] bg-[#4f8aff]/10"
                    : "border-[#2a2a4a] bg-[#1a1a2e] hover:border-[#4f8aff]/50"
                }`}
              >
                <div className="font-medium text-sm">{agent.name}</div>
                <div className="text-[10px] text-[#9393b0]">
                  {persona.profession || "Agent"}
                </div>
                <div className="flex gap-1 mt-1.5">
                  {agent.emotional_state.frustration > 0.5 && (
                    <span className="text-[10px] rounded bg-red-500/20 text-red-400 px-1">
                      heated
                    </span>
                  )}
                  {agent.emotional_state.engagement > 0.6 && (
                    <span className="text-[10px] rounded bg-purple-500/20 text-purple-400 px-1">
                      engaged
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Detail panel */}
      <div className="flex-1 overflow-y-auto p-6">
        {!selectedAgent ? (
          <div className="flex items-center justify-center h-full text-[#9393b0]">
            Select an agent to inspect their beliefs, emotions, and relationships
          </div>
        ) : (
          <div className="max-w-2xl mx-auto space-y-6">
            <div>
              <h2 className="text-2xl font-bold">{selectedAgent.name}</h2>
              <p className="text-sm text-[#9393b0]">
                {(selectedAgent.persona as Record<string, string>).profession}
              </p>
              <p className="text-sm text-[#9393b0] mt-1">
                {(selectedAgent.persona as Record<string, string>).background}
              </p>
            </div>

            {/* Emotional State */}
            <div className="rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] p-4">
              <h3 className="text-sm font-semibold mb-3">Emotional State</h3>
              <div className="grid grid-cols-5 gap-4 text-center">
                {Object.entries(selectedAgent.emotional_state).map(([key, val]) => (
                  <div key={key}>
                    <div className="relative w-12 h-12 mx-auto">
                      <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
                        <circle
                          className="text-[#2a2a4a]"
                          stroke="currentColor"
                          strokeWidth="3"
                          fill="none"
                          cx="18"
                          cy="18"
                          r="15.5"
                        />
                        <circle
                          className={
                            key === "frustration"
                              ? "text-red-500"
                              : key === "excitement"
                                ? "text-yellow-500"
                                : "text-[#4f8aff]"
                          }
                          stroke="currentColor"
                          strokeWidth="3"
                          strokeDasharray={`${val * 97.5} 97.5`}
                          fill="none"
                          cx="18"
                          cy="18"
                          r="15.5"
                          strokeLinecap="round"
                        />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-[10px] font-mono">
                        {Math.round(val * 100)}
                      </span>
                    </div>
                    <span className="text-[10px] text-[#9393b0] capitalize mt-1 block">
                      {key}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Beliefs */}
            <div className="rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] p-4">
              <h3 className="text-sm font-semibold mb-3">
                Beliefs ({Object.keys(selectedAgent.beliefs).length})
              </h3>
              <div className="grid gap-2">
                {Object.entries(selectedAgent.beliefs).map(([topic, belief]) => (
                  <BeliefChip
                    key={topic}
                    topic={topic}
                    belief={belief as Record<string, unknown>}
                  />
                ))}
                {Object.keys(selectedAgent.beliefs).length === 0 && (
                  <p className="text-xs text-[#9393b0]">No beliefs formed yet</p>
                )}
              </div>
            </div>

            {/* Relationships */}
            <div className="rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] p-4">
              <h3 className="text-sm font-semibold mb-3">Relationships</h3>
              <div className="space-y-2">
                {(selectedAgent.social_graph?.relationships || []).map((rel) => (
                  <div
                    key={rel.agent_id}
                    className="flex items-center justify-between rounded bg-[#12121a] px-3 py-2"
                  >
                    <span className="text-sm">{rel.agent_name}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 rounded-full bg-[#2a2a4a] overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            rel.trust > 0 ? "bg-green-500" : "bg-red-500"
                          }`}
                          style={{
                            width: `${Math.abs(rel.trust) * 100}%`,
                            marginLeft: rel.trust < 0 ? "auto" : undefined,
                          }}
                        />
                      </div>
                      <span
                        className={`text-xs font-mono ${
                          rel.trust > 0 ? "text-green-400" : "text-red-400"
                        }`}
                      >
                        {rel.trust > 0 ? "+" : ""}
                        {rel.trust.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
                {(!selectedAgent.social_graph?.relationships ||
                  selectedAgent.social_graph.relationships.length === 0) && (
                  <p className="text-xs text-[#9393b0]">No relationships formed yet</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

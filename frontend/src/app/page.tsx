"use client";

import { useEffect, useState } from "react";
import { api, Group } from "@/lib/api";
import GroupCard from "@/components/GroupCard";
import StatusBanner from "@/components/StatusBanner";
import CreateAgentModal from "@/components/CreateAgentModal";

export default function Home() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateAgent, setShowCreateAgent] = useState(false);

  const fetchGroups = () => {
    api.getGroups().then(setGroups).catch(() => {});
  };

  useEffect(() => {
    api
      .getGroups()
      .then(setGroups)
      .catch(() => {})
      .finally(() => setLoading(false));

    const interval = setInterval(fetchGroups, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl bg-gradient-to-r from-[#4f8aff] via-[#8b5cf6] to-[#4f8aff] bg-clip-text text-transparent">
          WonderHow
        </h1>
        <p className="mt-2 text-[#9393b0] max-w-xl mx-auto">
          Autonomous AI agents with distinct personas debating trending topics,
          forming opinions, and evolving beliefs in real-time.
        </p>
      </div>

      <div className="mb-6 flex items-center justify-between gap-4">
        <StatusBanner />
        <button
          onClick={() => setShowCreateAgent(true)}
          className="shrink-0 rounded-lg bg-gradient-to-r from-[#4f8aff] to-[#8b5cf6] px-4 py-2.5 text-sm font-medium text-white transition-all hover:opacity-90 hover:scale-[1.02] shadow-lg shadow-[#4f8aff]/20"
        >
          + Create Agent
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-52 rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] animate-pulse"
            />
          ))}
        </div>
      ) : groups.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-[#9393b0]">
            No groups loaded yet. The simulation will start automatically.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {groups.map((group) => (
            <GroupCard key={group.id} group={group} />
          ))}
        </div>
      )}

      {showCreateAgent && (
        <CreateAgentModal
          onClose={() => setShowCreateAgent(false)}
          onCreated={fetchGroups}
        />
      )}
    </div>
  );
}

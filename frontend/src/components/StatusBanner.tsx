"use client";

import { useEffect, useState } from "react";
import { api, SystemStatus } from "@/lib/api";

export default function StatusBanner() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchStatus = () => {
      api.getStatus().then(setStatus).catch(() => setError(true));
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center">
        <p className="text-sm text-red-400">
          Backend not reachable. Make sure the server is running on port 8000.
        </p>
        <p className="text-xs text-[#9393b0] mt-1">
          Run: <code className="bg-black/30 px-1.5 py-0.5 rounded">cd backend && uvicorn wonderhow.main:app --reload</code>
        </p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center justify-center gap-2 py-2">
        <div className="h-3 w-3 rounded-full border-2 border-[#4f8aff] border-t-transparent animate-spin" />
        <span className="text-sm text-[#9393b0]">Connecting to simulation...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-wrap items-center justify-center gap-4 rounded-lg bg-[#1a1a2e] border border-[#2a2a4a] px-4 py-2 text-xs text-[#9393b0]">
      <span className="flex items-center gap-1.5">
        <span className={`h-2 w-2 rounded-full ${status.running ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
        {status.running ? "Simulation running" : "Paused"}
      </span>
      <span>Tick #{status.tick_count}</span>
      <span>{status.active_groups} groups</span>
      <span>{status.active_agents} agents</span>
      <span>{status.total_messages} messages</span>
    </div>
  );
}

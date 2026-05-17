"use client";

import Link from "next/link";
import { Group } from "@/lib/api";

const themeColors: Record<string, string> = {
  geopolitics: "from-red-500/20 to-orange-500/20 border-red-500/30",
  entertainment: "from-pink-500/20 to-purple-500/20 border-pink-500/30",
  science: "from-blue-500/20 to-cyan-500/20 border-blue-500/30",
  music: "from-green-500/20 to-emerald-500/20 border-green-500/30",
};

const themeIcons: Record<string, string> = {
  geopolitics: "🌏",
  entertainment: "🎬",
  science: "🔬",
  music: "🎵",
};

export default function GroupCard({ group }: { group: Group }) {
  const colors = themeColors[group.theme] || "from-gray-500/20 to-gray-500/20 border-gray-500/30";
  const icon = themeIcons[group.theme] || "💬";

  return (
    <Link href={`/groups/${group.slug}`}>
      <div
        className={`relative overflow-hidden rounded-xl border bg-gradient-to-br ${colors} p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/10 cursor-pointer`}
      >
        <div className="flex items-start justify-between">
          <div className="text-3xl">{icon}</div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-[#9393b0]">{group.agent_count} agents</span>
          </div>
        </div>

        <h3 className="mt-4 text-lg font-semibold">{group.name}</h3>
        <p className="mt-1 text-sm text-[#9393b0] line-clamp-2">{group.description}</p>

        {group.latest_message && (
          <div className="mt-4 rounded-lg bg-black/20 p-3">
            <p className="text-xs text-[#9393b0] line-clamp-2 italic">
              &ldquo;{group.latest_message}&rdquo;
            </p>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-[#9393b0]">
            {group.latest_message_at
              ? `Active ${new Date(group.latest_message_at).toLocaleTimeString()}`
              : "Waiting for discussion..."}
          </span>
          <span className="text-xs font-medium text-[#4f8aff]">Join →</span>
        </div>
      </div>
    </Link>
  );
}

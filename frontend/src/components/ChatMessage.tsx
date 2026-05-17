"use client";

import { Message } from "@/lib/api";

const toneColors: Record<string, string> = {
  confrontational: "border-l-red-500",
  supportive: "border-l-green-500",
  humorous: "border-l-yellow-500",
  excited: "border-l-orange-500",
  frustrated: "border-l-red-400",
  neutral: "border-l-[#2a2a4a]",
  happy: "border-l-emerald-500",
  engaged: "border-l-blue-500",
  energetic: "border-l-purple-500",
};

const agentColors: string[] = [
  "text-blue-400",
  "text-purple-400",
  "text-green-400",
  "text-orange-400",
  "text-pink-400",
  "text-cyan-400",
  "text-yellow-400",
  "text-red-400",
];

function getAgentColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return agentColors[Math.abs(hash) % agentColors.length];
}

export default function ChatMessage({ message }: { message: Message }) {
  const isSystem = message.message_type === "system";
  const isUser = message.message_type === "user";
  const borderColor = toneColors[message.emotional_tone] || toneColors.neutral;
  const nameColor = getAgentColor(message.agent_name);

  if (isSystem) {
    return (
      <div className="flex justify-center py-2">
        <span className="rounded-full bg-[#1a1a2e] px-4 py-1.5 text-xs text-[#9393b0]">
          {message.content}
        </span>
      </div>
    );
  }

  if (isUser) {
    return (
      <div className="border-l-2 border-l-[#4f8aff] pl-4 py-2 bg-[#4f8aff]/[0.04]">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-[#4f8aff]">{message.agent_name}</span>
          <span className="rounded bg-[#4f8aff]/20 px-1.5 py-0.5 text-[10px] text-[#4f8aff] font-medium">
            YOU
          </span>
          <span className="text-[10px] text-[#9393b0]">
            {new Date(message.created_at).toLocaleTimeString()}
          </span>
        </div>
        <p className="mt-1 text-sm text-[#e4e4ef] leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    );
  }

  return (
    <div className={`border-l-2 ${borderColor} pl-4 py-2 hover:bg-white/[0.02] transition-colors`}>
      <div className="flex items-center gap-2">
        <span className={`text-sm font-semibold ${nameColor}`}>{message.agent_name}</span>
        {message.message_type === "debate" && (
          <span className="rounded bg-red-500/20 px-1.5 py-0.5 text-[10px] text-red-400 font-medium">
            DEBATE
          </span>
        )}
        <span className="text-[10px] text-[#9393b0]">
          {new Date(message.created_at).toLocaleTimeString()}
        </span>
        {message.emotional_tone !== "neutral" && (
          <span className="text-[10px] text-[#9393b0] italic">{message.emotional_tone}</span>
        )}
      </div>
      <p className="mt-1 text-sm text-[#e4e4ef] leading-relaxed whitespace-pre-wrap">
        {message.content}
      </p>
      {message.sources.length > 0 && (
        <div className="mt-1 flex flex-wrap gap-1">
          {message.sources.map((source, i) => (
            <span
              key={i}
              className="text-[10px] text-[#4f8aff] bg-[#4f8aff]/10 rounded px-1.5 py-0.5"
            >
              {source}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

interface AgentInfo {
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
}

function EmotionBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-16 text-[#9393b0]">{label}</span>
      <div className="flex-1 h-1.5 rounded-full bg-[#1a1a2e] overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-500`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="w-8 text-right text-[#9393b0]">{Math.round(value * 100)}%</span>
    </div>
  );
}

export default function AgentCard({ agent, compact = false }: { agent: AgentInfo; compact?: boolean }) {
  const es = agent.emotional_state;
  const persona = agent.persona as Record<string, string>;

  if (compact) {
    return (
      <div className="flex items-center gap-3 rounded-lg bg-[#1a1a2e] px-3 py-2 border border-[#2a2a4a]">
        <div className="flex flex-col">
          <span className="text-sm font-medium">{agent.name}</span>
          <span className="text-[10px] text-[#9393b0]">
            {persona.profession || "Agent"} · {persona.temperament || ""}
          </span>
        </div>
        <div className="ml-auto flex gap-1">
          {es.frustration > 0.5 && (
            <span className="text-[10px] rounded bg-red-500/20 text-red-400 px-1.5">heated</span>
          )}
          {es.excitement > 0.6 && (
            <span className="text-[10px] rounded bg-yellow-500/20 text-yellow-400 px-1.5">excited</span>
          )}
          {es.energy < 0.3 && (
            <span className="text-[10px] rounded bg-gray-500/20 text-gray-400 px-1.5">tired</span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] p-4 space-y-3">
      <div>
        <h4 className="font-semibold">{agent.name}</h4>
        <p className="text-xs text-[#9393b0]">
          {persona.age && `${persona.age}yo`} {persona.profession}
        </p>
        <p className="text-xs text-[#9393b0] mt-0.5">{persona.temperament}</p>
      </div>

      <div className="space-y-1.5">
        <EmotionBar label="Mood" value={es.mood} color="bg-emerald-500" />
        <EmotionBar label="Energy" value={es.energy} color="bg-blue-500" />
        <EmotionBar label="Engaged" value={es.engagement} color="bg-purple-500" />
        <EmotionBar label="Frustration" value={es.frustration} color="bg-red-500" />
        <EmotionBar label="Excitement" value={es.excitement} color="bg-yellow-500" />
      </div>

      {persona.political_bias && (
        <div className="text-xs">
          <span className="text-[#9393b0]">Bias: </span>
          <span className="text-[#e4e4ef]">{persona.political_bias}</span>
        </div>
      )}
    </div>
  );
}

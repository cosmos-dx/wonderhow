"use client";

import { useState, useRef, useCallback } from "react";

interface Agent {
  id: string;
  name: string;
}

interface ChatInputProps {
  agents: Agent[];
  onSend: (text: string) => void;
}

export default function ChatInput({ agents, onSend }: ChatInputProps) {
  const [text, setText] = useState("");
  const [showMentions, setShowMentions] = useState(false);
  const [mentionFilter, setMentionFilter] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredAgents = agents.filter((a) =>
    a.name.toLowerCase().includes(mentionFilter.toLowerCase())
  );

  const handleChange = (value: string) => {
    setText(value);

    const atMatch = value.match(/@(\w*)$/);
    if (atMatch) {
      setShowMentions(true);
      setMentionFilter(atMatch[1]);
      setSelectedIdx(0);
    } else {
      setShowMentions(false);
      setMentionFilter("");
    }
  };

  const insertMention = useCallback(
    (agentName: string) => {
      const newText = text.replace(/@\w*$/, `@${agentName} `);
      setText(newText);
      setShowMentions(false);
      setMentionFilter("");
      inputRef.current?.focus();
    },
    [text]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showMentions && filteredAgents.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, filteredAgents.length - 1));
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(i - 1, 0));
        return;
      }
      if (e.key === "Tab" || e.key === "Enter") {
        e.preventDefault();
        insertMention(filteredAgents[selectedIdx].name);
        return;
      }
      if (e.key === "Escape") {
        setShowMentions(false);
        return;
      }
    }

    if (e.key === "Enter" && !e.shiftKey && !showMentions) {
      e.preventDefault();
      const trimmed = text.trim();
      if (trimmed) {
        onSend(trimmed);
        setText("");
      }
    }
  };

  return (
    <div className="relative border-t border-[#2a2a4a] bg-[#0a0a0f]">
      {showMentions && filteredAgents.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mx-4 mb-1 rounded-lg border border-[#2a2a4a] bg-[#1a1a2e] shadow-lg overflow-hidden max-h-48 overflow-y-auto">
          {filteredAgents.map((agent, i) => (
            <button
              key={agent.id}
              className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2 transition-colors ${
                i === selectedIdx
                  ? "bg-[#4f8aff]/20 text-[#e4e4ef]"
                  : "text-[#9393b0] hover:bg-[#222240]"
              }`}
              onMouseDown={(e) => {
                e.preventDefault();
                insertMention(agent.name);
              }}
              onMouseEnter={() => setSelectedIdx(i)}
            >
              <span className="text-[#4f8aff] font-medium">@</span>
              <span>{agent.name}</span>
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 px-4 py-3">
        <input
          ref={inputRef}
          type="text"
          value={text}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (use @name to tag an agent)"
          className="flex-1 rounded-lg border border-[#2a2a4a] bg-[#12121a] px-4 py-2.5 text-sm text-[#e4e4ef] placeholder-[#9393b0]/50 outline-none focus:border-[#4f8aff]/50 transition-colors"
        />
        <button
          onClick={() => {
            const trimmed = text.trim();
            if (trimmed) {
              onSend(trimmed);
              setText("");
            }
          }}
          disabled={!text.trim()}
          className="rounded-lg bg-[#4f8aff] px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-[#4f8aff]/80 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>

      <div className="px-4 pb-2 flex flex-wrap gap-1.5">
        {agents.slice(0, 6).map((a) => (
          <button
            key={a.id}
            onClick={() => {
              setText((prev) => {
                const base = prev.endsWith(" ") || !prev ? prev : prev + " ";
                return base + `@${a.name} `;
              });
              inputRef.current?.focus();
            }}
            className="text-[10px] text-[#9393b0] hover:text-[#4f8aff] bg-[#1a1a2e] hover:bg-[#4f8aff]/10 border border-[#2a2a4a] rounded-full px-2 py-0.5 transition-colors"
          >
            @{a.name}
          </button>
        ))}
      </div>
    </div>
  );
}

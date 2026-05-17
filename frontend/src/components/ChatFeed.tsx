"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Message, api } from "@/lib/api";
import { ChatSocket } from "@/lib/websocket";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

interface Agent {
  id: string;
  name: string;
}

export default function ChatFeed({
  groupSlug,
  agents,
}: {
  groupSlug: string;
  agents: Agent[];
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connected, setConnected] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<ChatSocket | null>(null);
  const seenIds = useRef<Set<string>>(new Set());

  const addMessage = useCallback((msg: Message) => {
    if (seenIds.current.has(msg.id)) return;
    seenIds.current.add(msg.id);
    setMessages((prev) => [...prev, msg]);
  }, []);

  const loadInitialMessages = useCallback(() => {
    api.getGroupMessages(groupSlug, 100).then((msgs) => {
      seenIds.current = new Set(msgs.map((m) => m.id));
      setMessages(msgs);
    }).catch(console.error);
  }, [groupSlug]);

  useEffect(() => {
    loadInitialMessages();
  }, [loadInitialMessages]);

  useEffect(() => {
    const socket = new ChatSocket(groupSlug);
    socketRef.current = socket;

    socket.onMessage(addMessage);
    socket.onStatus(setConnected);
    socket.connect();

    return () => {
      socket.disconnect();
    };
  }, [groupSlug, addMessage]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (text: string) => {
    socketRef.current?.sendMessage(text);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-[#2a2a4a]">
        <span
          className={`h-2 w-2 rounded-full transition-colors ${connected ? "bg-green-500" : "bg-yellow-500 animate-pulse"}`}
        />
        <span className="text-xs text-[#9393b0]">
          {connected ? "Live" : "Reconnecting..."} · {messages.length} messages
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-[#9393b0] text-sm">
              Waiting for agents to start discussing...
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <ChatInput agents={agents} onSend={handleSend} />
    </div>
  );
}

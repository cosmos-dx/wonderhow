import { Message } from "./api";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type MessageHandler = (message: Message) => void;
type StatusHandler = (connected: boolean) => void;

export class ChatSocket {
  private ws: WebSocket | null = null;
  private messageHandlers: MessageHandler[] = [];
  private statusHandlers: StatusHandler[] = [];
  private groupSlug: string;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private shouldReconnect = true;

  constructor(groupSlug: string) {
    this.groupSlug = groupSlug;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    if (this.ws?.readyState === WebSocket.CONNECTING) return;

    try {
      this.ws = new WebSocket(`${WS_BASE}/ws/chat/${this.groupSlug}`);

      this.ws.onopen = () => {
        this.statusHandlers.forEach((h) => h(true));
      };

      this.ws.onmessage = (event) => {
        try {
          const message: Message = JSON.parse(event.data);
          this.messageHandlers.forEach((h) => h(message));
        } catch {
          console.warn("Failed to parse WS message:", event.data);
        }
      };

      this.ws.onclose = () => {
        this.statusHandlers.forEach((h) => h(false));
        if (this.shouldReconnect) {
          this.reconnectTimer = setTimeout(() => this.connect(), 3000);
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch {
      this.statusHandlers.forEach((h) => h(false));
      if (this.shouldReconnect) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000);
      }
    }
  }

  sendMessage(text: string, username: string = "You") {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({ type: "user_message", text, username })
      );
    }
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler);
    };
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.push(handler);
    return () => {
      this.statusHandlers = this.statusHandlers.filter((h) => h !== handler);
    };
  }

  disconnect() {
    this.shouldReconnect = false;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }
}

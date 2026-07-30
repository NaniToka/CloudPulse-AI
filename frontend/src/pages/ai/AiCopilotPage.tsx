import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Bot, User2, Paperclip, Cpu, AlertTriangle, DollarSign } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const SUGGESTED = [
  { icon: Cpu,           text: "Analyze my CPU spikes over the last 24h" },
  { icon: DollarSign,    text: "Show me the top 5 cost-saving opportunities" },
  { icon: AlertTriangle, text: "Summarize all P0 and P1 incidents this week" },
  { icon: Sparkles,      text: "What should I optimize first in my infrastructure?" },
];

const DEMO_REPLIES: Record<string, string> = {
  default:
    "I'm analyzing your infrastructure data. Based on current metrics, I can see elevated CPU usage on **api-prod-01** (91%) and a memory pressure situation on **web-prod-02** (88%). I recommend investigating the connection pool exhaustion on api-gateway first as it's causing cascading effects on downstream services.\n\nWould you like me to dig deeper into any specific area?",
};

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <div className={cn(
        "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
        isUser ? "bg-brand-gradient" : "bg-bg-elevated border border-white/10"
      )}>
        {isUser ? <User2 className="h-3.5 w-3.5 text-white" /> : <Bot className="h-3.5 w-3.5 text-brand-purple" />}
      </div>
      <div className={cn(
        "max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed",
        isUser
          ? "bg-brand-gradient text-white rounded-tr-sm"
          : "glass text-foreground rounded-tl-sm"
      )}>
        {msg.content.split("\n").map((line, i) => (
          <p key={i} className={i > 0 ? "mt-2" : ""}>{line}</p>
        ))}
        <p className={cn("text-[10px] mt-2", isUser ? "text-white/60" : "text-muted-foreground")}>
          {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </div>
  );
}

export default function AiCopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0",
      role: "assistant",
      content: "Hello! I'm your CloudPulse AI Copilot. I have access to your infrastructure metrics, logs, incidents, and cost data. What would you like to explore today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text, timestamp: new Date() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1200));
    const aiMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: DEMO_REPLIES.default,
      timestamp: new Date(),
    };
    setMessages((m) => [...m, aiMsg]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px-48px)] space-y-4">
      <PageHeader
        title="AI Copilot"
        subtitle="Conversational intelligence for your infrastructure"
      />

      <div className="flex flex-1 gap-4 min-h-0">
        {/* Chat area */}
        <div className="flex flex-1 flex-col glass rounded-xl overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)}
            {loading && (
              <div className="flex gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-bg-elevated border border-white/10">
                  <Bot className="h-3.5 w-3.5 text-brand-purple" />
                </div>
                <div className="glass rounded-xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1 items-center h-4">
                    {[0, 1, 2].map((i) => (
                      <span
                        key={i}
                        className="h-1.5 w-1.5 rounded-full bg-brand-purple animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-white/[0.06] p-4">
            <div className="flex gap-2">
              <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-bg-elevated text-muted-foreground hover:text-foreground transition-colors">
                <Paperclip className="h-4 w-4" />
              </button>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(input)}
                placeholder="Ask about your infrastructure…"
                className="flex-1 h-10 rounded-lg border border-white/10 bg-bg-elevated px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none focus:border-brand-blue/50"
              />
              <Button onClick={() => send(input)} disabled={!input.trim() || loading} size="icon">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Sidebar: suggestions */}
        <div className="hidden xl:flex flex-col w-64 shrink-0 space-y-3">
          <div className="glass rounded-xl p-4 space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Suggested Prompts</p>
            {SUGGESTED.map((s, i) => (
              <button
                key={i}
                onClick={() => send(s.text)}
                className="w-full flex items-start gap-2.5 rounded-lg p-2.5 text-left text-xs text-muted-foreground hover:bg-white/[0.04] hover:text-foreground transition-colors border border-transparent hover:border-white/[0.06]"
              >
                <s.icon className="h-3.5 w-3.5 mt-0.5 shrink-0 text-brand-purple" />
                {s.text}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

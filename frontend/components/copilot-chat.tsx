"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api";

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface CopilotChatResponse {
  reply: string;
  cited_metrics: Record<string, string | number>;
  suggested_follow_ups: string[];
}

interface CopilotChatProps {
  businessId: string;
  fileId: string;
}

export default function CopilotChat({ businessId, fileId }: CopilotChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I am your **AI Business Copilot**. I have analyzed your verified revenue, product sales, customer retention, and forecast data. What would you like to explore today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [followUps, setFollowUps] = useState<string[]>([
    "What is our total revenue and run-rate?",
    "Which products generate the most sales?",
    "What is our customer retention & churn risk?",
    "What is our projected sales forecast?",
  ]);

  async function handleSendMessage(queryText?: string) {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage: ChatMessage = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await apiJson<CopilotChatResponse>(
        `/api/v1/businesses/${businessId}/uploads/${fileId}/copilot/chat`,
        {
          method: "POST",
          body: JSON.stringify({
            message: textToSend,
            history: messages,
          }),
        }
      );

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: res.reply,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      if (res.suggested_follow_ups && res.suggested_follow_ups.length > 0) {
        setFollowUps(res.suggested_follow_ups);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the intelligence server. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[600px] rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900 overflow-hidden">
      {/* Chat Header */}
      <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-800/30">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-sm">
            AI
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              Interactive Business Copilot
            </h3>
            <span className="flex items-center gap-1.5 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" /> Grounded in Verified Financial Facts
            </span>
          </div>
        </div>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                m.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200"
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-zinc-100 px-4 py-3 text-xs text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-indigo-500 animate-ping" />
              AI Copilot is analyzing business facts...
            </div>
          </div>
        )}
      </div>

      {/* Quick Question Pills */}
      {followUps.length > 0 && (
        <div className="px-6 py-2 border-t border-zinc-100 dark:border-zinc-800/60 bg-zinc-50/30 dark:bg-zinc-900/30 flex items-center gap-2 overflow-x-auto">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider whitespace-nowrap font-medium">
            Suggested:
          </span>
          {followUps.slice(0, 3).map((q, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(q)}
              className="rounded-full border border-zinc-200 bg-white px-3 py-1 text-[11px] text-zinc-600 shadow-sm hover:border-indigo-400 hover:text-indigo-600 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:border-indigo-500 whitespace-nowrap transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input Box */}
      <div className="border-t border-zinc-200 p-4 dark:border-zinc-800 bg-white dark:bg-zinc-900">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask anything about your sales, top products, churn, or forecast..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-xs text-zinc-900 placeholder:text-zinc-400 focus:border-indigo-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors dark:bg-indigo-500"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

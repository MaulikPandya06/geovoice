import { useState } from "react";
import { SendHorizonal, Sparkles, TriangleAlert } from "lucide-react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Props = {
  selectedEvent: any;
};

export default function AIInsightsTab({ selectedEvent }: Props) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  // const suggestedPrompts = [
  //   "Which countries are most involved?",
  //   "Summarize the global response",
  //   "What are the geopolitical risks?",
  //   "Which countries support each side?",
  // ];

  const handleSend = (text?: string) => {
    const msg = text ?? input;
    if (!msg.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "AI-generated geopolitical insights will appear here once backend integration is connected.",
        },
      ]);
    }, 700);

    setInput("");
  };

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 px-1 py-2">

      {/* AI Header */}
      <div className="flex items-center gap-2.5 px-0.5">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 border border-blue-500/20">
          <Sparkles size={14} className="text-blue-400" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <p className="text-xs font-semibold text-white leading-tight">
              AI Geopolitical Assistant
            </p>
            <span className="rounded px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide bg-amber-500/15 text-amber-400 border border-amber-500/25">
              Beta
            </span>
          </div>
          <p className="text-[11px] text-gray-500 leading-tight mt-0.5">
            Ask questions related to{" "}
            <span className="text-blue-400 font-medium">
              {selectedEvent?.title}
            </span>
          </p>
        </div>
      </div>

      {/* Disclaimer banner */}
      <div className="flex items-start gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2">
        <TriangleAlert size={12} className="mt-0.5 shrink-0 text-amber-400/70" />
        <p className="text-[10px] leading-relaxed text-amber-400/70">
          AI responses may be inaccurate or incomplete. Verify critical information from official sources before making decisions.
        </p>
      </div>

      {/* Suggested prompts — single scrollable row */}
      {/* <div className="flex gap-1.5 overflow-x-auto pb-0.5 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {suggestedPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSend(prompt)}
            className="shrink-0 whitespace-nowrap rounded-lg border border-gray-800 bg-[#08111f] px-2.5 py-1 text-[11px] text-gray-400 transition-all hover:border-blue-500/30 hover:text-gray-200"
          >
            {prompt}
          </button>
        ))}
      </div> */}

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-gray-800/60 bg-[#07111f] p-3 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {messages.length === 0 ? (
          <p className="text-center text-[11px] text-gray-600 mt-4">
            Type a question below
          </p>
        ) : (
          <div className="flex flex-col gap-2.5">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[88%] rounded-xl px-3 py-2 text-[11px] leading-relaxed ${
                    message.role === "user"
                      ? "bg-blue-600/15 border border-blue-500/20 text-blue-50"
                      : "bg-[#0d1a2d] border border-gray-800/60 text-gray-300"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex items-end gap-2">
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Ask about alliances, sanctions, responses..."
          className="flex-1 resize-none rounded-xl border border-gray-800 bg-[#08111f] px-3 py-2 text-[11px] leading-5 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500/40"
        />
        <button
          onClick={() => handleSend()}
          className="flex h-[52px] w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-500"
        >
          <SendHorizonal size={14} />
        </button>
      </div>

    </div>
  );
}

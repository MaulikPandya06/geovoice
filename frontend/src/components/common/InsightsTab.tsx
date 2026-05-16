import { useState, useEffect, useRef  } from "react";
import { SendHorizonal, Sparkles, TriangleAlert } from "lucide-react";
import { fetchWithLoading } from "../../services/fetchWithLoading";

type Props = {
  selectedEvent: any;
  selectedCountry: any;
};

export default function AIInsightsTab({
  selectedEvent ,
  selectedCountry
}: Props) {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const suggestionsRef = useRef<HTMLDivElement | null>(null);

  // const [input, setInput] = useState("");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);

  const [loading, setLoading] = useState(false);

  const suggestedPrompts = [
    `What is the stance of ${selectedCountry?.country_name}?`,
    "Summarize the responses",
    "What are the geopolitical risks?",
  ];
  const scrollSuggestions = (direction: "left" | "right") => {
    if (!suggestionsRef.current) return;

    suggestionsRef.current.scrollBy({
      left: direction === "right" ? 220 : -220,
      behavior: "smooth",
    });
  };

  const sendMessage = async () => {
    if (!question.trim() || !selectedCountry || !selectedEvent) return;

    const userMessage = {
      role: "user" as const,
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentQuestion = question;
    setQuestion("");

    try {
      setLoading(true);
      const API_URL = import.meta.env.VITE_API_URL;

      // const response = await fetch(
      const response = await fetchWithLoading(
        `${API_URL}/api/chatbot/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: currentQuestion,
            country: selectedCountry.country_name,
            event: selectedEvent.title,
          }),
        }
      );

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data.answer || "No response received.",
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Failed to get AI response.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // const handleSend = (text?: string) => {
  //   const msg = text ?? input;
  //   if (!msg.trim()) return;

  //   setMessages((prev) => [...prev, { role: "user", content: msg }]);

  //   setTimeout(() => {
  //     setMessages((prev) => [
  //       ...prev,
  //       {
  //         role: "assistant",
  //         content:
  //           "AI-generated geopolitical insights will appear here once backend integration is connected.",
  //       },
  //     ]);
  //   }, 700);

  //   setInput("");
  // };

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
      <div className="relative">

        {/* Left fade */}
        <div className="pointer-events-none absolute left-0 top-0 z-10 h-full w-8 bg-gradient-to-r from-[#020817] to-transparent" />

        {/* Right fade */}
        <div className="pointer-events-none absolute right-0 top-0 z-10 h-full w-10 bg-gradient-to-l from-[#020817] to-transparent" />

        <div className="relative">

          {/* Left Arrow */}
          <button
            onClick={() => scrollSuggestions("left")}
            className="
              absolute left-1 top-1/2 z-20
              flex h-5 w-5 -translate-y-1/2 items-center justify-center
              rounded-full border border-white/10
              bg-[#0b1220]/90
              text-[10px] text-gray-400
              backdrop-blur-sm
              transition hover:border-blue-400/30 hover:text-white
            "
          >
            ‹
          </button>

          {/* Right Arrow */}
          <button
            onClick={() => scrollSuggestions("right")}
            className="
              absolute right-1 top-1/2 z-20
              flex h-5 w-5 -translate-y-1/2 items-center justify-center
              rounded-full border border-white/10
              bg-[#0b1220]/90
              text-[10px] text-gray-400
              backdrop-blur-sm
              transition hover:border-blue-400/30 hover:text-white
            "
          >
            ›
          </button>

          <div
            ref={suggestionsRef}
            className="
              flex gap-2 overflow-x-auto pb-1 px-7
              [scrollbar-width:none]
              [-ms-overflow-style:none]
              [&::-webkit-scrollbar]:hidden
            "
          >

          {suggestedPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => setQuestion(prompt)}
              className="
                group shrink-0 whitespace-nowrap rounded-xl
                border border-blue-500/20
                bg-gradient-to-b from-blue-500/10 to-blue-500/[0.03]
                px-3 py-2
                text-[11px] font-medium
                text-blue-100
                shadow-[0_0_0_1px_rgba(59,130,246,0.05)]
                transition-all duration-200

                hover:border-blue-400/40
                hover:bg-blue-500/15
                hover:text-white
                hover:shadow-[0_0_20px_rgba(59,130,246,0.12)]
                hover:-translate-y-[1px]

                active:scale-[0.98]
              "
            >
              <span className="opacity-70 transition-opacity group-hover:opacity-100">
                ✦
              </span>

              <span className="ml-1.5">
                {prompt}
              </span>
            </button>
          ))}

        </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-gray-800/60 bg-[#07111f] p-3 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {messages.length === 0 ? (
          <p className="text-center text-[11px] text-gray-600 mt-4">
            Type a question below or select from the suggestions above
          </p>
        ) : (
          // <div className="flex flex-col gap-2.5">
          //   {messages.map((message, index) => (
          //     <div
          //       key={index}
          //       className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          //     >
          //       <div
          //         className={`max-w-[88%] rounded-xl px-3 py-2 text-[11px] leading-relaxed ${
          //           message.role === "user"
          //             ? "bg-blue-600/15 border border-blue-500/20 text-blue-50"
          //             : "bg-[#0d1a2d] border border-gray-800/60 text-gray-300"
          //         }`}
          //       >
          //         {message.content}
          //       </div>
          //     </div>
          //   ))}
          // </div>
          <div className="flex flex-col gap-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                  msg.role === "user"
                    ? "ml-auto bg-blue-600 text-white"
                    : "bg-white/5 text-gray-200 border border-white/10"
                }`}
              >
                {msg.content}
              </div>
            ))}

            {loading && (
              <div className="bg-white/5 border border-white/10 text-gray-300 px-4 py-3 rounded-2xl w-fit">
                Thinking...
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex items-end gap-2">
        <textarea
          rows={2}
          // value={input}
          // onChange={(e) => setInput(e.target.value)}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Type here..."
          className="flex-1 resize-none rounded-xl border border-gray-800 bg-[#08111f] px-3 py-2 text-[11px] leading-5 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500/40"
        />
        <button
          onClick={sendMessage}
          className="flex h-[52px] w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-500"
        >
          <SendHorizonal size={14} />
        </button>
      </div>

    </div>
  );
}

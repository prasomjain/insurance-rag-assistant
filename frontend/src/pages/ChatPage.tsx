import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  ShieldCheck,
  FileText,
  AlertCircle,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { chatWithBot } from "../api";
import { ECGBackground } from "../components/ECGBackground";
import clsx from "clsx";

interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  timestamp: Date;
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "bot",
      content:
        "Hello! I'm your **Claims Assistant**. \n\nI can help you with:\n- Analyzing denied claims\n- Checking patient records\n- Provider statistics\n\n*Ask me anything!*",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatWithBot(userMessage.content, "improved");
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: response.answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: "Sorry, I encountered an error processing your request.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center p-4 md:p-8 relative overflow-hidden font-sans selection:bg-cyan-500/30">
      <ECGBackground />

      <header className="w-full max-w-6xl mb-6 flex items-center justify-between glass p-4 rounded-2xl z-10 relative border border-white/10 shadow-2xl bg-slate-900/40 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-linear-to-br from-cyan-500 to-blue-600 rounded-xl shadow-lg shadow-cyan-500/20 ring-1 ring-white/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-linear-to-r from-cyan-400 via-blue-500 to-teal-400 bg-clip-text text-transparent tracking-tight drop-shadow-sm pb-1">
              Claims Query Assistant
            </h1>
            <p className="text-[10px] text-cyan-200/80 font-bold tracking-widest uppercase">
              RAG-Powered Intelligence
            </p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-white/10 text-xs text-slate-300 font-medium">
          <FileText className="w-3.5 h-3.5 text-cyan-400" />
          <span>2,000 Records</span>
        </div>
      </header>

      <main className="w-full max-w-6xl flex-1 flex flex-col glass-card rounded-3xl overflow-hidden h-[75vh] z-10 relative shadow-2xl shadow-black/80 border border-white/10 ring-1 ring-white/5 bg-slate-900/60 backdrop-blur-xl">
        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar scroll-smooth">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className={clsx(
                  "flex gap-5 max-w-[85%]",
                  msg.role === "user" ? "ml-auto flex-row-reverse" : "",
                )}
              >
                <div
                  className={clsx(
                    "w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg ring-2 ring-white/10",
                    msg.role === "user" ?
                      "bg-linear-to-br from-blue-600 to-indigo-600"
                    : "bg-linear-to-br from-cyan-500 to-blue-600",
                  )}
                >
                  {msg.role === "user" ?
                    <User className="w-5 h-5 text-white" />
                  : <Bot className="w-5 h-5 text-white" />}
                </div>

                <div
                  className={clsx(
                    "p-6 rounded-2xl shadow-xl text-sm leading-relaxed relative overflow-hidden group border",
                    msg.role === "user" ?
                      "bg-blue-600 text-white rounded-tr-none border-blue-400/30"
                    : "bg-slate-900/95 text-slate-100 rounded-tl-none border-slate-700/80",
                  )}
                >
                  {msg.role === "bot" ?
                    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-headings:text-cyan-300 prose-a:text-cyan-400 prose-strong:text-white prose-code:bg-slate-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:text-cyan-200 prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-li:marker:text-cyan-500 prose-table:border-slate-700 prose-th:bg-slate-800/50 prose-th:text-cyan-300">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  : <span className="font-medium tracking-wide">
                      {msg.content}
                    </span>
                  }
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-5"
            >
              <div className="w-10 h-10 rounded-full bg-linear-to-br from-cyan-500 to-blue-600 flex items-center justify-center shrink-0 shadow-lg ring-2 ring-white/10">
                <Sparkles className="w-5 h-5 text-white animate-pulse" />
              </div>
              <div className="bg-slate-900/90 border border-slate-700/80 p-5 rounded-2xl rounded-tl-none flex items-center gap-2 shadow-xl">
                <span
                  className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-5 border-t border-white/10 bg-slate-900/80 backdrop-blur-xl">
          <div className="relative flex items-center gap-3 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about claims, patients, or denials..."
              className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all placeholder:text-slate-500 text-white shadow-inner hover:bg-slate-950/80 font-medium"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-2.5 p-2.5 bg-linear-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all text-white shadow-lg shadow-cyan-500/20 active:scale-95"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div className="flex items-center justify-center gap-2 mt-3 text-[10px] text-slate-500 font-bold tracking-wider opacity-60 uppercase">
            <AlertCircle className="w-3 h-3" />
            <p>AI-generated responses may vary. Verify critical information.</p>
          </div>
        </div>
      </main>
    </div>
  );
}

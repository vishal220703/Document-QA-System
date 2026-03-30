"use client";

import { useEffect, useState } from "react";
import { askQuestion, ConversationDetail, createConversation, getConversation } from "@/lib/api";

type Props = {
  documentId: string | null;
  filename: string | null;
  activeConversationId: string | null;
  onConversationChange: (conversationId: string) => void;
  onConversationRefresh: () => void;
};

export default function ChatPanel({
  documentId,
  filename,
  activeConversationId,
  onConversationChange,
  onConversationRefresh
}: Props) {
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadConversation = async () => {
      if (!activeConversationId) {
        setConversation(null);
        return;
      }

      try {
        const details = await getConversation(activeConversationId);
        setConversation(details);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load conversation");
      }
    };

    void loadConversation();
  }, [activeConversationId]);

  const handleAsk = async () => {
    if (!documentId) {
      setError("Upload and index a document first.");
      return;
    }

    if (!question.trim()) {
      setError("Question is required.");
      return;
    }

    setError("");
    setIsLoading(true);
    try {
      let conversationId = activeConversationId;
      if (!conversationId) {
        const created = await createConversation(documentId, filename ?? "Document Chat");
        conversationId = created.id;
        onConversationChange(created.id);
      }

      const response = await askQuestion(documentId, question, conversationId);
      const details = await getConversation(response.conversation_id);
      setConversation(details);
      onConversationRefresh();
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mx-auto flex h-[calc(100vh-1rem)] w-full max-w-5xl flex-col md:h-screen">
      <header className="border-b border-white/10 bg-slate-950/90 px-4 py-3 backdrop-blur">
        <h2 className="text-sm font-semibold text-slate-100">DocQuest Assistant</h2>
        <p className="mt-1 truncate text-xs text-slate-400">{filename ? `Using: ${filename}` : "Upload a document to begin"}</p>
      </header>

      <div className="flex-1 overflow-auto px-3 py-4 md:px-6">
        {!conversation ? (
          <div className="mx-auto mt-12 max-w-md rounded-2xl border border-white/10 bg-slate-900/50 p-6 text-center text-slate-400">
            <p>Ask anything about your uploaded document.</p>
            <p className="mt-2 text-sm">Use natural prompts like you would in ChatGPT.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {conversation.messages.map((message) => (
              <article
                key={message.id}
                className={`max-w-[92%] rounded-2xl border px-4 py-3 ${
                  message.role === "user"
                    ? "ml-auto border-blue-400/30 bg-blue-500/20"
                    : "border-slate-700 bg-slate-900/70"
                }`}
              >
                <p className="mb-1 text-xs text-slate-300">
                  <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
                </p>
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-slate-100">{message.content}</div>
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-white/10 bg-slate-950/95 px-3 py-3 backdrop-blur md:px-6 md:py-4">
        <textarea
          value={question}
          onChange={(event: React.ChangeEvent<HTMLTextAreaElement>) => setQuestion(event.target.value)}
          placeholder="Message DocQuest"
          rows={3}
          className="w-full resize-y rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-blue-400/60"
        />
        <div className="mt-2 flex justify-end">
          <button
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-600/50"
            onClick={handleAsk}
            disabled={isLoading || !documentId}
          >
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>

      {error ? <p className="mx-3 mb-3 rounded-xl border border-rose-400/50 bg-rose-900/40 px-3 py-2 text-xs text-rose-100 md:mx-6">{error}</p> : null}
    </section>
  );
}

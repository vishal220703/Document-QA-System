"use client";

import { ConversationSummary } from "@/lib/api";

function normalizeChatTitle(value: string): string {
  const raw = value.trim();
  if (!raw) return "Document Chat";
  return raw.replace(/^[a-z0-9]{10,}[_.-]+/i, "") || raw;
}

type Props = {
  items: ConversationSummary[];
  activeConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
};

export default function ConversationsPanel({
  items,
  activeConversationId,
  onSelectConversation
}: Props) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-800/40 p-3 shadow-xl shadow-black/20">
      <div>
        <h2 className="text-sm font-semibold text-slate-100">Document Chats</h2>
        <p className="mt-1 text-xs text-slate-400">Each uploaded file keeps its own saved chat.</p>
      </div>
      {items.length === 0 ? <p className="mt-3 text-xs text-slate-400">No chat yet. Upload a document to start.</p> : null}
      <div className="hide-scrollbar mt-3 grid max-h-[45vh] gap-2 overflow-y-auto overflow-x-hidden pr-1">
        {items.map((conversation) => {
          const isActive = activeConversationId === conversation.id;
          return (
            <button
              key={conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
              className={`rounded-xl border px-3 py-2 text-left transition ${
                isActive
                  ? "border-blue-400/60 bg-blue-500/20"
                  : "border-slate-700 bg-slate-900/70 hover:border-slate-500 hover:bg-slate-800"
              } overflow-hidden`}
            >
              <strong className="block truncate text-sm text-slate-100">{normalizeChatTitle(conversation.title)}</strong>
              <span className="mt-1 block line-clamp-2 break-words text-xs text-slate-400">
                {conversation.last_message_preview ?? "No messages yet"}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

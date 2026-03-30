"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import ChatPanel from "@/components/ChatPanel";
import ConversationsPanel from "@/components/ConversationsPanel";
import UploadPanel from "@/components/UploadPanel";
import { clearAuthToken, ConversationSummary, createConversation, getAuthToken, listConversations } from "@/lib/api";

function normalizeChatTitle(value: string | null | undefined): string {
  const raw = (value ?? "").trim();
  if (!raw) return "Document Chat";

  // Strip generated storage prefixes like "a3f91..._resume.pdf" or "ab12...-resume.pdf".
  const cleaned = raw.replace(/^[a-z0-9]{10,}[_.-]+/i, "");
  return cleaned || raw;
}

export default function HomePage() {
  const router = useRouter();
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [sidebarWidth, setSidebarWidth] = useState<number>(340);
  const [isResizingSidebar, setIsResizingSidebar] = useState(false);
  const [isAuthChecked, setIsAuthChecked] = useState(false);

  useEffect(() => {
    if (!getAuthToken()) {
      router.replace("/login");
      return;
    }
    setIsAuthChecked(true);
  }, [router]);

  useEffect(() => {
    if (!isResizingSidebar) return;

    const onMouseMove = (event: MouseEvent) => {
      const nextWidth = Math.min(520, Math.max(280, event.clientX));
      setSidebarWidth(nextWidth);
    };

    const onMouseUp = () => {
      setIsResizingSidebar(false);
    };

    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    return () => {
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [isResizingSidebar]);

  const refreshConversations = async () => {
    const rows = await listConversations();
    setConversations(rows);
    return rows;
  };

  useEffect(() => {
    if (!isAuthChecked) return;
    void refreshConversations();
  }, [isAuthChecked]);

  useEffect(() => {
    const ensureDocumentConversation = async () => {
      if (!isAuthChecked) return;
      if (!documentId) {
        setActiveConversationId(null);
        return;
      }

      const rows = await listConversations();
      const existing = rows.find((item) => item.document_id === documentId);

      if (existing) {
        setConversations(rows);
        setActiveConversationId(existing.id);
        return;
      }

      const created = await createConversation(documentId, normalizeChatTitle(filename));
      const updatedRows = await listConversations();
      setConversations(updatedRows);
      setActiveConversationId(created.id);
    };

    void ensureDocumentConversation();
  }, [documentId, filename, isAuthChecked]);

  if (!isAuthChecked) {
    return <main className="min-h-screen bg-slate-950" />;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div
        className="grid min-h-screen md:[grid-template-columns:var(--sidebar-width)_minmax(0,1fr)]"
        style={{ ["--sidebar-width" as string]: `${sidebarWidth}px` }}
      >
        <aside className="relative border-b border-white/10 bg-slate-900/90 p-3 backdrop-blur md:border-b-0 md:border-r">
          <div className="mb-3 flex items-center gap-2 rounded-xl border border-white/10 bg-slate-800/60 px-3 py-2 text-sm font-semibold tracking-wide text-slate-100">
            <Image src="/logo.png" alt="DocQuest logo" width={24} height={24} className="rounded" priority />
            <span className="flex-1">DocQuest</span>
            <button
              type="button"
              onClick={() => {
                clearAuthToken();
                router.replace("/login");
              }}
              className="rounded-md border border-slate-600 px-2 py-1 text-xs font-medium text-slate-300 transition hover:bg-slate-700"
            >
              Logout
            </button>
          </div>
          <button
            type="button"
            aria-label="Resize sidebar"
            className="absolute right-0 top-0 hidden h-full w-2 cursor-col-resize bg-transparent transition hover:bg-blue-500/25 md:block"
            onMouseDown={() => setIsResizingSidebar(true)}
          />
          <UploadPanel
            onUpload={(newDocumentId, newFilename) => {
              setDocumentId(newDocumentId);
              setFilename(normalizeChatTitle(newFilename));
              setActiveConversationId(null);
            }}
          />
          <ConversationsPanel
            items={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={(conversationId) => {
              setActiveConversationId(conversationId);
              const selected = conversations.find((item) => item.id === conversationId);
              if (!selected) return;
              setDocumentId(selected.document_id);
              setFilename(normalizeChatTitle(selected.title));
            }}
          />
        </aside>

        <section className="min-w-0 bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.12),transparent_35%)]">
          <ChatPanel
            documentId={documentId}
            filename={filename}
            activeConversationId={activeConversationId}
            onConversationChange={(conversationId) => setActiveConversationId(conversationId)}
            onConversationRefresh={() => void refreshConversations()}
          />
        </section>
      </div>
    </main>
  );
}

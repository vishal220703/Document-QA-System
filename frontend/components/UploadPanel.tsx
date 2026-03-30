"use client";

import { DragEvent, KeyboardEvent, useRef, useState } from "react";
import { uploadDocument } from "@/lib/api";

type Props = {
  onUpload: (documentId: string, filename: string) => void;
};

export default function UploadPanel({ onUpload }: Props) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const pickFile = () => fileInputRef.current?.click();

  const onFileChange = (selected?: File | null) => {
    if (!selected) return;
    setFile(selected);
    setStatus("");
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    onFileChange(event.dataTransfer.files?.[0]);
  };

  const onDropKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      pickFile();
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Choose a file first.");
      return;
    }

    setStatus("");
    setIsLoading(true);
    try {
      const response = await uploadDocument(file);
      onUpload(response.document_id, response.filename);
      setStatus(`Ready: ${response.filename}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mb-3 rounded-2xl border border-white/10 bg-slate-800/40 p-3 shadow-xl shadow-black/20">
      <h2 className="text-sm font-semibold text-slate-100">Knowledge File</h2>
      <p className="mt-1 text-xs text-slate-400">Upload one PDF, DOCX, or TXT document.</p>

      <div className="mt-3 grid gap-2.5">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: "none" }}
          onChange={(event) => onFileChange(event.target.files?.[0])}
        />

        <div
          className="grid gap-2 rounded-xl border border-dashed border-slate-600 bg-slate-900/70 p-3 transition hover:border-slate-500"
          role="button"
          tabIndex={0}
          onClick={pickFile}
          onDrop={onDrop}
          onDragOver={(event) => event.preventDefault()}
          onKeyDown={onDropKeyDown}
        >
          <strong className="text-sm text-slate-100">Choose file or drag and drop</strong>
          <span className="text-xs text-slate-400">The selected file becomes your current chat context.</span>
          <div>
            <button
              type="button"
              className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700"
              onClick={(event) => {
                event.stopPropagation();
                pickFile();
              }}
            >
              Browse Files
            </button>
          </div>
          {file ? (
            <span className="inline-flex w-fit max-w-full truncate rounded-full border border-slate-600 px-2 py-1 text-xs text-slate-300">
              {file.name}
            </span>
          ) : (
            <span className="inline-flex w-fit rounded-full border border-slate-600 px-2 py-1 text-xs text-slate-400">
              No file selected
            </span>
          )}
        </div>

        <button
          className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-600/50"
          onClick={handleUpload}
          disabled={!file || isLoading}
        >
          {isLoading ? "Uploading..." : "Upload and Build Index"}
        </button>
      </div>

      {status ? <p className="mt-2 text-xs text-emerald-300">{status}</p> : null}
    </section>
  );
}

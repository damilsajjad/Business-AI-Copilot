"use client";

import { useState, useRef } from "react";
import { apiFetch, apiJson } from "@/lib/api";

interface FileUploadProps {
  businessId: string;
  onUploadSuccess: (fileId: string) => void;
}

export default function FileUpload({ businessId, onUploadSuccess }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_SIZE_MB = 50;
  const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"];

  function validateFile(file: File): string | null {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return "Only CSV (.csv) and Excel (.xlsx, .xls) files are supported.";
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File size exceeds the ${MAX_SIZE_MB}MB limit.`;
    }
    return null;
  }

  async function handleFileUpload(file: File) {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiFetch(`/api/v1/businesses/${businessId}/uploads`, {
        method: "POST",
        body: formData,
        headers: {}, // Do not set Content-Type header so browser sets multipart boundary
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      const data = await response.json();
      onUploadSuccess(data.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  async function handleLoadSample() {
    setLoadingSample(true);
    setError(null);
    try {
      const data = await apiJson<{ id: string }>(
        `/api/v1/businesses/${businessId}/uploads/sample`,
        { method: "POST" }
      );
      onUploadSuccess(data.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load sample dataset.");
    } finally {
      setLoadingSample(false);
    }
  }

  function onDragOver(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(true);
  }

  function onDragLeave(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }

  return (
    <div className="w-full space-y-4">
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
          }
        }}
      />

      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !uploading && !loadingSample && fileInputRef.current?.click()}
        className={`group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-all cursor-pointer ${
          isDragging
            ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20"
            : "border-zinc-300 bg-white hover:border-indigo-400 hover:bg-zinc-50/50 dark:border-zinc-800 dark:bg-zinc-900/60 dark:hover:border-zinc-700 dark:hover:bg-zinc-900"
        } ${uploading || loadingSample ? "opacity-60 cursor-not-allowed" : ""}`}
      >
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 ring-8 ring-indigo-50/50 dark:bg-indigo-950 dark:text-indigo-400 dark:ring-indigo-950/40 transition-transform group-hover:scale-105">
          {uploading || loadingSample ? (
            <svg
              className="h-7 w-7 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          ) : (
            <svg
              className="h-7 w-7"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.75}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
              />
            </svg>
          )}
        </div>

        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          {uploading
            ? "Analyzing & Profiling Data..."
            : loadingSample
            ? "Generating Synthetic Retail Dataset..."
            : "Upload Business Dataset"}
        </h3>
        <p className="mt-1 max-w-sm text-sm text-zinc-500 dark:text-zinc-400">
          Drag and drop your spreadsheet here, or <span className="text-indigo-600 dark:text-indigo-400 font-medium">browse files</span>.
        </p>
        <p className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
          Supports CSV and multi-sheet Excel (.xlsx) up to 50MB
        </p>
      </div>

      {/* Quick 1-Click Demo Loader */}
      <div className="flex items-center justify-between rounded-xl border border-indigo-100 bg-indigo-50/50 p-4 dark:border-indigo-900/30 dark:bg-indigo-950/20">
        <div className="flex items-center gap-3">
          <span className="text-xl">📊</span>
          <div>
            <p className="text-xs font-bold text-zinc-900 dark:text-zinc-100">
              Don&apos;t have a file ready?
            </p>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Load our pre-built synthetic retail dataset (350 orders, 8 products, customer RFM history).
            </p>
          </div>
        </div>

        <button
          disabled={loadingSample || uploading}
          onClick={handleLoadSample}
          className="rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 dark:bg-indigo-500"
        >
          {loadingSample ? "Generating..." : "⚡ Load Sample Data"}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/20 dark:text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}

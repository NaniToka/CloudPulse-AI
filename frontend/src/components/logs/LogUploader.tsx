import React, { useState, useRef } from "react";
import { UploadCloud, FileText, AlertCircle, CheckCircle2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface LogUploaderProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
  uploadProgress: number;
}

const ALLOWED_EXTENSIONS = [".log", ".txt", ".json"];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export default function LogUploader({ onUpload, isUploading, uploadProgress }: LogUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File): boolean => {
    setErrorMessage(null);
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setErrorMessage(`Invalid file format '${ext}'. Only .log, .txt, and .json files are supported.`);
      return false;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the ${MAX_SIZE_MB} MB limit.`);
      return false;
    }
    setSelectedFile(file);
    return true;
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (isUploading) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (validateAndSetFile(file)) {
        await onUpload(file);
      }
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (validateAndSetFile(file)) {
        await onUpload(file);
      }
    }
  };

  return (
    <div className="w-full space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 transition-all cursor-pointer text-center group",
          isDragOver
            ? "border-brand-blue bg-brand-blue/10 scale-[1.01]"
            : "border-white/10 hover:border-brand-blue/50 hover:bg-white/[0.02]",
          isUploading && "pointer-events-none opacity-80"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".log,.txt,.json"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="p-4 rounded-full bg-brand-blue/10 border border-brand-blue/20 text-brand-blue group-hover:scale-110 transition-transform">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div className="space-y-1">
            <p className="text-base font-medium text-foreground">
              Drag & Drop server log file here, or{" "}
              <span className="text-brand-blue hover:underline">browse</span>
            </p>
            <p className="text-xs text-muted-foreground">
              Supports <code className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[11px]">.log</code>,{" "}
              <code className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[11px]">.txt</code>, and{" "}
              <code className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[11px]">.json</code> up to 10 MB
            </p>
          </div>

          {selectedFile && !isUploading && !errorMessage && (
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-md border border-emerald-500/20">
              <FileText className="w-4 h-4" />
              <span>{selectedFile.name}</span>
              <span className="text-muted-foreground">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        {isUploading && (
          <div className="mt-4 space-y-2 max-w-xs mx-auto">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Uploading & Parsing log entries…</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="h-1.5 bg-white/10" />
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="flex items-center gap-2 text-xs text-rose-400 bg-rose-500/10 p-3 rounded-lg border border-rose-500/20">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

import { useCallback, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  X,
  AlertCircle,
  CheckCircle2,
  Loader2,
  UploadCloud,
  ArrowLeft,
  ShieldCheck,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { uploadReport } from '@/lib/api/api';
import { useReportStore } from '@/stores/reportStore';
import type { ApiError } from '@/types/report.types';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const ALLOWED_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
];
const ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg'];
const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isValidFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return `Invalid file type "${ext}". Only PDF, PNG, JPG, and JPEG files are supported.`;
  }
  if (!ALLOWED_TYPES.includes(file.type) && file.type !== '') {
    return `Invalid MIME type "${file.type}". Please upload a valid medical report file.`;
  }
  if (file.size > MAX_FILE_SIZE) {
    return `File is too large (${formatFileSize(file.size)}). Maximum allowed size is ${formatFileSize(MAX_FILE_SIZE)}.`;
  }
  if (file.size === 0) {
    return 'File is empty. Please select a valid file.';
  }
  return null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
const UploadPage = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    isUploading,
    uploadProgress,
    error,
    setReport,
    setUploading,
    setProgress,
    setError,
    reset,
  } = useReportStore();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [uploadPhase, setUploadPhase] = useState<'idle' | 'uploading' | 'processing' | 'done'>('idle');

  // ---- File selection helpers ----
  const handleFileSelect = useCallback((file: File) => {
    setValidationError(null);
    setError(null);

    const err = isValidFile(file);
    if (err) {
      setValidationError(err);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  }, [setError]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
    // Reset the input so the same file can be re-selected after removal
    e.target.value = '';
  };

  const removeFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    reset();
    setUploadPhase('idle');
  };

  // ---- Upload handler ----
  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadPhase('uploading');

    try {
      const response = await uploadReport(selectedFile, (pct) => {
        setProgress(pct);
        if (pct >= 100) {
          setUploadPhase('processing');
        }
      });

      setUploadPhase('done');
      setReport(response);

      // Brief pause to show success before navigating
      setTimeout(() => {
        navigate('/report');
      }, 800);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr);
      setUploadPhase('idle');
    }
  };

  // ---- Derived state ----
  const displayError = validationError || error?.message;
  const isProcessing = uploadPhase === 'processing';
  const isDone = uploadPhase === 'done';

  return (
    <div className="min-h-screen bg-background">
      {/* Decorative background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 right-0 h-[500px] w-[500px] rounded-full bg-teal-500/10 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 h-[400px] w-[400px] rounded-full bg-sky-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Back button */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <button
            onClick={() => navigate('/')}
            className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </button>
        </motion.div>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10 text-center"
        >
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-teal-500/20 bg-teal-500/5 px-4 py-1.5 text-sm font-medium text-teal-700 dark:text-teal-300">
            <ShieldCheck className="h-4 w-4" />
            Secure & Private
          </div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Upload Your Medical Report
          </h1>
          <p className="mt-3 text-lg text-muted-foreground">
            Upload a PDF or image of your lab report for instant AI-powered analysis
          </p>
        </motion.div>

        {/* Upload Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="glass rounded-2xl p-8 shadow-soft-lg"
        >
          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={!isUploading && !selectedFile ? handleBrowseClick : undefined}
            className={`
              relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed
              px-6 py-14 transition-all duration-300
              ${isDragging
                ? 'border-teal-500 bg-teal-500/5 scale-[1.02]'
                : selectedFile
                  ? 'border-teal-500/40 bg-teal-500/5'
                  : 'border-border hover:border-teal-500/40 hover:bg-muted/50'
              }
              ${isUploading ? 'pointer-events-none' : ''}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleInputChange}
              className="hidden"
              aria-label="Choose medical report file"
            />

            <AnimatePresence mode="wait">
              {!selectedFile && !isUploading && (
                <motion.div
                  key="drop-prompt"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="flex flex-col items-center text-center"
                >
                  <div className="mb-4 rounded-2xl bg-gradient-to-br from-teal-500/10 to-sky-500/10 p-4">
                    <UploadCloud className="h-10 w-10 text-teal-600 dark:text-teal-400" />
                  </div>
                  <p className="text-base font-semibold text-foreground">
                    Drag & drop your report here
                  </p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    or{' '}
                    <span className="font-medium text-teal-600 dark:text-teal-400 underline underline-offset-2">
                      click to browse
                    </span>
                  </p>
                  <p className="mt-4 text-xs text-muted-foreground">
                    Supports PDF, PNG, JPG, JPEG • Max 25 MB
                  </p>
                </motion.div>
              )}

              {selectedFile && !isUploading && !isDone && (
                <motion.div
                  key="file-selected"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex w-full items-center gap-4"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-500/10">
                    <FileText className="h-6 w-6 text-teal-600 dark:text-teal-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile();
                    }}
                    className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500"
                    aria-label="Remove file"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </motion.div>
              )}

              {isUploading && (
                <motion.div
                  key="uploading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex w-full flex-col items-center gap-4"
                >
                  {isProcessing ? (
                    <>
                      <div className="relative">
                        <Loader2 className="h-10 w-10 animate-spin text-teal-600 dark:text-teal-400" />
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-semibold text-foreground">
                          Analyzing your report...
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          Extracting text, parsing patient info & lab results
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <Upload className="h-8 w-8 text-teal-600 dark:text-teal-400 animate-pulse" />
                      <div className="w-full max-w-xs">
                        <div className="mb-2 flex items-center justify-between text-xs">
                          <span className="font-medium text-foreground">Uploading...</span>
                          <span className="text-muted-foreground">{uploadProgress}%</span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                          <motion.div
                            className="h-full rounded-full bg-gradient-to-r from-teal-500 to-sky-500"
                            initial={{ width: 0 }}
                            animate={{ width: `${uploadProgress}%` }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                      </div>
                    </>
                  )}
                </motion.div>
              )}

              {isDone && (
                <motion.div
                  key="done"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center gap-3"
                >
                  <div className="rounded-full bg-emerald-500/10 p-3">
                    <CheckCircle2 className="h-8 w-8 text-emerald-500" />
                  </div>
                  <p className="text-sm font-semibold text-foreground">
                    Report analyzed successfully!
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Redirecting to your results...
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Error display */}
          <AnimatePresence>
            {displayError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 overflow-hidden"
              >
                <div className="flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                  <AlertCircle className="h-5 w-5 shrink-0 text-red-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-600 dark:text-red-400">
                      {displayError}
                    </p>
                    {error?.status === 0 && (
                      <p className="mt-1 text-xs text-muted-foreground">
                        Make sure the backend server is running at{' '}
                        <code className="rounded bg-muted px-1 py-0.5 text-xs">
                          {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                        </code>
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload button */}
          {selectedFile && !isUploading && !isDone && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6"
            >
              <Button
                size="lg"
                className="w-full"
                onClick={handleUpload}
              >
                <Upload className="h-5 w-5" />
                Analyze Report
              </Button>
            </motion.div>
          )}
        </motion.div>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8 grid gap-4 sm:grid-cols-3"
        >
          {[
            { icon: FileText, title: 'Clear Scans', desc: 'Upload high-quality scans for best accuracy' },
            { icon: ShieldCheck, title: 'Data Privacy', desc: 'Your reports are processed securely and never stored' },
            { icon: CheckCircle2, title: 'Instant Results', desc: 'Get AI analysis within seconds of uploading' },
          ].map((tip) => (
            <div
              key={tip.title}
              className="flex items-start gap-3 rounded-xl bg-white/50 dark:bg-slate-800/50 p-4 border border-border/50"
            >
              <tip.icon className="h-5 w-5 shrink-0 text-teal-600 dark:text-teal-400 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-foreground">{tip.title}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{tip.desc}</p>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default UploadPage;
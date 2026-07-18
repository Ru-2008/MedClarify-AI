import { create } from 'zustand';
import type { UploadResponse, ApiError } from '@/types/report.types';

// ---------------------------------------------------------------------------
// Report store — holds upload state and the parsed report response
// ---------------------------------------------------------------------------

interface ReportState {
  /** The full backend response after a successful upload */
  report: UploadResponse | null;

  /** Whether an upload is currently in progress */
  isUploading: boolean;

  /** Upload progress percentage (0-100) */
  uploadProgress: number;

  /** Last error from the upload attempt */
  error: ApiError | null;

  // Actions
  setReport: (report: UploadResponse) => void;
  setUploading: (isUploading: boolean) => void;
  setProgress: (percent: number) => void;
  setError: (error: ApiError | null) => void;
  reset: () => void;
}

export const useReportStore = create<ReportState>((set) => ({
  report: null,
  isUploading: false,
  uploadProgress: 0,
  error: null,

  setReport: (report) =>
    set({ report, isUploading: false, uploadProgress: 100, error: null }),

  setUploading: (isUploading) =>
    set({ isUploading, error: null, uploadProgress: 0 }),

  setProgress: (uploadProgress) => set({ uploadProgress }),

  setError: (error) => set({ error, isUploading: false, uploadProgress: 0 }),

  reset: () =>
    set({
      report: null,
      isUploading: false,
      uploadProgress: 0,
      error: null,
    }),
}));

import axios, { AxiosError, AxiosProgressEvent } from 'axios';
import type { UploadResponse, ApiError } from '@/types/report.types';

// ---------------------------------------------------------------------------
// Axios instance — reads base URL from VITE_API_URL env variable
// ---------------------------------------------------------------------------
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000, // 120s — large PDFs with OCR can take time
});

// ---------------------------------------------------------------------------
// Error normalizer
// ---------------------------------------------------------------------------
function normalizeError(err: unknown): ApiError {
  if (err instanceof AxiosError) {
    const status = err.response?.status;
    const detail =
      err.response?.data?.detail ??
      err.response?.data?.message ??
      err.message;

    if (err.code === 'ECONNABORTED') {
      return {
        message: 'Request timed out. The server took too long to respond.',
        status,
        detail,
      };
    }

    if (!err.response) {
      return {
        message:
          'Cannot reach the server. Please check if the backend is running.',
        status: 0,
        detail: err.message,
      };
    }

    if (status === 400) {
      return {
        message: detail || 'Invalid file. Please upload a valid PDF or image.',
        status,
        detail,
      };
    }

    if (status === 500) {
      return {
        message: 'Server error while processing the report. Please try again.',
        status,
        detail,
      };
    }

    return {
      message: detail || 'An unexpected error occurred.',
      status,
      detail,
    };
  }

  return {
    message: err instanceof Error ? err.message : 'An unknown error occurred.',
  };
}

// ---------------------------------------------------------------------------
// Upload API call
// ---------------------------------------------------------------------------
export async function uploadReport(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post<UploadResponse>(
      '/api/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event: AxiosProgressEvent) => {
          if (event.total && onProgress) {
            const percent = Math.round((event.loaded * 100) / event.total);
            onProgress(percent);
          }
        },
      },
    );

    if (!response.data.success) {
      throw new Error('Upload completed but server reported failure.');
    }

    return response.data;
  } catch (err) {
    throw normalizeError(err);
  }
}

export { apiClient };

// ============================================================
// TypeScript types matching the real FastAPI backend response
// from POST /api/upload
// ============================================================

/** Reference range for a laboratory test */
export interface ReferenceRange {
  min: number | null;
  max: number | null;
  low: number | null;
  high: number | null;
}

/** A single enriched laboratory test result */
export interface LabTest {
  test_name: string;
  value: number | null;
  unit: string | null;
  reference_range: ReferenceRange | null;
  status: 'NORMAL' | 'LOW' | 'HIGH' | 'BORDERLINE' | 'CRITICAL' | 'UNKNOWN';
  severity: string;
  confidence: number;
  source_text: string;
  extraction_strategy: string;
}

/** Patient information extracted from the report */
export interface PatientInfo {
  name: string | null;
  age: string | null;
  gender: string | null;
  report_date: string | null;
  lab_name: string | null;
  doctor_name: string | null;
  patient_id: string | null;
  sample_type: string | null;
  collection_date: string | null;
  approval_date: string | null;
  hospital: string | null;
  doctor: string | null;
  laboratory: string | null;
  registration_number: string | null;
  uhid: string | null;
  lab_id: string | null;
}

/** Interpretation of an abnormal test from the Knowledge Engine */
export interface Interpretation {
  test_name: string;
  finding: string;
  explanation: string;
  evidence: string[];
  recommendations: string[];
}

/** Metadata about the extraction/OCR process */
export interface ProcessingMetadata {
  extraction_method: string;
  ocr_pages: number[];
  processing_time_ms: number;
}

/** The full parsed_data object from the backend */
export interface ParsedData {
  patient: PatientInfo;
  laboratory_tests: LabTest[];
  abnormal_tests?: LabTest[];
  interpretation?: Interpretation[];
  summary?: string;
  confidence?: number;
  warnings?: string[];
  processing_metadata?: ProcessingMetadata;
}

/** Top-level response from POST /api/upload */
export interface UploadResponse {
  success: boolean;
  filename: string;
  original_name: string;
  preview_text: string | null;
  character_count: number;
  pages: number;
  parsed_data: ParsedData;
}

/** Normalized API error shape */
export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

import type { LabTest } from '@/types/report.types';
import {
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Minus,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Status configuration — single source of truth for colors/icons
// ---------------------------------------------------------------------------

export interface StatusConfig {
  label: string;
  color: string;
  bg: string;
  bgSolid: string;
  dot: string;
  border: string;
  icon: React.ElementType;
}

export function getStatusConfig(status: string): StatusConfig {
  switch (status.toUpperCase()) {
    case 'NORMAL':
      return {
        label: 'Normal',
        color: 'text-emerald-600 dark:text-emerald-400',
        bg: 'bg-emerald-500/10',
        bgSolid: 'bg-emerald-500',
        dot: 'bg-emerald-500',
        border: 'border-emerald-500/20',
        icon: CheckCircle2,
      };
    case 'HIGH':
      return {
        label: 'High',
        color: 'text-red-600 dark:text-red-400',
        bg: 'bg-red-500/10',
        bgSolid: 'bg-red-500',
        dot: 'bg-red-500',
        border: 'border-red-500/20',
        icon: TrendingUp,
      };
    case 'LOW':
      return {
        label: 'Low',
        color: 'text-blue-600 dark:text-blue-400',
        bg: 'bg-blue-500/10',
        bgSolid: 'bg-blue-500',
        dot: 'bg-blue-500',
        border: 'border-blue-500/20',
        icon: TrendingDown,
      };
    case 'BORDERLINE':
      return {
        label: 'Borderline',
        color: 'text-amber-600 dark:text-amber-400',
        bg: 'bg-amber-500/10',
        bgSolid: 'bg-amber-500',
        dot: 'bg-amber-500',
        border: 'border-amber-500/20',
        icon: AlertTriangle,
      };
    case 'CRITICAL':
      return {
        label: 'Critical',
        color: 'text-rose-600 dark:text-rose-400',
        bg: 'bg-rose-500/10',
        bgSolid: 'bg-rose-500',
        dot: 'bg-rose-500',
        border: 'border-rose-500/20',
        icon: AlertTriangle,
      };
    default:
      return {
        label: 'Unknown',
        color: 'text-gray-500 dark:text-gray-400',
        bg: 'bg-gray-500/10',
        bgSolid: 'bg-gray-400',
        dot: 'bg-gray-400',
        border: 'border-gray-500/20',
        icon: Minus,
      };
  }
}

// ---------------------------------------------------------------------------
// Reference range formatter
// ---------------------------------------------------------------------------

export function formatRefRange(test: LabTest): string {
  const r = test.reference_range;
  if (!r) return '—';
  const low = r.low ?? r.min;
  const high = r.high ?? r.max;
  if (low != null && high != null) return `${low} – ${high}`;
  if (low != null) return `≥ ${low}`;
  if (high != null) return `≤ ${high}`;
  return '—';
}

// ---------------------------------------------------------------------------
// Confidence configuration
// ---------------------------------------------------------------------------

export function getConfidenceConfig(confidence: number) {
  if (confidence >= 90)
    return { label: 'High', color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-500/10', stroke: '#10b981' };
  if (confidence >= 70)
    return { label: 'Medium', color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-500/10', stroke: '#f59e0b' };
  return { label: 'Low', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-500/10', stroke: '#ef4444' };
}

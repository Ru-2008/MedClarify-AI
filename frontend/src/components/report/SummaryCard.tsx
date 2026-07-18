import { motion } from 'framer-motion';
import {
  HeartPulse,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
} from 'lucide-react';

interface SummaryCardProps {
  summary: string;
  abnormalCount: number;
  totalTests: number;
  warnings: string[];
}

export function SummaryCard({ summary, abnormalCount, totalTests, warnings }: SummaryCardProps) {
  const hasAbnormal = abnormalCount > 0;
  const normalCount = totalTests - abnormalCount;

  // Parse the summary into sections (backend sends labeled paragraphs)
  const sections = summary.split('\n\n').filter(Boolean);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
      className="glass rounded-2xl p-6 shadow-soft"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className={`rounded-xl p-2.5 ${hasAbnormal ? 'bg-amber-500/10' : 'bg-emerald-500/10'}`}>
          <HeartPulse className={`h-5 w-5 ${hasAbnormal ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`} />
        </div>
        <div>
          <h2 className="font-display text-lg font-bold text-foreground">Overall Health Summary</h2>
          <p className="text-xs text-muted-foreground">
            {totalTests} tests analyzed • {normalCount} normal • {abnormalCount} abnormal
          </p>
        </div>
      </div>

      {/* Quick status banner */}
      <div className={`mb-5 rounded-xl p-4 ${hasAbnormal ? 'bg-amber-500/5 border border-amber-500/15' : 'bg-emerald-500/5 border border-emerald-500/15'}`}>
        <div className="flex items-start gap-3">
          {hasAbnormal ? (
            <ShieldAlert className="h-5 w-5 shrink-0 mt-0.5 text-amber-500" />
          ) : (
            <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5 text-emerald-500" />
          )}
          <p className={`text-sm font-medium leading-relaxed ${hasAbnormal ? 'text-amber-700 dark:text-amber-300' : 'text-emerald-700 dark:text-emerald-300'}`}>
            {hasAbnormal
              ? `${abnormalCount} abnormal finding${abnormalCount > 1 ? 's' : ''} require${abnormalCount === 1 ? 's' : ''} attention. Please consult your healthcare professional.`
              : 'All laboratory values are within the normal range. No abnormalities detected.'}
          </p>
        </div>
      </div>

      {/* Summary paragraphs */}
      <div className="space-y-3">
        {sections.map((paragraph, i) => (
          <p key={i} className="text-sm leading-relaxed text-foreground/80">
            {paragraph}
          </p>
        ))}
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="mt-5 rounded-xl border border-amber-500/15 bg-amber-500/5 p-4">
          <div className="flex items-center gap-2 mb-2.5">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            <p className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
              Extraction Warnings
            </p>
          </div>
          <ul className="space-y-1.5">
            {warnings.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-500" />
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}

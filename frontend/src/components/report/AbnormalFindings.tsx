import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Lightbulb,
  TrendingUp,
  TrendingDown,
  Activity,
} from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { getStatusConfig, formatRefRange } from './helpers';
import type { LabTest, Interpretation } from '@/types/report.types';

interface AbnormalFindingsProps {
  abnormalTests: LabTest[];
  interpretations: Interpretation[];
}

function FindingCard({ test, interp }: { test: LabTest; interp?: Interpretation }) {
  const [isOpen, setIsOpen] = useState(false);
  const sc = getStatusConfig(test.status);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl border ${sc.border} ${sc.bg} overflow-hidden transition-shadow hover:shadow-soft`}
    >
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-4 p-4 text-left"
      >
        <div className={`rounded-lg p-2 ${sc.bg}`}>
          {test.status === 'HIGH' || test.status === 'CRITICAL' ? (
            <TrendingUp className={`h-4 w-4 ${sc.color}`} />
          ) : (
            <TrendingDown className={`h-4 w-4 ${sc.color}`} />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground">{test.test_name}</p>
          <div className="flex items-center gap-2 mt-0.5">
            <span className={`text-sm font-bold ${sc.color}`}>
              {test.value != null ? test.value : '—'} {test.unit || ''}
            </span>
            <span className="text-xs text-muted-foreground">
              (ref: {formatRefRange(test)})
            </span>
          </div>
        </div>
        <StatusBadge status={test.status} />
        {interp && (
          isOpen
            ? <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0" />
            : <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
        )}
      </button>

      {/* Expandable interpretation */}
      <AnimatePresence>
        {isOpen && interp && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border/30 px-4 pb-4 pt-3 space-y-4">
              {/* Explanation */}
              {interp.explanation && (
                <div>
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Lightbulb className="h-3.5 w-3.5 text-amber-500" />
                    <p className="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground">Explanation</p>
                  </div>
                  <p className="text-sm leading-relaxed text-foreground/80">{interp.explanation}</p>
                </div>
              )}

              {/* Evidence */}
              {interp.evidence && interp.evidence.length > 0 && (
                <div>
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Activity className="h-3.5 w-3.5 text-sky-500" />
                    <p className="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground">Evidence</p>
                  </div>
                  <ul className="space-y-1">
                    {interp.evidence.map((e, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-sky-500" />
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {interp.recommendations && interp.recommendations.length > 0 && (
                <div>
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-teal-500" />
                    <p className="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground">Recommendations</p>
                  </div>
                  <ul className="space-y-1">
                    {interp.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-teal-700 dark:text-teal-300">
                        <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal-500" />
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Low confidence warning */}
              {test.confidence < 0.8 && (
                <div className="flex items-center gap-2 rounded-lg bg-amber-500/10 p-2.5 text-xs text-amber-600 dark:text-amber-400">
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                  Low extraction confidence ({Math.round(test.confidence * 100)}%) — verify this value against your original report.
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function AbnormalFindings({ abnormalTests, interpretations }: AbnormalFindingsProps) {
  if (abnormalTests.length === 0) return null;

  // Map interpretations by test_name for quick lookup
  const interpMap = new Map<string, Interpretation>();
  interpretations.forEach((interp) => {
    interpMap.set(interp.test_name, interp);
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass rounded-2xl p-6 shadow-soft"
    >
      <div className="flex items-center gap-3 mb-5">
        <div className="rounded-xl bg-red-500/10 p-2.5">
          <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
        </div>
        <div>
          <h2 className="font-display text-lg font-bold text-foreground">Abnormal Findings</h2>
          <p className="text-xs text-muted-foreground">
            {abnormalTests.length} test{abnormalTests.length !== 1 ? 's' : ''} outside normal range — tap to expand
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {abnormalTests.map((test, i) => (
          <FindingCard
            key={`${test.test_name}-${i}`}
            test={test}
            interp={interpMap.get(test.test_name)}
          />
        ))}
      </div>
    </motion.div>
  );
}

import { motion } from 'framer-motion';

export function HeroIllustration() {
  return (
    <div className="relative mx-auto w-full max-w-lg" aria-hidden="true">
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-teal-500/20 via-sky-500/10 to-transparent blur-2xl" />

      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        className="relative rounded-2xl border border-border bg-card p-6 shadow-soft-lg"
      >
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-red-400" />
            <div className="h-3 w-3 rounded-full bg-amber-400" />
            <div className="h-3 w-3 rounded-full bg-emerald-400" />
          </div>
          <span className="text-xs font-medium text-muted-foreground">
            Pathology Report
          </span>
        </div>

        <svg viewBox="0 0 320 200" className="w-full" fill="none">
          <rect x="20" y="20" width="120" height="8" rx="4" fill="currentColor" className="text-muted" />
          <rect x="20" y="40" width="180" height="6" rx="3" fill="currentColor" className="text-muted/70" />
          <rect x="20" y="54" width="160" height="6" rx="3" fill="currentColor" className="text-muted/70" />
          <rect x="20" y="80" width="280" height="40" rx="8" fill="currentColor" className="text-teal-500/10" />
          <rect x="30" y="90" width="80" height="6" rx="3" fill="#14b8a6" />
          <rect x="30" y="104" width="60" height="6" rx="3" fill="#0ea5e9" />
          <rect x="20" y="140" width="90" height="40" rx="8" fill="currentColor" className="text-amber-500/15" />
          <rect x="120" y="140" width="90" height="40" rx="8" fill="currentColor" className="text-teal-500/15" />
          <rect x="220" y="140" width="80" height="40" rx="8" fill="currentColor" className="text-sky-500/15" />
        </svg>
      </motion.div>

      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        className="absolute -right-4 top-8 rounded-xl border border-border bg-card px-4 py-3 shadow-soft-lg sm:-right-8"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10">
            <svg viewBox="0 0 24 24" className="h-5 w-5 text-teal-600" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <p className="text-xs font-semibold text-foreground">AI Analysis</p>
            <p className="text-xs text-muted-foreground">3 insights found</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        className="absolute -left-4 bottom-4 rounded-xl border border-border bg-card px-4 py-3 shadow-soft-lg sm:-left-8"
      >
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-gradient-brand" />
          <div>
            <p className="text-xs font-semibold text-foreground">Health Score</p>
            <p className="text-sm font-bold text-teal-600">82 / 100</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

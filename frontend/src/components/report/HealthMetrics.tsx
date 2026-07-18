import { motion } from 'framer-motion';
import {
  FlaskConical,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Clock,
  Shield,
  Zap,
} from 'lucide-react';
import { ConfidenceRing } from './ConfidenceRing';
import type { ProcessingMetadata } from '@/types/report.types';

interface HealthMetricsProps {
  totalTests: number;
  normalCount: number;
  abnormalCount: number;
  confidence: number | undefined;
  pages: number;
  processingTimeMs: number | undefined;
}

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } },
};

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  colorClass: string;
  bgClass: string;
}

function MetricCard({ label, value, icon: Icon, colorClass, bgClass }: MetricCardProps) {
  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="glass rounded-xl p-4 cursor-default group transition-shadow hover:shadow-soft-lg"
    >
      <div className={`mb-3 inline-flex rounded-lg p-2 ${bgClass}`}>
        <Icon className={`h-4 w-4 ${colorClass}`} />
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="mt-0.5 text-xs text-muted-foreground">{label}</p>
    </motion.div>
  );
}

export function HealthMetrics({
  totalTests,
  normalCount,
  abnormalCount,
  confidence,
  pages,
  processingTimeMs,
}: HealthMetricsProps) {
  const processingTimeSec = processingTimeMs != null ? (processingTimeMs / 1000).toFixed(1) : null;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6"
    >
      <MetricCard
        label="Total Tests"
        value={totalTests}
        icon={FlaskConical}
        colorClass="text-teal-600 dark:text-teal-400"
        bgClass="bg-teal-500/10"
      />
      <MetricCard
        label="Normal"
        value={normalCount}
        icon={CheckCircle2}
        colorClass="text-emerald-600 dark:text-emerald-400"
        bgClass="bg-emerald-500/10"
      />
      <MetricCard
        label="Abnormal"
        value={abnormalCount}
        icon={AlertTriangle}
        colorClass="text-red-600 dark:text-red-400"
        bgClass="bg-red-500/10"
      />
      {confidence != null && (
        <motion.div
          variants={cardVariants}
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
          className="glass rounded-xl p-4 cursor-default flex flex-col items-center justify-center transition-shadow hover:shadow-soft-lg"
        >
          <ConfidenceRing confidence={confidence} size={64} />
          <p className="mt-1 text-xs text-muted-foreground">Confidence</p>
        </motion.div>
      )}
      <MetricCard
        label="Pages"
        value={pages}
        icon={FileText}
        colorClass="text-sky-600 dark:text-sky-400"
        bgClass="bg-sky-500/10"
      />
      {processingTimeSec != null && (
        <MetricCard
          label="Processing"
          value={`${processingTimeSec}s`}
          icon={Zap}
          colorClass="text-violet-600 dark:text-violet-400"
          bgClass="bg-violet-500/10"
        />
      )}
    </motion.div>
  );
}

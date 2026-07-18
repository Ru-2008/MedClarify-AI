import { motion } from 'framer-motion';
import { getConfidenceConfig } from './helpers';

interface ConfidenceRingProps {
  confidence: number;
  size?: number;
}

export function ConfidenceRing({ confidence, size = 80 }: ConfidenceRingProps) {
  const config = getConfidenceConfig(confidence);
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (confidence / 100) * circumference;
  const center = size / 2;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-border"
        />
        {/* Progress */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={config.stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-lg font-bold ${config.color}`}>{confidence}%</span>
      </div>
    </div>
  );
}

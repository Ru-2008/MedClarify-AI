import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { BarChart3 } from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { LabTest } from '@/types/report.types';

interface ChartsSectionProps {
  tests: LabTest[];
}

const STATUS_COLORS: Record<string, string> = {
  NORMAL: '#10b981',
  HIGH: '#ef4444',
  LOW: '#3b82f6',
  BORDERLINE: '#f59e0b',
  CRITICAL: '#e11d48',
  UNKNOWN: '#9ca3af',
};

const STATUS_LABELS: Record<string, string> = {
  NORMAL: 'Normal',
  HIGH: 'High',
  LOW: 'Low',
  BORDERLINE: 'Borderline',
  CRITICAL: 'Critical',
  UNKNOWN: 'Unknown',
};

export function ChartsSection({ tests }: ChartsSectionProps) {
  if (tests.length === 0) return null;

  // Status distribution for pie & bar
  const statusData = useMemo(() => {
    const counts: Record<string, number> = {};
    tests.forEach((t) => {
      const s = t.status.toUpperCase();
      counts[s] = (counts[s] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([status, count]) => ({
        name: STATUS_LABELS[status] || status,
        value: count,
        color: STATUS_COLORS[status] || '#9ca3af',
      }))
      .sort((a, b) => b.value - a.value);
  }, [tests]);

  // Normal vs Abnormal pie
  const normalVsAbnormal = useMemo(() => {
    const normal = tests.filter((t) => t.status.toUpperCase() === 'NORMAL').length;
    const abnormal = tests.length - normal;
    return [
      { name: 'Normal', value: normal, color: '#10b981' },
      { name: 'Abnormal', value: abnormal, color: '#ef4444' },
    ].filter((d) => d.value > 0);
  }, [tests]);

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number; payload: { color: string } }> }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="glass rounded-lg px-3 py-2 shadow-soft text-xs">
        <p className="font-semibold text-foreground">{payload[0].name}</p>
        <p className="text-muted-foreground">{payload[0].value} test{payload[0].value !== 1 ? 's' : ''}</p>
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35 }}
      className="glass rounded-2xl p-6 shadow-soft"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="rounded-xl bg-violet-500/10 p-2.5">
          <BarChart3 className="h-5 w-5 text-violet-600 dark:text-violet-400" />
        </div>
        <div>
          <h2 className="font-display text-lg font-bold text-foreground">Visualizations</h2>
          <p className="text-xs text-muted-foreground">Distribution of test results</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Normal vs Abnormal Pie */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Normal vs Abnormal
          </p>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={normalVsAbnormal}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {normalVsAbnormal.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  formatter={(value: string) => <span className="text-xs text-foreground">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status Distribution Bar */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Status Distribution
          </p>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  className="text-muted-foreground"
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  className="text-muted-foreground"
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={40}>
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

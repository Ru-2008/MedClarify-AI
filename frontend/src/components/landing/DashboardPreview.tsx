import { motion } from 'framer-motion';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Sparkles, TrendingUp } from 'lucide-react';
import { SectionTitle } from './SectionTitle';

const chartData = [
  { month: 'Jan', hemoglobin: 13.2, glucose: 95 },
  { month: 'Feb', hemoglobin: 13.5, glucose: 92 },
  { month: 'Mar', hemoglobin: 13.1, glucose: 98 },
  { month: 'Apr', hemoglobin: 13.8, glucose: 89 },
  { month: 'May', hemoglobin: 14.0, glucose: 87 },
  { month: 'Jun', hemoglobin: 14.2, glucose: 85 },
];

const labCards = [
  { name: 'Hemoglobin', value: '14.2', unit: 'g/dL', range: '13.0 – 17.0', status: 'normal' },
  { name: 'Fasting Glucose', value: '85', unit: 'mg/dL', range: '70 – 100', status: 'normal' },
  { name: 'Total Cholesterol', value: '218', unit: 'mg/dL', range: '< 200', status: 'high' },
  { name: 'Vitamin D', value: '22', unit: 'ng/mL', range: '30 – 100', status: 'low' },
];

const recommendations = [
  'Discuss elevated cholesterol with your primary care provider',
  'Consider vitamin D supplementation after consulting your doctor',
  'Continue monitoring glucose levels at your next annual checkup',
];

export function DashboardPreview() {
  return (
    <section className="bg-muted/30 py-20 sm:py-28" aria-labelledby="demo-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Demo Preview"
          title="Your health, beautifully organized"
          description="See how MedClarify AI transforms raw lab data into a premium dashboard designed for clarity."
        />

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-16 overflow-hidden rounded-3xl border border-border bg-card shadow-soft-lg"
        >
          <div className="flex items-center gap-2 border-b border-border bg-muted/50 px-6 py-3">
            <div className="h-3 w-3 rounded-full bg-red-400" />
            <div className="h-3 w-3 rounded-full bg-amber-400" />
            <div className="h-3 w-3 rounded-full bg-emerald-400" />
            <span className="ml-2 text-xs font-medium text-muted-foreground">
              MedClarify Dashboard — Preview
            </span>
          </div>

          <div className="p-6 sm:p-8">
            <div className="mb-8 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Patient</p>
                <h3 className="text-xl font-bold text-foreground">Sarah Mitchell</h3>
                <p className="text-sm text-muted-foreground">
                  Complete Blood Count · June 12, 2026
                </p>
              </div>

              <div className="flex items-center gap-4 rounded-2xl border border-border bg-background px-6 py-4">
                <div className="relative flex h-16 w-16 items-center justify-center">
                  <svg className="h-16 w-16 -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
                    <circle
                      cx="18"
                      cy="18"
                      r="15.5"
                      fill="none"
                      stroke="currentColor"
                      className="text-muted"
                      strokeWidth="3"
                    />
                    <circle
                      cx="18"
                      cy="18"
                      r="15.5"
                      fill="none"
                      stroke="url(#scoreGradient)"
                      strokeWidth="3"
                      strokeDasharray="82 100"
                      strokeLinecap="round"
                    />
                    <defs>
                      <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#14b8a6" />
                        <stop offset="100%" stopColor="#0ea5e9" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <span className="absolute text-lg font-bold text-foreground">82</span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">Health Score</p>
                  <p className="flex items-center gap-1 text-xs text-teal-600 dark:text-teal-400">
                    <TrendingUp className="h-3 w-3" aria-hidden="true" />
                    Good overall
                  </p>
                </div>
              </div>
            </div>

            <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {labCards.map((lab) => (
                <div
                  key={lab.name}
                  className="rounded-xl border border-border bg-background p-4"
                >
                  <p className="text-xs font-medium text-muted-foreground">{lab.name}</p>
                  <p className="mt-1 text-2xl font-bold text-foreground">
                    {lab.value}
                    <span className="ml-1 text-sm font-normal text-muted-foreground">
                      {lab.unit}
                    </span>
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">Ref: {lab.range}</p>
                  <span
                    className={`mt-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      lab.status === 'normal'
                        ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                        : lab.status === 'high'
                          ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400'
                          : 'bg-red-500/10 text-red-700 dark:text-red-400'
                    }`}
                  >
                    {lab.status === 'normal' ? 'Normal' : lab.status === 'high' ? 'Above range' : 'Below range'}
                  </span>
                </div>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-5">
              <div className="rounded-xl border border-border bg-background p-4 lg:col-span-3">
                <p className="mb-4 text-sm font-semibold text-foreground">
                  Biomarker Trends
                </p>
                <div className="h-48 w-full" aria-label="Sample biomarker trend chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="hemoglobinGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#14b8a6" stopOpacity={0.3} />
                          <stop offset="100%" stopColor="#14b8a6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="hemoglobin"
                        stroke="#14b8a6"
                        fill="url(#hemoglobinGrad)"
                        name="Hemoglobin"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="space-y-4 lg:col-span-2">
                <div className="rounded-xl border border-border bg-background p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-teal-600" aria-hidden="true" />
                    <p className="text-sm font-semibold text-foreground">AI Summary</p>
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    Most results are within normal ranges. Cholesterol is slightly elevated
                    and vitamin D is below the recommended range. Consider discussing these
                    findings with your healthcare provider.
                  </p>
                </div>

                <div className="rounded-xl border border-border bg-background p-4">
                  <p className="mb-3 text-sm font-semibold text-foreground">
                    Recommendations
                  </p>
                  <ul className="space-y-2" role="list">
                    {recommendations.map((rec) => (
                      <li
                        key={rec}
                        className="flex items-start gap-2 text-xs leading-relaxed text-muted-foreground"
                      >
                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Sample data for demonstration only. Not intended as medical advice.
        </p>
      </div>
    </section>
  );
}

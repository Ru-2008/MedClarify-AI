import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';
import { SectionTitle } from './SectionTitle';
import { cn } from '@/lib/utils';

const traditionalItems = [
  'Dense medical terminology',
  'No visual context for trends',
  'Difficult to spot what changed',
  'Hard to share with family',
];

const medclarifyItems = [
  'AI explanations in plain language',
  'Beautiful charts and timelines',
  'Overall health score overview',
  'Easy-to-read downloadable summaries',
];

interface ComparisonColumnProps {
  title: string;
  items: string[];
  variant: 'traditional' | 'medclarify';
}

function ComparisonColumn({ title, items, variant }: ComparisonColumnProps) {
  const isMedclarify = variant === 'medclarify';

  return (
    <motion.div
      initial={{ opacity: 0, x: isMedclarify ? 20 : -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className={cn(
        'rounded-2xl border p-8 shadow-soft',
        isMedclarify
          ? 'border-teal-500/30 bg-gradient-to-br from-teal-500/5 to-sky-500/5 ring-1 ring-teal-500/20'
          : 'border-border bg-card',
      )}
    >
      <h3 className="mb-6 text-xl font-bold text-foreground">{title}</h3>
      <ul className="space-y-4" role="list">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-3">
            {isMedclarify ? (
              <Check
                className="mt-0.5 h-5 w-5 shrink-0 text-teal-600 dark:text-teal-400"
                aria-hidden="true"
              />
            ) : (
              <X
                className="mt-0.5 h-5 w-5 shrink-0 text-red-500"
                aria-hidden="true"
              />
            )}
            <span className="text-sm leading-relaxed text-muted-foreground">
              {item}
            </span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

export function Comparison() {
  return (
    <section
      id="about"
      className="py-20 sm:py-28"
      aria-labelledby="comparison-heading"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Why MedClarify AI"
          title="A better way to understand your health data"
          description="Traditional lab reports were designed for clinicians—not patients. MedClarify AI bridges that gap with clarity and compassion."
        />

        <div className="mt-16 grid gap-8 md:grid-cols-2">
          <ComparisonColumn
            title="Traditional Report"
            items={traditionalItems}
            variant="traditional"
          />
          <ComparisonColumn
            title="MedClarify AI"
            items={medclarifyItems}
            variant="medclarify"
          />
        </div>
      </div>
    </section>
  );
}

import { motion } from 'framer-motion';
import { type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  index?: number;
}

export function FeatureCard({ icon: Icon, title, description, index = 0 }: FeatureCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -4 }}
      className={cn(
        'group relative rounded-2xl border border-border bg-card p-6 shadow-soft transition-shadow hover:shadow-soft-lg',
      )}
    >
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-600 transition-colors group-hover:bg-teal-500 group-hover:text-white dark:text-teal-400">
        <Icon className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>
      <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
    </motion.article>
  );
}

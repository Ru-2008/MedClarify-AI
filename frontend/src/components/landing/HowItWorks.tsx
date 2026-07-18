import { motion } from 'framer-motion';
import { FileUp, Brain, Stethoscope, LayoutDashboard } from 'lucide-react';
import { SectionTitle } from './SectionTitle';

const steps = [
  {
    step: 1,
    icon: FileUp,
    title: 'Upload PDF',
    description: 'Securely upload your pathology or laboratory report in PDF format.',
    color: 'from-teal-500 to-teal-600',
  },
  {
    step: 2,
    icon: Brain,
    title: 'AI Extracts Data',
    description: 'Our AI reads test names, values, units, and reference ranges automatically.',
    color: 'from-sky-500 to-sky-600',
  },
  {
    step: 3,
    icon: Stethoscope,
    title: 'Medical Analysis',
    description: 'Results are analyzed and explained in clear, everyday language.',
    color: 'from-violet-500 to-violet-600',
  },
  {
    step: 4,
    icon: LayoutDashboard,
    title: 'Health Dashboard',
    description: 'View charts, health scores, and personalized insights in one place.',
    color: 'from-emerald-500 to-emerald-600',
  },
];

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="bg-muted/30 py-20 sm:py-28"
      aria-labelledby="how-it-works-heading"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="How It Works"
          title="From PDF to clarity in four simple steps"
          description="No medical background required. MedClarify AI handles the complexity so you can focus on understanding your health."
        />

        <div className="relative mt-16">
          <div
            className="absolute left-1/2 top-24 hidden h-[calc(100%-6rem)] w-px -translate-x-1/2 bg-gradient-to-b from-teal-500/50 via-sky-500/50 to-emerald-500/50 lg:block"
            aria-hidden="true"
          />

          <div className="grid gap-12 lg:grid-cols-4 lg:gap-8">
            {steps.map((item, index) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.12 }}
                  className="relative flex flex-col items-center text-center"
                >
                  {index < steps.length - 1 && (
                    <div
                      className="mb-4 text-2xl text-muted-foreground lg:hidden"
                      aria-hidden="true"
                    >
                      ↓
                    </div>
                  )}

                  <div
                    className={`mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${item.color} shadow-soft-lg`}
                  >
                    <Icon className="h-7 w-7 text-white" aria-hidden="true" />
                  </div>

                  <span className="mb-2 text-xs font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">
                    Step {item.step}
                  </span>
                  <h3 className="mb-2 text-lg font-semibold text-foreground">
                    {item.title}
                  </h3>
                  <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
                    {item.description}
                  </p>

                  {index < steps.length - 1 && (
                    <div
                      className="mt-6 hidden text-muted-foreground lg:block"
                      aria-hidden="true"
                    >
                      →
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

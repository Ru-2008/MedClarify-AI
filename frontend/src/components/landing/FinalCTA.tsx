import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export function FinalCTA() {
  return (
    <section className="py-20 sm:py-28" aria-labelledby="cta-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-brand px-8 py-16 text-center shadow-soft-lg sm:px-16 sm:py-20"
        >
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.15),transparent_50%)]" />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(255,255,255,0.1),transparent_50%)]" />

          <div className="relative">
            <h2
              id="cta-heading"
              className="font-display text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl"
            >
              Ready to understand your health better?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-white/85">
              Join thousands of patients who use MedClarify AI to decode their
              medical reports with confidence and clarity.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link to="/upload">
                <Button
                  size="lg"
                  variant="secondary"
                  className="w-full bg-white text-teal-700 hover:bg-white/90 sm:w-auto"
                >
                  <Upload className="h-5 w-5" aria-hidden="true" />
                  Upload Report
                </Button>
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

import { motion } from 'framer-motion';
import {
  Building2,
  FlaskConical,
  GraduationCap,
  HeartPulse,
  Stethoscope,
} from 'lucide-react';

const partners = [
  { name: 'Metro General Hospital', icon: HeartPulse },
  { name: 'CareFirst Clinic', icon: Stethoscope },
  { name: 'Precision Diagnostics', icon: Building2 },
  { name: 'LabCore Laboratories', icon: FlaskConical },
  { name: 'Health Sciences University', icon: GraduationCap },
];

export function TrustedBy() {
  return (
    <section className="border-y border-border bg-muted/30 py-12" aria-label="Trusted by healthcare organizations">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="mb-8 text-center text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Trusted by healthcare teams worldwide
        </p>
        <div className="grid grid-cols-2 items-center gap-8 sm:grid-cols-3 lg:grid-cols-5">
          {partners.map((partner, index) => {
            const Icon = partner.icon;
            return (
              <motion.div
                key={partner.name}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="flex flex-col items-center gap-2 grayscale opacity-60 transition-opacity hover:opacity-100"
              >
                <Icon className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
                <span className="text-center text-xs font-semibold text-muted-foreground">
                  {partner.name}
                </span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

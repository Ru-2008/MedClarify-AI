import { motion } from 'framer-motion';
import { Quote } from 'lucide-react';
import { SectionTitle } from './SectionTitle';

interface TestimonialCardProps {
  quote: string;
  name: string;
  role: string;
  index: number;
}

function TestimonialCard({ quote, name, role, index }: TestimonialCardProps) {
  return (
    <motion.blockquote
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
      className="flex h-full flex-col rounded-2xl border border-border bg-card p-6 shadow-soft"
    >
      <Quote
        className="mb-4 h-8 w-8 text-teal-500/40"
        aria-hidden="true"
      />
      <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
        &ldquo;{quote}&rdquo;
      </p>
      <footer className="mt-6 border-t border-border pt-4">
        <cite className="not-italic">
          <p className="font-semibold text-foreground">{name}</p>
          <p className="text-xs text-muted-foreground">{role}</p>
        </cite>
      </footer>
    </motion.blockquote>
  );
}

const testimonials = [
  {
    quote:
      'For the first time, I actually understood what my blood work meant. The visual dashboard made it easy to discuss results with my doctor.',
    name: 'Priya Sharma',
    role: 'Patient · Bangalore',
  },
  {
    quote:
      'We use MedClarify AI to help patients review lab results before appointments. It saves time and improves shared decision-making.',
    name: 'Dr. James Okonkwo',
    role: 'Primary Care Physician',
  },
  {
    quote:
      'Our diagnostic center partners love how patients arrive better informed. The platform turns complex reports into clear next steps.',
    name: 'Elena Rodriguez',
    role: 'Lab Operations Director',
  },
];

export function Testimonials() {
  return (
    <section className="py-20 sm:py-28" aria-labelledby="testimonials-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Testimonials"
          title="Trusted by patients and providers"
          description="Healthcare teams and individuals rely on MedClarify AI to make medical reports more accessible."
        />

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <TestimonialCard key={testimonial.name} {...testimonial} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}

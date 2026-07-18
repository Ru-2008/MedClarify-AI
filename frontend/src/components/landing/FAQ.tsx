import * as Accordion from '@radix-ui/react-accordion';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { SectionTitle } from './SectionTitle';
import { cn } from '@/lib/utils';

const faqs = [
  {
    question: 'What types of medical reports can I upload?',
    answer:
      'MedClarify AI supports pathology reports and laboratory reports in PDF format. This includes complete blood counts, metabolic panels, lipid profiles, thyroid tests, and most standard lab results.',
  },
  {
    question: 'Is my health data secure?',
    answer:
      'Yes. Your reports are encrypted in transit and at rest. We follow healthcare data protection best practices and never sell your personal health information to third parties.',
  },
  {
    question: 'How does the AI analysis work?',
    answer:
      'Our AI extracts test names, values, and reference ranges from your PDF, then generates plain-language explanations and visual summaries. It highlights values outside typical ranges for your review.',
  },
  {
    question: 'Is MedClarify AI a replacement for my doctor?',
    answer:
      'No. MedClarify AI is an educational tool designed to help you understand your reports. Always consult a qualified healthcare professional for diagnosis, treatment, and medical decisions.',
  },
  {
    question: 'Can I share my results with my physician?',
    answer:
      'Absolutely. You can download simplified summaries and visual reports to share with your care team during appointments or via secure messaging.',
  },
  {
    question: 'Do I need a referral to use the platform?',
    answer:
      'No referral is required. Anyone with a pathology or laboratory report can create a free account and upload their documents for AI-powered analysis.',
  },
];

export function FAQ() {
  return (
    <section className="bg-muted/30 py-20 sm:py-28" aria-labelledby="faq-heading">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="FAQ"
          title="Frequently asked questions"
          description="Everything you need to know about MedClarify AI and how it helps you understand your medical reports."
        />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12"
        >
          <Accordion.Root type="single" collapsible className="space-y-3">
            {faqs.map((faq, index) => (
              <Accordion.Item
                key={faq.question}
                value={`item-${index}`}
                className="overflow-hidden rounded-xl border border-border bg-card shadow-soft"
              >
                <Accordion.Header>
                  <Accordion.Trigger
                    className={cn(
                      'flex w-full items-center justify-between gap-4 px-5 py-4 text-left text-sm font-semibold text-foreground transition-colors hover:bg-muted/50',
                      'group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                    )}
                  >
                    {faq.question}
                    <ChevronDown
                      className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-data-[state=open]:rotate-180"
                      aria-hidden="true"
                    />
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
                  <div className="px-5 pb-4 text-sm leading-relaxed text-muted-foreground">
                    {faq.answer}
                  </div>
                </Accordion.Content>
              </Accordion.Item>
            ))}
          </Accordion.Root>
        </motion.div>
      </div>
    </section>
  );
}

import {
  AlertTriangle,
  BarChart3,
  Bot,
  Download,
  FileSearch,
  History,
} from 'lucide-react';
import { SectionTitle } from './SectionTitle';
import { FeatureCard } from './FeatureCard';

const features = [
  {
    icon: FileSearch,
    title: 'AI Report Analysis',
    description:
      'Upload pathology and lab PDFs. Our AI extracts test values, reference ranges, and flags results that may need attention.',
  },
  {
    icon: BarChart3,
    title: 'Medical Insights',
    description:
      'Receive clear summaries of your results with context about what each marker measures and why it matters for your health.',
  },
  {
    icon: History,
    title: 'Health Timeline',
    description:
      'Track changes across multiple reports over time. Spot trends in key biomarkers with an intuitive visual timeline.',
  },
  {
    icon: Bot,
    title: 'AI Chat',
    description:
      'Ask follow-up questions about your report in plain language. Get explanations tailored to your uploaded results.',
  },
  {
    icon: AlertTriangle,
    title: 'Abnormality Detection',
    description:
      'Automatically highlight values outside reference ranges so you can focus on what your care team may want to review.',
  },
  {
    icon: Download,
    title: 'Download Reports',
    description:
      'Export simplified summaries and visual reports to share with your physician or keep for your personal health records.',
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 sm:py-28" aria-labelledby="features-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Features"
          title="Everything you need to understand your reports"
          description="MedClarify AI turns complex medical documents into actionable insights you can actually understand."
        />

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} {...feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}

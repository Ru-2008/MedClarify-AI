import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Upload } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { HeroIllustration } from './HeroIllustration';

export function Hero() {
  return (
    <section
      id="home"
      className="relative overflow-hidden pt-28 pb-20 sm:pt-32 sm:pb-28 lg:pt-40 lg:pb-32"
      aria-labelledby="hero-heading"
    >
      <div className="pointer-events-none absolute inset-0 bg-grid-pattern bg-grid opacity-40" />
      <div className="pointer-events-none absolute -top-40 right-0 h-[500px] w-[500px] rounded-full bg-teal-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-20 -left-20 h-[400px] w-[400px] rounded-full bg-sky-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-500/20 bg-teal-500/5 px-4 py-1.5 text-sm font-medium text-teal-700 dark:text-teal-300">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-teal-500" />
              </span>
              AI-powered medical report understanding
            </div>

            <h1
              id="hero-heading"
              className="font-display text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl lg:leading-[1.1]"
            >
              Understand Your Medical Reports with{' '}
              <span className="text-gradient">AI</span>
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground sm:text-xl">
              Upload your pathology report and receive AI-powered explanations,
              health insights, and beautiful visualizations within seconds.
            </p>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link to="/upload">
                <Button size="lg" className="w-full sm:w-auto">
                  <Upload className="h-5 w-5" aria-hidden="true" />
                  Upload Report
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                  Learn More
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Button>
              </a>
            </div>

            <p className="mt-8 text-sm text-muted-foreground">
              Supports PDF pathology and laboratory reports. Your data stays private
              and encrypted.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <HeroIllustration />
          </motion.div>
        </div>
      </div>
    </section>
  );
}

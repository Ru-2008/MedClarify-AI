import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export function Logo({ className, showText = true }: LogoProps) {
  return (
    <Link
      to="/"
      className={cn('flex items-center gap-2.5 group', className)}
      aria-label="MedClarify AI home"
    >
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-brand shadow-soft transition-transform group-hover:scale-105">
        <Activity className="h-5 w-5 text-white" aria-hidden="true" />
      </div>
      {showText && (
        <span className="font-display text-lg font-bold tracking-tight text-foreground">
          MedClarify<span className="text-teal-600 dark:text-teal-400"> AI</span>
        </span>
      )}
    </Link>
  );
}

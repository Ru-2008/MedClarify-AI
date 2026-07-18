import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings2,
  ChevronDown,
  ChevronUp,
  Clock,
  FileText,
  Cpu,
  Eye,
  Hash,
} from 'lucide-react';
import type { ProcessingMetadata } from '@/types/report.types';

interface MetadataCardProps {
  metadata: ProcessingMetadata;
  pages: number;
  characterCount: number;
  filename: string;
}

export function MetadataCard({ metadata, pages, characterCount, filename }: MetadataCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="rounded-2xl border border-border/50 bg-muted/20 overflow-hidden"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between px-5 py-3.5 text-left"
      >
        <div className="flex items-center gap-2.5">
          <Settings2 className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium text-muted-foreground">Processing Details</span>
        </div>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="grid grid-cols-2 gap-3 px-5 pb-5 sm:grid-cols-3">
              <MetaItem icon={Cpu} label="Extraction Method" value={metadata.extraction_method} />
              <MetaItem icon={Clock} label="Processing Time" value={`${(metadata.processing_time_ms / 1000).toFixed(2)}s`} />
              <MetaItem icon={FileText} label="Pages" value={String(pages)} />
              <MetaItem icon={Hash} label="Characters" value={characterCount.toLocaleString()} />
              <MetaItem icon={FileText} label="Filename" value={filename} />
              {metadata.ocr_pages.length > 0 && (
                <MetaItem
                  icon={Eye}
                  label="OCR Pages"
                  value={metadata.ocr_pages.join(', ')}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function MetaItem({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="rounded-xl bg-background/50 p-3">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="h-3 w-3 text-muted-foreground" />
        <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground">{label}</p>
      </div>
      <p className="text-sm font-medium text-foreground truncate" title={value}>{value}</p>
    </div>
  );
}

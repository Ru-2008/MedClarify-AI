import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Upload } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useReportStore } from '@/stores/reportStore';

// Import our new premium components
import { HealthMetrics } from '@/components/report/HealthMetrics';
import { SummaryCard } from '@/components/report/SummaryCard';
import { PatientCard } from '@/components/report/PatientCard';
import { AbnormalFindings } from '@/components/report/AbnormalFindings';
import { ChartsSection } from '@/components/report/ChartsSection';
import { LabTable } from '@/components/report/LabTable';
import { MetadataCard } from '@/components/report/MetadataCard';
import { ExportActions } from '@/components/report/ExportActions';

const ViewerPage = () => {
  const navigate = useNavigate();
  const { report } = useReportStore();

  // Redirect to upload if no report is loaded
  useEffect(() => {
    if (!report) {
      navigate('/upload', { replace: true });
    }
  }, [report, navigate]);

  if (!report) return null;

  const { parsed_data } = report;
  const patient = parsed_data.patient;
  const tests = parsed_data.laboratory_tests || [];
  const abnormalTests = parsed_data.abnormal_tests || [];
  const interpretations = parsed_data.interpretation || [];
  const summary = parsed_data.summary;
  const confidence = parsed_data.confidence;
  const warnings = parsed_data.warnings || [];
  const metadata = parsed_data.processing_metadata;

  const normalCount = tests.filter((t) => t.status.toUpperCase() === 'NORMAL').length;
  const abnormalCount = tests.length - normalCount;

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Decorative background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 right-0 h-[500px] w-[500px] rounded-full bg-teal-500/8 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 h-[400px] w-[400px] rounded-full bg-sky-500/8 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        
        {/* Top Navigation & Actions */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/upload')}
              className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Upload Another
            </button>
            <span className="text-border">|</span>
            <Link
              to="/"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Home
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <ExportActions report={report} />
            <Link to="/upload">
              <Button variant="default" size="sm">
                <Upload className="h-3.5 w-3.5" />
                New Upload
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-4"
        >
          <div>
            <h1 className="font-display text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Report Dashboard
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Analyzed {report.filename} on {new Date().toLocaleDateString()}
            </p>
          </div>
        </motion.div>

        {/* 1. Health Metrics Strip */}
        <HealthMetrics
          totalTests={tests.length}
          normalCount={normalCount}
          abnormalCount={abnormalCount}
          confidence={confidence}
          pages={report.pages}
          processingTimeMs={metadata?.processing_time_ms}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Content Column (Left - 8 columns) */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* 2. Overall Health Summary */}
            {summary && (
              <SummaryCard
                summary={summary}
                abnormalCount={abnormalCount}
                totalTests={tests.length}
                warnings={warnings}
              />
            )}

            {/* 3. Abnormal Findings */}
            <AbnormalFindings
              abnormalTests={abnormalTests}
              interpretations={interpretations}
            />

            {/* 4. Laboratory Tests Table */}
            <LabTable tests={tests} />

          </div>

          {/* Sidebar Column (Right - 4 columns) */}
          <div className="lg:col-span-4 space-y-8">
            
            {/* 5. Patient Information */}
            <PatientCard patient={patient} />

            {/* 6. Charts & Visualizations */}
            <ChartsSection tests={tests} />

            {/* 7. Processing Details */}
            {metadata && (
              <MetadataCard
                metadata={metadata}
                pages={report.pages}
                characterCount={report.character_count}
                filename={report.filename}
              />
            )}

            {/* Medical Disclaimer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="rounded-xl border border-border/50 bg-muted/20 p-4 text-center"
            >
              <p className="text-xs leading-relaxed text-muted-foreground">
                <strong className="text-foreground font-semibold">Disclaimer:</strong> This dashboard is generated
                by AI for informational purposes only. It is not a substitute for professional medical
                advice, diagnosis, or treatment. Always consult your healthcare provider.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewerPage;
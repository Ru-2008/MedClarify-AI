import { useCallback } from 'react';
import { motion } from 'framer-motion';
import { Download, Printer } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { UploadResponse } from '@/types/report.types';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface ExportActionsProps {
  report: UploadResponse;
}

export function ExportActions({ report }: ExportActionsProps) {
  const handleDownloadPDF = useCallback(() => {
    const doc = new jsPDF();
    const { parsed_data } = report;
    const { patient, laboratory_tests = [], abnormal_tests = [], interpretation = [], summary, confidence, processing_metadata, warnings = [] } = parsed_data;
    
    // Config
    const startY = 20;
    const margin = 14;
    let currentY = startY;

    // Helper: Add Title
    const addSectionTitle = (title: string, yOffset = 10) => {
      currentY += yOffset;
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text(title, margin, currentY);
      currentY += 6;
    };

    // Header
    doc.setFontSize(22);
    doc.setFont('helvetica', 'bold');
    doc.text('MedClarify AI Report', margin, currentY);
    
    currentY += 8;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100);
    doc.text(`Filename: ${report.filename} | Processed: ${new Date().toLocaleString()}`, margin, currentY);
    doc.setTextColor(0);

    // Patient Info
    if (patient) {
      addSectionTitle('Patient Information', 15);
      const patientData = [
        ['Name', patient.name || 'N/A', 'Age/Gender', `${patient.age || 'N/A'} / ${patient.gender || 'N/A'}`],
        ['Patient ID', patient.patient_id || 'N/A', 'Report Date', patient.report_date || 'N/A'],
        ['Doctor', patient.doctor_name || patient.doctor || 'N/A', 'Laboratory', patient.laboratory || patient.lab_name || 'N/A'],
      ];
      autoTable(doc, {
        startY: currentY,
        body: patientData,
        theme: 'grid',
        styles: { fontSize: 9, cellPadding: 3 },
        columnStyles: { 0: { fontStyle: 'bold', fillColor: [245, 245, 245] }, 2: { fontStyle: 'bold', fillColor: [245, 245, 245] } },
      });
      currentY = (doc as any).lastAutoTable.finalY;
    }

    // Summary
    if (summary) {
      addSectionTitle('Health Summary');
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      const lines = doc.splitTextToSize(summary, 190 - margin * 2);
      doc.text(lines, margin, currentY);
      currentY += (lines.length * 5);
    }

    // Warnings
    if (warnings.length > 0) {
      addSectionTitle('Extraction Warnings');
      doc.setFontSize(9);
      doc.setTextColor(200, 50, 50); // Red
      warnings.forEach((w) => {
        const lines = doc.splitTextToSize(`• ${w}`, 190 - margin * 2);
        doc.text(lines, margin, currentY);
        currentY += (lines.length * 5);
      });
      doc.setTextColor(0);
    }

    // Abnormal Tests
    if (abnormal_tests.length > 0) {
      addSectionTitle('Abnormal Findings');
      const abnormalData = abnormal_tests.map(t => {
        const interp = interpretation.find(i => i.test_name === t.test_name);
        let details = '';
        if (interp && interp.explanation) details += `Explanation: ${interp.explanation}\n`;
        if (interp && interp.recommendations && interp.recommendations.length > 0) details += `Recommendations: ${interp.recommendations.join(', ')}`;
        
        return [
          t.test_name,
          `${t.value ?? '—'} ${t.unit || ''}`,
          (() => {
            const r = t.reference_range;
            if (!r) return '—';
            const low = r.low ?? r.min;
            const high = r.high ?? r.max;
            if (low != null && high != null) return `${low} – ${high}`;
            if (low != null) return `≥ ${low}`;
            if (high != null) return `≤ ${high}`;
            return '—';
          })(),
          t.status,
          details
        ];
      });

      autoTable(doc, {
        startY: currentY,
        head: [['Test', 'Value', 'Reference', 'Status', 'AI Interpretation']],
        body: abnormalData,
        theme: 'striped',
        headStyles: { fillColor: [225, 29, 72] }, // Rose color
        styles: { fontSize: 8, cellPadding: 4 },
        columnStyles: { 4: { cellWidth: 70 } }
      });
      currentY = (doc as any).lastAutoTable.finalY;
    }

    // All Tests
    if (laboratory_tests.length > 0) {
      addSectionTitle('All Laboratory Tests');
      const allTestsData = laboratory_tests.map(t => [
        t.test_name,
        `${t.value ?? '—'} ${t.unit || ''}`,
        (() => {
          const r = t.reference_range;
          if (!r) return '—';
          const low = r.low ?? r.min;
          const high = r.high ?? r.max;
          if (low != null && high != null) return `${low} – ${high}`;
          if (low != null) return `≥ ${low}`;
          if (high != null) return `≤ ${high}`;
          return '—';
        })(),
        t.status
      ]);

      autoTable(doc, {
        startY: currentY,
        head: [['Test Name', 'Value', 'Reference Range', 'Status']],
        body: allTestsData,
        theme: 'striped',
        headStyles: { fillColor: [13, 148, 136] }, // Teal color
        styles: { fontSize: 9, cellPadding: 3 },
      });
      currentY = (doc as any).lastAutoTable.finalY;
    }

    // Metadata Footer
    addSectionTitle('Processing Details');
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100);
    const metaText = `Overall Confidence: ${confidence ?? 'N/A'}% | Processing Time: ${((processing_metadata?.processing_time_ms ?? 0) / 1000).toFixed(2)}s | Engine: ${processing_metadata?.extraction_method ?? 'Unknown'}`;
    doc.text(metaText, margin, currentY);

    // Save
    doc.save(`medclarify-report-${report.filename.replace(/\.[^/.]+$/, '')}.pdf`);
  }, [report]);

  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.45 }}
      className="flex flex-wrap gap-3"
    >
      <Button variant="secondary" size="sm" onClick={handleDownloadPDF}>
        <Download className="mr-2 h-3.5 w-3.5" />
        Download PDF
      </Button>
      <Button variant="ghost" size="sm" onClick={handlePrint}>
        <Printer className="mr-2 h-3.5 w-3.5" />
        Print Report
      </Button>
    </motion.div>
  );
}

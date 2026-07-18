import { motion } from 'framer-motion';
import {
  User,
  Calendar,
  Building2,
  Stethoscope,
  FlaskConical,
  Hash,
  Info,
} from 'lucide-react';
import type { PatientInfo } from '@/types/report.types';

interface PatientCardProps {
  patient: PatientInfo;
}

interface FieldDef {
  label: string;
  value: string | null | undefined;
  icon: React.ElementType;
}

function FieldItem({ label, value, icon: Icon }: FieldDef) {
  if (!value) return null;
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="rounded-lg bg-teal-500/10 p-1.5">
        <Icon className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</p>
        <p className="text-sm font-medium text-foreground truncate">{value}</p>
      </div>
    </div>
  );
}

function FieldGroup({ title, fields }: { title: string; fields: FieldDef[] }) {
  const visibleFields = fields.filter((f) => f.value);
  if (visibleFields.length === 0) return null;

  return (
    <div>
      <p className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground/70 mb-1">{title}</p>
      <div className="divide-y divide-border/40">
        {visibleFields.map((f) => (
          <FieldItem key={f.label} {...f} />
        ))}
      </div>
    </div>
  );
}

export function PatientCard({ patient }: PatientCardProps) {
  const identityFields: FieldDef[] = [
    { label: 'Name', value: patient.name, icon: User },
    { label: 'Age', value: patient.age, icon: User },
    { label: 'Gender', value: patient.gender, icon: User },
    { label: 'Patient ID', value: patient.patient_id, icon: Hash },
    { label: 'UHID', value: patient.uhid, icon: Hash },
  ];

  const medicalFields: FieldDef[] = [
    { label: 'Doctor', value: patient.doctor_name || patient.doctor, icon: Stethoscope },
    { label: 'Laboratory', value: patient.laboratory || patient.lab_name, icon: Building2 },
    { label: 'Hospital', value: patient.hospital, icon: Building2 },
    { label: 'Sample Type', value: patient.sample_type, icon: FlaskConical },
    { label: 'Lab ID', value: patient.lab_id || patient.registration_number, icon: Hash },
  ];

  const dateFields: FieldDef[] = [
    { label: 'Report Date', value: patient.report_date, icon: Calendar },
    { label: 'Collection Date', value: patient.collection_date, icon: Calendar },
    { label: 'Approval Date', value: patient.approval_date, icon: Calendar },
  ];

  const allEmpty = [...identityFields, ...medicalFields, ...dateFields].every((f) => !f.value);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      className="glass rounded-2xl p-6 shadow-soft"
    >
      <div className="flex items-center gap-3 mb-5">
        <div className="rounded-xl bg-gradient-to-br from-teal-500/20 to-sky-500/20 p-2.5">
          <User className="h-5 w-5 text-teal-600 dark:text-teal-400" />
        </div>
        <h2 className="font-display text-lg font-bold text-foreground">Patient Information</h2>
      </div>

      {allEmpty ? (
        <div className="flex items-center gap-3 rounded-xl bg-muted/50 p-4">
          <Info className="h-5 w-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Patient information could not be extracted from this report.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <FieldGroup title="Identity" fields={identityFields} />
          <FieldGroup title="Medical" fields={medicalFields} />
          <FieldGroup title="Dates" fields={dateFields} />
        </div>
      )}
    </motion.div>
  );
}

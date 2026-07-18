import { getStatusConfig } from './helpers';

export function StatusBadge({ status }: { status: string }) {
  const config = getStatusConfig(status);
  const Icon = config.icon;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${config.bg} ${config.border} ${config.color}`}
    >
      <Icon className="h-3 w-3" />
      {config.label}
    </span>
  );
}

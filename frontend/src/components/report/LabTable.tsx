import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  FlaskConical,
  Search,
  ChevronUp,
  ChevronDown,
  AlertTriangle,
  ArrowUpDown,
} from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { getStatusConfig, formatRefRange } from './helpers';
import type { LabTest } from '@/types/report.types';

interface LabTableProps {
  tests: LabTest[];
}

type SortKey = 'test_name' | 'value' | 'status';
type SortDir = 'asc' | 'desc';
type FilterStatus = 'ALL' | 'NORMAL' | 'LOW' | 'HIGH' | 'BORDERLINE' | 'CRITICAL';

const FILTER_OPTIONS: { label: string; value: FilterStatus }[] = [
  { label: 'All', value: 'ALL' },
  { label: 'Normal', value: 'NORMAL' },
  { label: 'Low', value: 'LOW' },
  { label: 'High', value: 'HIGH' },
  { label: 'Critical', value: 'CRITICAL' },
];

const PAGE_SIZE = 20;

export function LabTable({ tests }: LabTableProps) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<FilterStatus>('ALL');
  const [sortKey, setSortKey] = useState<SortKey>('test_name');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [page, setPage] = useState(0);

  // Filter + search
  const filtered = useMemo(() => {
    let result = [...tests];

    // Status filter
    if (filter !== 'ALL') {
      result = result.filter((t) => t.status.toUpperCase() === filter);
    }

    // Text search
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (t) =>
          t.test_name.toLowerCase().includes(q) ||
          (t.unit && t.unit.toLowerCase().includes(q)) ||
          t.status.toLowerCase().includes(q),
      );
    }

    // Sort
    result.sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'test_name') cmp = a.test_name.localeCompare(b.test_name);
      else if (sortKey === 'value') cmp = (a.value ?? 0) - (b.value ?? 0);
      else if (sortKey === 'status') cmp = a.status.localeCompare(b.status);
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [tests, filter, search, sortKey, sortDir]);

  // Pagination
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    else {
      setSortKey(key);
      setSortDir('asc');
    }
    setPage(0);
  };

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return <ArrowUpDown className="h-3 w-3 text-muted-foreground/40" />;
    return sortDir === 'asc'
      ? <ChevronUp className="h-3 w-3 text-teal-500" />
      : <ChevronDown className="h-3 w-3 text-teal-500" />;
  };

  // Count per status for filter badges
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { ALL: tests.length };
    tests.forEach((t) => {
      const s = t.status.toUpperCase();
      counts[s] = (counts[s] || 0) + 1;
    });
    return counts;
  }, [tests]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass rounded-2xl p-6 shadow-soft"
    >
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-teal-500/10 p-2.5">
            <FlaskConical className="h-5 w-5 text-teal-600 dark:text-teal-400" />
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-foreground">Laboratory Tests</h2>
            <p className="text-xs text-muted-foreground">{tests.length} tests extracted</p>
          </div>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            placeholder="Search tests..."
            className="w-full rounded-xl border border-border bg-background/50 py-2 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-teal-500/30 focus:border-teal-500/50 transition-all"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-5">
        {FILTER_OPTIONS.map((opt) => {
          const count = statusCounts[opt.value] || 0;
          const isActive = filter === opt.value;
          return (
            <button
              key={opt.value}
              onClick={() => { setFilter(opt.value); setPage(0); }}
              className={`
                inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all
                ${isActive
                  ? 'bg-teal-500/15 text-teal-700 dark:text-teal-300 border border-teal-500/30'
                  : 'bg-muted/50 text-muted-foreground border border-transparent hover:bg-muted hover:text-foreground'
                }
              `}
            >
              {opt.label}
              <span className={`rounded-full px-1.5 py-0.5 text-[10px] ${isActive ? 'bg-teal-500/20' : 'bg-muted'}`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Table */}
      {tests.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <FlaskConical className="h-12 w-12 text-muted-foreground/30" />
          <p className="mt-4 text-sm text-muted-foreground">No laboratory tests were extracted.</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Search className="h-10 w-10 text-muted-foreground/30" />
          <p className="mt-3 text-sm text-muted-foreground">No tests match your search.</p>
          <button
            onClick={() => { setSearch(''); setFilter('ALL'); }}
            className="mt-2 text-sm font-medium text-teal-600 dark:text-teal-400 hover:underline"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto -mx-6 px-6">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th
                  className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground cursor-pointer select-none"
                  onClick={() => toggleSort('test_name')}
                >
                  <span className="inline-flex items-center gap-1">
                    Test <SortIcon col="test_name" />
                  </span>
                </th>
                <th
                  className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground cursor-pointer select-none"
                  onClick={() => toggleSort('value')}
                >
                  <span className="inline-flex items-center gap-1">
                    Value <SortIcon col="value" />
                  </span>
                </th>
                <th className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Unit</th>
                <th className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Ref Range</th>
                <th
                  className="pb-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground cursor-pointer select-none"
                  onClick={() => toggleSort('status')}
                >
                  <span className="inline-flex items-center gap-1">
                    Status <SortIcon col="status" />
                  </span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {paged.map((test, i) => {
                const sc = getStatusConfig(test.status);
                const lowConf = test.confidence < 0.8;
                return (
                  <tr
                    key={`${test.test_name}-${i}`}
                    className="group hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-2">
                        <span className={`h-1.5 w-1.5 rounded-full shrink-0 ${sc.dot}`} />
                        <span className="text-sm font-medium text-foreground">{test.test_name}</span>
                        {lowConf && (
                          <AlertTriangle className="h-3 w-3 text-amber-500" title="Low extraction confidence" />
                        )}
                      </div>
                    </td>
                    <td className={`py-3 pr-4 text-sm font-semibold tabular-nums ${sc.color}`}>
                      {test.value != null ? test.value : '—'}
                    </td>
                    <td className="py-3 pr-4 text-sm text-muted-foreground">{test.unit || '—'}</td>
                    <td className="py-3 pr-4 text-sm text-muted-foreground tabular-nums">{formatRefRange(test)}</td>
                    <td className="py-3">
                      <StatusBadge status={test.status} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filtered.length)} of {filtered.length}
          </p>
          <div className="flex items-center gap-1">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`
                  h-8 min-w-[2rem] rounded-lg px-2 text-xs font-medium transition-all
                  ${page === i
                    ? 'bg-teal-500/15 text-teal-700 dark:text-teal-300'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }
                `}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

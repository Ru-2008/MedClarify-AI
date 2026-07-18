import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Upload, FileDown } from 'lucide-react';
import { Logo } from './Logo';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { useReportStore } from '@/stores/reportStore';

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const report = useReportStore((state) => state.report);
  const resetReport = useReportStore((state) => state.reset);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  const handleNavClick = () => setMobileOpen(false);

  const handleNewUpload = () => {
    resetReport();
    handleNavClick();
    navigate('/upload');
  };

  const handleDownloadPDF = () => {
    // This will be handled by a global event or store later if needed, 
    // but typically users will download from the Viewer page.
    // If they click it here, just go to report
    if (report) {
      handleNavClick();
      navigate('/report');
    }
  };

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-50 transition-all duration-300',
        isScrolled ? 'glass shadow-soft py-3' : 'bg-transparent py-5',
      )}
      role="banner"
    >
      <nav
        className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8"
        aria-label="Main navigation"
      >
        <Logo />

        <div className="hidden items-center gap-3 md:flex">
          {report && (
            <Button variant="ghost" size="sm" onClick={() => navigate('/report')}>
              View Report
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={handleNewUpload}>
            <Upload className="mr-2 h-3.5 w-3.5" />
            New Upload
          </Button>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-lg p-2 text-foreground md:hidden"
          onClick={() => setMobileOpen((open) => !open)}
          aria-expanded={mobileOpen}
          aria-controls="mobile-menu"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            id="mobile-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="glass border-t border-border md:hidden"
          >
            <div className="mx-auto max-w-7xl space-y-1 px-4 py-4 sm:px-6">
              <Link
                to="/"
                onClick={handleNavClick}
                className="block rounded-lg px-3 py-2.5 text-base font-medium text-foreground hover:bg-muted"
              >
                Home
              </Link>
              {report && (
                <Link
                  to="/report"
                  onClick={handleNavClick}
                  className="block rounded-lg px-3 py-2.5 text-base font-medium text-foreground hover:bg-muted"
                >
                  View Report
                </Link>
              )}
              <div className="flex flex-col gap-2 pt-4">
                <Button variant="outline" className="w-full" onClick={handleNewUpload}>
                  <Upload className="mr-2 h-4 w-4" />
                  New Upload
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

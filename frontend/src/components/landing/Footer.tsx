import { Logo } from './Logo';

export function Footer() {
  return (
    <footer
      id="contact"
      className="border-t border-border bg-card py-16"
      role="contentinfo"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          <div className="max-w-sm">
            <Logo />
            <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
              Understand Your Medical Reports with AI. MedClarify AI helps patients
              and providers turn complex pathology and lab results into clear,
              actionable insights.
            </p>
          </div>

          <div className="flex gap-12">
            <div>
              <h3 className="mb-4 text-sm font-semibold text-foreground">Legal</h3>
              <ul className="space-y-3" role="list">
                <li>
                  <a href="#privacy" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#terms" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    Terms of Service
                  </a>
                </li>
                <li>
                  <a href="#hipaa" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    HIPAA Compliance
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 text-sm font-semibold text-foreground">Contact</h3>
              <ul className="space-y-3" role="list">
                <li>
                  <a href="mailto:support@medclarifyai.com" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    support@medclarifyai.com
                  </a>
                </li>
                <li>
                  <a href="#contact" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    Contact Us
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border pt-8 sm:flex-row">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} MedClarify AI. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground">
            <strong className="font-semibold text-foreground">Medical Disclaimer:</strong> MedClarify AI does not provide medical advice. 
            Consult your healthcare provider for medical decisions.
          </p>
        </div>
      </div>
    </footer>
  );
}

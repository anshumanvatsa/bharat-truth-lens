import { Shield } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => (
  <footer className="border-t border-border/50 bg-navy-deep">
    <div className="container mx-auto px-4 py-12">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        <div className="md:col-span-2">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-display font-bold text-lg">Bharat Truth Lens</span>
          </div>
          <p className="text-muted-foreground text-sm max-w-md">
            AI-powered civic intelligence platform delivering truth verification, public opinion analysis, and political transparency.
          </p>
        </div>
        <div>
          <h4 className="font-display font-semibold text-sm mb-3 text-foreground">Platform</h4>
          <div className="space-y-2">
            {["Analyzer", "Public Pulse", "Election Pulse", "Trending", "Leaders"].map((l) => (
              <Link key={l} to={`/${l.toLowerCase().replace(" ", "-")}`} className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                {l}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-display font-semibold text-sm mb-3 text-foreground">Legal</h4>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>Privacy Policy</p>
            <p>Terms of Service</p>
            <p>Civic Disclaimer</p>
          </div>
        </div>
      </div>
      <div className="border-t border-border/50 pt-6">
        <p className="text-xs text-muted-foreground text-center leading-relaxed">
          ⚠ This platform provides AI-generated analysis and simulated civic opinion insights. It does not represent official election results, government positions, or verified judicial outcomes. All data is for informational and civic engagement purposes only.
        </p>
        <p className="text-xs text-muted-foreground text-center mt-2">
          © 2026 Bharat Truth Lens. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
);

export default Footer;

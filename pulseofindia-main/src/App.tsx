import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Index from "./pages/Index";
import AnalyzerPage from "./pages/AnalyzerPage";
import PublicPulsePage from "./pages/PublicPulsePage";
import ElectionPulsePage from "./pages/ElectionPulsePage";
import TrendingPage from "./pages/TrendingPage";
import LeadersPage from "./pages/LeadersPage";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/analyzer" element={<AnalyzerPage />} />
            <Route path="/public-pulse" element={<PublicPulsePage />} />
            <Route path="/election-pulse" element={<ElectionPulsePage />} />
            <Route path="/trending" element={<TrendingPage />} />
            <Route path="/leaders" element={<LeadersPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

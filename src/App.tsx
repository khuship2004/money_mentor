import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { GoalsProvider } from "./contexts/GoalsContext";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import InvestmentPlanner from "./pages/InvestmentPlanner";
import Portfolio from "./pages/Portfolio";
import NotFound from "./pages/NotFound";
import GoalDetails from "./pages/GoalDetails";
import Navigation from "./components/Navigation";

const AppContent = () => {
  const location = useLocation();
  const showNav = !["/", "/auth"].includes(location.pathname);

  return (
    <>
      {showNav && <Navigation />}
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/planner" element={<InvestmentPlanner />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/goals/:id" element={<GoalDetails />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
};

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <GoalsProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </GoalsProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

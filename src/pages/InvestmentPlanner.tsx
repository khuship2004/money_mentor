import { useMemo, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Calculator, TrendingUp, PiggyBank, Shield, Zap, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { useGoals } from "@/contexts/GoalsContext";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { useLocation, useNavigate } from "react-router-dom";
import jsPDF from "jspdf";

const InvestmentPlanner = () => {
  const { toast } = useToast();
  const { addGoal } = useGoals();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [goalType, setGoalType] = useState("");
  const [customGoalName, setCustomGoalName] = useState("");
  const [goalAmount, setGoalAmount] = useState("");
  const [targetYear, setTargetYear] = useState("");
  const [targetMonth, setTargetMonth] = useState<string>("");
  const [riskAppetite, setRiskAppetite] = useState("");
  const [investmentType, setInvestmentType] = useState("sip");
  const [sipStartDate, setSipStartDate] = useState("");
  const [lumpsumAvailable, setLumpsumAvailable] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  interface PortfolioRecommendation {
    portfolio: Record<string, number>;
    expected_return: number;
    portfolio_risk: number;
    monthly_sip?: number;
    lumpsum_amount?: number;
    total_invested?: number;
    expected_wealth?: number;
    message?: string;
    optimization_status?: string;
    asset_allocation?: Record<string, number>;
  }

  const [portfolioRecommendation, setPortfolioRecommendation] = useState<PortfolioRecommendation | null>(null);
  const [showExcessDialog, setShowExcessDialog] = useState(false);
  const [pendingGoalData, setPendingGoalData] = useState<any>(null);
  const [calculatedGoalData, setCalculatedGoalData] = useState<any>(null);
  const [isGoalSaved, setIsGoalSaved] = useState(false);

  const currentYear = new Date().getFullYear();
  const minYear = Math.max(2026, currentYear);
  const monthOptions = useMemo(
    () => [
      { value: "1", label: "Jan" },
      { value: "2", label: "Feb" },
      { value: "3", label: "Mar" },
      { value: "4", label: "Apr" },
      { value: "5", label: "May" },
      { value: "6", label: "Jun" },
      { value: "7", label: "Jul" },
      { value: "8", label: "Aug" },
      { value: "9", label: "Sep" },
      { value: "10", label: "Oct" },
      { value: "11", label: "Nov" },
      { value: "12", label: "Dec" },
    ],
    []
  );

  const API_BASE_URL = "http://localhost:8000";

const formatYears = (years?: number) => {
  if (!years) return "0";
  const rounded = Math.round(years * 2) / 2;
  return rounded % 1 === 0 ? rounded.toString() : rounded.toFixed(1);
};

  // Asset-specific inflation rates (fetched from backend models)
  const [inflationRates, setInflationRates] = useState<Record<string, number>>({
    car: 0.055, // Default 5.5%
    house: 0.0726, // Default 7.26%
    education: 0.115, // Default 11.5%
    gold: 0.1403, // Default 14.03%
    custom: 0.06, // Default 6%
  });
  const [inflationRatesDisplay, setInflationRatesDisplay] = useState<Record<string, { rate: number; description: string; period: string }>>({});

  // Fetch inflation rates from backend on component mount
  useEffect(() => {
    const fetchInflationRates = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/inflation-rates-simple`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === "success") {
            setInflationRates(data.rates);
            setInflationRatesDisplay(data.display);
          }
        }
      } catch {
        // Using default inflation rates when backend is unavailable
      }
    };
    fetchInflationRates();
  }, []);

  const getMonthsToTarget = () => {
    if (!targetYear) return 0;
    const monthValue = targetMonth ? parseInt(targetMonth) : 12;
    const now = new Date();
    const targetDate = new Date(parseInt(targetYear), monthValue - 1, 1);
    const months = (targetDate.getFullYear() - now.getFullYear()) * 12 + (targetDate.getMonth() - now.getMonth());
    return Math.max(months, 0);
  };

  const calculateInflatedValue = () => {
    const currentAmount = parseFloat(goalAmount);
    const months = getMonthsToTarget();
    const years = months / 12;
    const inflationRate = inflationRates[goalType] || 0.06;
    const futureValue = currentAmount * Math.pow(1 + inflationRate, years);
    
    return { futureValue, inflationRate, years, months };
  };

  const handleCalculate = async () => {
    if (!goalAmount || !targetYear || !goalType || !riskAppetite || !targetMonth) {
      toast({
        title: "Missing Information",
        description: "Please fill all required fields",
        variant: "destructive"
      });
      return;
    }

    if (goalType === "custom" && !customGoalName.trim()) {
      toast({
        title: "Missing Goal Name",
        description: "Please name your custom goal",
        variant: "destructive"
      });
      return;
    }

    const targetYearNum = parseInt(targetYear);
    if (targetYearNum < minYear) {
      toast({
        title: "Invalid Year",
        description: `Target year must be ${minYear} or later`,
        variant: "destructive"
      });
      return;
    }

    const now = new Date();
    const targetMonthNum = parseInt(targetMonth);
    if (targetYearNum === now.getFullYear() && targetMonthNum <= now.getMonth() + 1) {
      toast({
        title: "Invalid Target Month",
        description: "Target month must be in the future",
        variant: "destructive"
      });
      return;
    }

    setIsCalculating(true);
    
    try {
      const { futureValue, years, months, inflationRate } = calculateInflatedValue();
      
      // Determine time horizon based on years
      let timeHorizon = "medium";
      if (years <= 3) timeHorizon = "short";
      else if (years > 7) timeHorizon = "long";

      // Call backend API — years must be ≥ 1 for the backend validator
      const apiYears = Math.max(1, Math.ceil(years));

      const response = await fetch(`${API_BASE_URL}/api/recommend-portfolio`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          inflated_goal: futureValue,
          years: apiYears,
          risk_profile: riskAppetite,
          time_horizon: timeHorizon,
          investment_type: investmentType,
          goal_type: goalType,
          current_price: parseFloat(goalAmount)
        })
      });

      if (!response.ok) {
        throw new Error("Failed to get recommendation");
      }

      const data: PortfolioRecommendation = await response.json();
      setPortfolioRecommendation(data);
      setShowResults(true);

      const newGoalId = `goal-${Date.now()}`;
      const calculatedMonthlySip = data.monthly_sip || (months ? futureValue / months : 0);
      const calculatedLumpsum = data.lumpsum_amount || futureValue;
      const goalName = goalType === "custom" ? customGoalName.trim() : goalType;

      // Use data.portfolio which is what the backend returns
      const allocation = data.portfolio || data.asset_allocation || {};

      const baseGoal = {
        id: newGoalId,
        goalType,
        goalName,
        goalAmount: parseFloat(goalAmount),
        targetYear: targetYearNum,
        targetMonth: targetMonthNum,
        riskProfile: riskAppetite,
        investmentType,
        inflationRate,
        inflatedValue: futureValue,
        years,
        portfolio: allocation,
        expectedReturn: data.expected_return || 0,
        portfolioRisk: data.portfolio_risk || 0,
        monthlySip: calculatedMonthlySip,
        lumpsumAmount: calculatedLumpsum,
        lumpsumAvailable: lumpsumAvailable ? Number.parseFloat(lumpsumAvailable) : undefined,
        message: data.message || "Portfolio calculated successfully",
        optimizationStatus: data.optimization_status || "unknown",
        isLocked: false,
        status: "ongoing" as const,
        createdAt: new Date().toISOString(),
        sipStartDate: investmentType === "sip" ? sipStartDate : undefined,
        sipPayments: [],
        contributions: [],
        lastInflationUpdate: new Date().toISOString(),
        isHybrid: false,
        hybridSip: undefined as number | undefined,
      };

      // Check if lumpsum investment needs a hybrid strategy (shortfall scenario)
      if (investmentType === "lumpsum" && lumpsumAvailable) {
        const available = Number.parseFloat(lumpsumAvailable);
        const expectedReturn = data.expected_return || 0.08;
        const projectedGrowth = available * Math.pow(1 + expectedReturn, years);
        
        if (projectedGrowth < futureValue) {
          // Calculate hybrid SIP needed
          const r = expectedReturn / 12;
          const sipToFillGap = r > 0 
            ? (futureValue - projectedGrowth) * r / (Math.pow(1 + r, months) - 1)
            : (futureValue - projectedGrowth) / months;
          
          baseGoal.isHybrid = true;
          baseGoal.hybridSip = Math.round(Math.max(0, sipToFillGap));
          baseGoal.lumpsumAmount = available;
        }
      }

      // Store calculated goal data but don't save yet - wait for "Add Goal" click
      setCalculatedGoalData(baseGoal);
      setIsGoalSaved(false);
      
      if (investmentType === "lumpsum" && lumpsumAvailable && parseFloat(lumpsumAvailable) > calculatedLumpsum) {
        setPendingGoalData({ ...baseGoal, lumpsumAmount: calculatedLumpsum });
      }

      toast({
        title: "Portfolio ready",
        description: data.message || "Your investment plan is ready",
      });

    } catch (error) {
      console.error("Error:", error);
      
      // Fallback: generate a rule-based allocation locally so the user
      // still gets usable results even without the backend.
      const { futureValue, years, months, inflationRate } = calculateInflatedValue();
      const targetYearNum = parseInt(targetYear);
      const targetMonthNum = parseInt(targetMonth);

      const fallbackAllocations: Record<string, Record<string, number>> = {
        low:    { Equity: 0.20, Gold: 0.15, Bonds: 0.50, Cash: 0.15 },
        medium: { Equity: 0.45, Gold: 0.25, Bonds: 0.20, Cash: 0.10 },
        high:   { Equity: 0.70, Gold: 0.15, Bonds: 0.10, Cash: 0.05 },
      };
      const allocation = fallbackAllocations[riskAppetite] || fallbackAllocations.medium;

      // Estimate expected return from the allocation
      const assetReturns: Record<string, number> = { Equity: 0.12, Gold: 0.08, Bonds: 0.065, Cash: 0.055 };
      const expectedReturn = Object.entries(allocation).reduce((sum, [a, w]) => sum + w * (assetReturns[a] || 0.06), 0);
      const portfolioRisk = riskAppetite === "high" ? 0.14 : riskAppetite === "medium" ? 0.09 : 0.05;

      const r = expectedReturn / 12;
      const n = Math.max(months, 12);
      const monthlySip = r > 0 ? futureValue * r / (Math.pow(1 + r, n) - 1) : futureValue / n;
      const lumpsumAmount = futureValue / Math.pow(1 + expectedReturn, Math.max(years, 1));

      const fallbackData: PortfolioRecommendation = {
        portfolio: allocation,
        expected_return: expectedReturn,
        portfolio_risk: portfolioRisk,
        monthly_sip: Math.round(monthlySip),
        lumpsum_amount: Math.round(lumpsumAmount),
        optimization_status: "rule_based",
        message: "Calculated locally (backend unavailable)",
      };
      setPortfolioRecommendation(fallbackData);
      setShowResults(true);

      const newGoalId = `goal-${Date.now()}`;
      const calculatedMonthlySip = fallbackData.monthly_sip || (months ? futureValue / months : 0);
      const calculatedLumpsum = fallbackData.lumpsum_amount || futureValue;
      const goalName = goalType === "custom" ? customGoalName.trim() : goalType;

      const baseGoal = {
        id: newGoalId,
        goalType,
        goalName,
        goalAmount: Number.parseFloat(goalAmount),
        targetYear: targetYearNum,
        targetMonth: targetMonthNum,
        riskProfile: riskAppetite,
        investmentType,
        inflationRate,
        inflatedValue: futureValue,
        years,
        portfolio: allocation,
        expectedReturn,
        portfolioRisk,
        monthlySip: calculatedMonthlySip,
        lumpsumAmount: calculatedLumpsum,
        lumpsumAvailable: lumpsumAvailable ? Number.parseFloat(lumpsumAvailable) : undefined,
        message: fallbackData.message,
        optimizationStatus: "rule_based",
        isLocked: false,
        status: "ongoing" as const,
        createdAt: new Date().toISOString(),
        sipStartDate: investmentType === "sip" ? sipStartDate : undefined,
        sipPayments: [],
        contributions: [],
        lastInflationUpdate: new Date().toISOString(),
        isHybrid: false,
        hybridSip: undefined as number | undefined,
      };

      // Check if lumpsum investment needs a hybrid strategy (shortfall scenario)
      if (investmentType === "lumpsum" && lumpsumAvailable) {
        const available = Number.parseFloat(lumpsumAvailable);
        const projectedGrowth = available * Math.pow(1 + expectedReturn, years);
        
        if (projectedGrowth < futureValue) {
          // Calculate hybrid SIP needed
          const sipToFillGap = r > 0 
            ? (futureValue - projectedGrowth) * r / (Math.pow(1 + r, n) - 1)
            : (futureValue - projectedGrowth) / n;
          
          baseGoal.isHybrid = true;
          baseGoal.hybridSip = Math.round(Math.max(0, sipToFillGap));
          baseGoal.lumpsumAmount = available;
        }
      }

      // Store calculated goal data but don't save yet - wait for "Add Goal" click
      setCalculatedGoalData(baseGoal);
      setIsGoalSaved(false);

      toast({
        title: "Portfolio ready (offline mode)",
        description: "Used rule-based allocation. Start the backend for Markowitz-optimized results.",
      });
    } finally {
      setIsCalculating(false);
    }
  };

  const handleExcessDecision = (acceptExcess: boolean) => {
    if (!pendingGoalData) return;
    const updatedGoal = {
      ...pendingGoalData,
      lumpsumAmount: acceptExcess
        ? parseFloat(lumpsumAvailable)
        : pendingGoalData.lumpsumAmount,
    };
    setCalculatedGoalData(updatedGoal);
    setPendingGoalData(null);
    setShowExcessDialog(false);
  };

  const handleAddGoal = () => {
    if (!calculatedGoalData) {
      toast({
        title: "No plan calculated",
        description: "Please calculate your investment plan first.",
        variant: "destructive",
      });
      return;
    }

    // Check for excess lumpsum before adding
    if (calculatedGoalData.investmentType === "lumpsum" && 
        calculatedGoalData.lumpsumAvailable && 
        calculatedGoalData.lumpsumAvailable > (calculatedGoalData.lumpsumAmount || 0) &&
        !isGoalSaved) {
      setPendingGoalData(calculatedGoalData);
      setShowExcessDialog(true);
      return;
    }

    // Add the goal to the portfolio
    addGoal(calculatedGoalData);
    setIsGoalSaved(true);
    
    toast({
      title: "Goal added to portfolio",
      description: "Your goal is now active and being tracked.",
    });
    navigate('/portfolio');
  };

  const results = showResults ? calculateInflatedValue() : null;
  const animatePlanner = Boolean((location.state as { fromAddGoal?: boolean } | null)?.fromAddGoal);


  return (
    <div className={`min-h-screen bg-background ${animatePlanner ? "animate-slide-up" : ""}`}>
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Investment Planner</h1>
          <p className="text-muted-foreground">Plan your investments to achieve your financial goals</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                Calculate Your Goal
              </CardTitle>
              <CardDescription>Enter your goal details to get personalized recommendations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="goal">Goal Description *</Label>
                <Select value={goalType} onValueChange={setGoalType}>
                  <SelectTrigger id="goal">
                    <SelectValue placeholder="Select your financial goal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="car">
                      Buy a Car ({((inflationRates.car || 0.055) * 100).toFixed(1)}% inflation)
                    </SelectItem>
                    <SelectItem value="house">
                      Buy a House ({((inflationRates.house || 0.0726) * 100).toFixed(1)}% inflation)
                    </SelectItem>
                    <SelectItem value="education">
                      Child's Education ({((inflationRates.education || 0.115) * 100).toFixed(1)}% inflation)
                    </SelectItem>
                    <SelectItem value="gold">
                      Gold Investment ({((inflationRates.gold || 0.1403) * 100).toFixed(1)}% inflation)
                    </SelectItem>
                  </SelectContent>
                </Select>
                {goalType && inflationRatesDisplay[goalType] && (
                  <p className="text-xs text-muted-foreground">
                    {inflationRatesDisplay[goalType].description} ({inflationRatesDisplay[goalType].period})
                  </p>
                )}
              </div>

              {goalType === "custom" && (
                <div className="space-y-2">
                  <Label htmlFor="custom-goal">Name your goal</Label>
                  <Input
                    id="custom-goal"
                    type="text"
                    placeholder="e.g., Startup Fund"
                    value={customGoalName}
                    onChange={(e) => setCustomGoalName(e.target.value)}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="amount">Current Cost of Goal (₹) *</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="e.g., 1000000"
                  value={goalAmount}
                  onChange={(e) => setGoalAmount(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Target Month & Year *</Label>
                <div className="grid grid-cols-2 gap-3">
                  <Select value={targetMonth} onValueChange={setTargetMonth}>
                    <SelectTrigger>
                      <SelectValue placeholder="Month" />
                    </SelectTrigger>
                    <SelectContent>
                      {monthOptions.map((month) => (
                        <SelectItem key={month.value} value={month.value}>
                          {month.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    id="year"
                    type="number"
                    placeholder={`e.g., ${minYear}`}
                    value={targetYear}
                    onChange={(e) => setTargetYear(e.target.value)}
                    min={minYear}
                  />
                </div>
                <p className="text-xs text-muted-foreground">Minimum year: {minYear}</p>
              </div>

              <div className="space-y-3">
                <Label>Investment Type *</Label>
                <RadioGroup value={investmentType} onValueChange={setInvestmentType}>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="sip" id="sip" />
                    <Label htmlFor="sip" className="flex items-center gap-2 cursor-pointer flex-1">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <div>
                        <div className="font-medium">SIP (Systematic Investment Plan)</div>
                        <div className="text-xs text-muted-foreground">Monthly investments</div>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="lumpsum" id="lumpsum" />
                    <Label htmlFor="lumpsum" className="flex items-center gap-2 cursor-pointer flex-1">
                      <PiggyBank className="h-4 w-4 text-success" />
                      <div>
                        <div className="font-medium">Lumpsum</div>
                        <div className="text-xs text-muted-foreground">One-time investment</div>
                      </div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              {investmentType === "sip" && (
                <div className="space-y-2">
                  <Label htmlFor="sip-start">SIP Start Date (optional)</Label>
                  <Input
                    id="sip-start"
                    type="date"
                    value={sipStartDate}
                    onChange={(e) => setSipStartDate(e.target.value)}
                  />
                </div>
              )}

              {investmentType === "lumpsum" && (
                <div className="space-y-2">
                  <Label htmlFor="lumpsum-available">Lumpsum Available (₹)</Label>
                  <Input
                    id="lumpsum-available"
                    type="number"
                    placeholder="e.g., 1200000"
                    value={lumpsumAvailable}
                    onChange={(e) => setLumpsumAvailable(e.target.value)}
                  />
                </div>
              )}

              <div className="space-y-3">
                <Label>Risk Appetite *</Label>
                <RadioGroup value={riskAppetite} onValueChange={setRiskAppetite}>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="low" id="low" />
                    <Label htmlFor="low" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Shield className="h-4 w-4 text-success" />
                      <div>
                        <div className="font-medium">Low Risk</div>
                        <div className="text-xs text-muted-foreground">Fixed deposits, government bonds, debt funds</div>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="medium" id="medium" />
                    <Label htmlFor="medium" className="flex items-center gap-2 cursor-pointer flex-1">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <div>
                        <div className="font-medium">Medium Risk</div>
                        <div className="text-xs text-muted-foreground">Balanced funds, index funds, hybrid mutual funds</div>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="high" id="high" />
                    <Label htmlFor="high" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Zap className="h-4 w-4 text-destructive" />
                      <div>
                        <div className="font-medium">High Risk</div>
                        <div className="text-xs text-muted-foreground">Equity stocks, equity mutual funds, thematic/sectoral funds</div>
                      </div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <Button 
                onClick={handleCalculate} 
                className="w-full" 
                size="lg"
                disabled={!goalAmount || !targetYear || !targetMonth || !goalType || !riskAppetite || (goalType === "custom" && !customGoalName.trim()) || isCalculating}
              >
                {isCalculating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Calculating...
                  </>
                ) : (
                  "Calculate Investment Plan"
                )}
              </Button>

              {showResults && results && (
                <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
                  <CardContent className="pt-6 space-y-4">
                    <div className="text-center space-y-2">
                      <p className="text-sm text-muted-foreground">Current Value</p>
                      <p className="text-2xl font-bold text-foreground">₹{parseFloat(goalAmount).toLocaleString('en-IN')}</p>
                    </div>
                    <div className="text-center space-y-2">
                      <p className="text-sm text-muted-foreground">Predicted Future Value ({results.months} months)</p>
                      <p className="text-3xl font-bold text-primary">₹{results.futureValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                      <Badge variant="secondary">
                        +{((results.inflationRate * 100).toFixed(1))}% annual inflation
                      </Badge>
                    </div>
                    <div className="pt-2">
                      <p className="text-xs text-muted-foreground text-center mb-2">Inflation Impact</p>
                      <Progress value={results.inflationRate * 100} className="h-2" />
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>

          {/* Investment Recommendations */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-foreground">
                {showResults ? "Recommended Investment Strategy" : "Investment Options"}
              </h2>
              {showResults && riskAppetite && (
                <Badge variant="outline" className="capitalize">
                  {riskAppetite} Risk Profile
                </Badge>
              )}
            </div>
            
            {!showResults && (
              <Card className="bg-muted/50">
                <CardContent className="pt-6 text-center text-muted-foreground">
                  <Calculator className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>Enter your goal details and risk appetite to see personalized investment recommendations</p>
                </CardContent>
              </Card>
            )}

            {showResults && results && portfolioRecommendation && (
              <Card className="border-2 border-primary">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <TrendingUp className="h-6 w-6 text-primary" />
                    Portfolio Plan
                  </CardTitle>
                  <CardDescription>Risk-based allocation matched to your goal</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Portfolio Allocation */}
                  <div className="space-y-3">
                    <h3 className="font-semibold">Asset Allocation</h3>
                    {Object.entries(portfolioRecommendation.portfolio).map(([asset, weight]) => {
                      const percentage = (weight * 100).toFixed(1);
                      return (
                        <div key={asset} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium">{asset}</span>
                            <span className="text-muted-foreground">{percentage}%</span>
                          </div>
                          <Progress value={weight * 100} className="h-2" />
                        </div>
                      );
                    })}
                  </div>

                  {/* Investment Details */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-accent/20 rounded-lg">
                    <div>
                      <p className="text-xs text-muted-foreground">Expected Annual Return</p>
                      <p className="text-xl font-bold text-success">
                        {(portfolioRecommendation.expected_return * 100).toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Portfolio Risk</p>
                      <p className="text-xl font-bold text-primary">
                        {(portfolioRecommendation.portfolio_risk * 100).toFixed(2)}%
                      </p>
                    </div>
                  </div>

                  {/* SIP/Lumpsum Amount */}
                  <div className="p-4 bg-gradient-to-br from-primary to-accent text-white rounded-lg border-2 border-primary/30">
                    <div className="text-center space-y-2">
                      <p className="text-sm text-white/90">
                        {investmentType === "sip" ? "Monthly SIP Required" : "Lumpsum Required"}
                      </p>
                      <p className="text-3xl font-bold text-white">
                        ₹{(investmentType === "sip" 
                          ? (portfolioRecommendation.monthly_sip ?? 0)
                          : (portfolioRecommendation.lumpsum_amount ?? 0)
                        ).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </p>
                    </div>
                    {investmentType === "sip" && portfolioRecommendation.monthly_sip && (
                      <div className="mt-4 pt-4 border-t border-white/30">
                        <div className="flex justify-between text-sm">
                          <span className="text-white/90">Monthly investment amount</span>
                          <span className="font-semibold">
                            ₹{portfolioRecommendation.monthly_sip.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Funding Gap Analysis for Lumpsum */}
                  {investmentType === "lumpsum" && lumpsumAvailable && results && (() => {
                    const available = Number.parseFloat(lumpsumAvailable);
                    const required = portfolioRecommendation.lumpsum_amount ?? 0;
                    const shortfall = required - available;
                    const expectedReturn = portfolioRecommendation.expected_return || 0.08;
                    const projectedGrowth = available * Math.pow(1 + expectedReturn, results.years);
                    const willReachGoal = projectedGrowth >= results.futureValue;
                    
                    // Calculate hybrid SIP needed to bridge gap
                    const months = results.months || 12;
                    const r = expectedReturn / 12;
                    const sipToFillGap = shortfall > 0 && r > 0 
                      ? (results.futureValue - projectedGrowth) * r / (Math.pow(1 + r, months) - 1)
                      : 0;

                    return (
                      <div className="space-y-4 p-4 bg-accent/10 rounded-lg border">
                        <h4 className="font-semibold flex items-center gap-2">
                          <PiggyBank className="h-4 w-4" />
                          Funding Gap Analysis
                        </h4>
                        
                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 bg-background rounded-lg">
                            <p className="text-xs text-muted-foreground">Your Available Amount</p>
                            <p className="text-lg font-bold text-primary">₹{available.toLocaleString('en-IN')}</p>
                          </div>
                          <div className="p-3 bg-background rounded-lg">
                            <p className="text-xs text-muted-foreground">Required Investment Today</p>
                            <p className="text-lg font-bold">₹{Math.round(required).toLocaleString('en-IN')}</p>
                          </div>
                        </div>

                        {shortfall > 0 ? (
                          <>
                            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                              <p className="text-xs text-muted-foreground">Shortfall</p>
                              <p className="text-lg font-bold text-destructive">₹{Math.round(shortfall).toLocaleString('en-IN')}</p>
                            </div>
                            
                            <div className="space-y-2">
                              <p className="text-sm font-medium">Your ₹{available.toLocaleString('en-IN')} will grow to:</p>
                              <div className="p-3 bg-background rounded-lg">
                                <p className="text-lg font-bold text-success">₹{Math.round(projectedGrowth).toLocaleString('en-IN')}</p>
                                <p className="text-xs text-muted-foreground">
                                  In {formatYears(results.years)} years @ {(expectedReturn * 100).toFixed(1)}% returns
                                </p>
                              </div>
                            </div>

                            <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg space-y-3">
                              <p className="font-semibold text-primary flex items-center gap-2">
                                <Zap className="h-4 w-4" />
                                Hybrid Strategy Recommended
                              </p>
                              <p className="text-sm text-muted-foreground">
                                Invest your ₹{available.toLocaleString('en-IN')} now and add a monthly SIP to reach your goal:
                              </p>
                              <div className="flex items-center justify-between p-3 bg-background rounded-lg">
                                <span className="text-sm">Additional Monthly SIP Needed</span>
                                <span className="text-xl font-bold text-primary">
                                  ₹{Math.round(Math.max(0, sipToFillGap)).toLocaleString('en-IN')}
                                </span>
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="p-3 bg-success/10 border border-success/20 rounded-lg">
                            <p className="text-xs text-muted-foreground">Surplus</p>
                            <p className="text-lg font-bold text-success">₹{Math.round(Math.abs(shortfall)).toLocaleString('en-IN')}</p>
                            <p className="text-xs text-muted-foreground mt-1">You have more than enough to reach your goal!</p>
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  <div className="flex gap-2">
                    <Button 
                      className="flex-1" 
                      onClick={handleAddGoal}
                      disabled={isGoalSaved}
                    >
                      {isGoalSaved ? "Goal Added ✓" : "Add Goal to Portfolio"}
                    </Button>
                    <Button variant="outline" className="flex-1" onClick={() => {
                      const goalData = calculatedGoalData;
                      if (!goalData) {
                        toast({
                          title: "No report available",
                          description: "Calculate your plan first.",
                          variant: "destructive",
                        });
                        return;
                      }
                      
                      // Risk-based fund recommendations (same as GoalDetails)
                      const RISK_FUND_MAP: Record<string, Array<{ label: string; description: string; examples: string[] }>> = {
                        low: [
                          { label: "Fixed Deposits", description: "Invest in bank fixed deposits", examples: ["SBI FD", "HDFC FD", "ICICI FD"] },
                          { label: "Government Bonds", description: "Invest in sovereign-backed securities", examples: ["RBI Savings Bonds", "G-Sec", "PPF"] },
                          { label: "Debt Funds", description: "Invest in fixed-income securities", examples: ["HDFC Short Term Debt", "SBI Magnum Gilt", "ICICI Pru All Seasons Bond"] },
                        ],
                        medium: [
                          { label: "Balanced Funds", description: "Invest in a combination of debt and equity", examples: ["HDFC Balanced Advantage", "ICICI Pru Balanced Advantage"] },
                          { label: "Index Funds", description: "Track market indices for steady growth", examples: ["UTI Nifty 50", "HDFC Index S&P BSE Sensex", "Nippon India Nifty 50"] },
                          { label: "Hybrid Mutual Funds", description: "Offers benefit of asset allocation and diversification", examples: ["SBI Equity Hybrid", "Mirae Asset Hybrid"] },
                        ],
                        high: [
                          { label: "Equity Stocks", description: "Invest in equities and equity related instruments", examples: ["Nifty 50 stocks", "Mid-cap stocks", "Small-cap stocks"] },
                          { label: "Equity Mutual Funds", description: "For long-term capital growth", examples: ["Axis Bluechip", "SBI Small Cap", "Mirae Asset Large Cap"] },
                          { label: "Thematic / Sectoral Funds", description: "Tailored for specific themes or sectors", examples: ["ICICI Technology", "SBI PSU Fund", "Nippon India Pharma"] },
                        ],
                      };
                      
                      const doc = new jsPDF();
                      const pageWidth = doc.internal.pageSize.getWidth();
                      const pageHeight = doc.internal.pageSize.getHeight();
                      const primaryColor: [number, number, number] = [124, 99, 64]; // #7c6340
                      const accentColor: [number, number, number] = [91, 138, 114]; // #5b8a72
                      const successColor: [number, number, number] = [34, 139, 34];
                      const mutedColor: [number, number, number] = [128, 128, 128];
                      const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                      
                      const riskFunds = RISK_FUND_MAP[goalData.riskProfile] || RISK_FUND_MAP.medium;
                      const investmentAmt = goalData.investmentType === "sip" ? goalData.monthlySip : goalData.lumpsumAmount;
                      const netInvestment = goalData.investmentType === "sip" 
                        ? (goalData.monthlySip || 0) * (goalData.years || 1) * 12 
                        : (goalData.lumpsumAmount || 0);
                      const estimatedReturns = Math.max(0, (goalData.inflatedValue || 0) - netInvestment);
                      
                      // ==================== PAGE 1 ====================
                      // Header
                      doc.setFillColor(...primaryColor);
                      doc.rect(0, 0, pageWidth, 40, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(22);
                      doc.setFont("helvetica", "bold");
                      doc.text("MoneyMentor", 14, 20);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "normal");
                      doc.text("Investment Goal Report", 14, 30);
                      doc.setFontSize(9);
                      doc.text(`Generated: ${new Date().toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}`, pageWidth - 14, 25, { align: "right" });
                      
                      let yPos = 52;
                      
                      // Goal Title with Risk Badge
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(16);
                      doc.setFont("helvetica", "bold");
                      doc.text((goalData.goalName || goalData.goalType).toUpperCase(), 14, yPos);
                      doc.setFillColor(...accentColor);
                      doc.roundedRect(pageWidth - 48, yPos - 7, 34, 9, 2, 2, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(7);
                      doc.text(`${(goalData.riskProfile || "medium").toUpperCase()} RISK`, pageWidth - 31, yPos - 1, { align: "center" });
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(9);
                      doc.setFont("helvetica", "normal");
                      doc.text("Goal details and portfolio breakdown", 14, yPos + 8);
                      
                      yPos += 20;
                      
                      // ===== SECTION 1: CURRENT INFLATION IMPACT =====
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14, yPos, pageWidth - 28, 50, 3, 3, 'F');
                      doc.setDrawColor(...primaryColor);
                      doc.setLineWidth(0.8);
                      doc.roundedRect(14, yPos, pageWidth - 28, 50, 3, 3, 'S');
                      
                      doc.setTextColor(...primaryColor);
                      doc.setFontSize(9);
                      doc.setFont("helvetica", "bold");
                      doc.text("CURRENT INFLATION IMPACT", 20, yPos + 10);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("How inflation affects your financial goals", 85, yPos + 10);
                      
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(20);
                      doc.setFont("helvetica", "bold");
                      doc.text(`${((goalData.inflationRate || 0.06) * 100).toFixed(1)}% p.a.`, 20, yPos + 26);
                      
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.setFont("helvetica", "normal");
                      const purchasingPowerLoss = Math.round((goalData.inflationRate || 0.06) * 10000);
                      doc.text(`Your purchasing power decreases by approx ₹${purchasingPowerLoss.toLocaleString("en-IN")} for every ₹10,000 annually`, 20, yPos + 35);
                      
                      // Current vs Inflation-adjusted mini boxes
                      const miniBoxWidth = (pageWidth - 48) / 2;
                      doc.setFillColor(255, 255, 255);
                      doc.roundedRect(20, yPos + 40, miniBoxWidth - 5, 22, 2, 2, 'F');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.text("Total Goal Value Today", 25, yPos + 48);
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "bold");
                      doc.text(`₹${goalData.goalAmount.toLocaleString("en-IN")}`, 25, yPos + 57);
                      
                      doc.setFillColor(...primaryColor);
                      doc.roundedRect(20 + miniBoxWidth, yPos + 40, miniBoxWidth - 5, 22, 2, 2, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Inflation-Adjusted Value", 25 + miniBoxWidth, yPos + 48);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "bold");
                      doc.text(`₹${(goalData.inflatedValue || goalData.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, 25 + miniBoxWidth, yPos + 57);
                      
                      yPos += 75;
                      
                      // ===== SECTION 2: GOAL SUMMARY =====
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "bold");
                      doc.text("Goal Summary", 14, yPos);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.setFont("helvetica", "normal");
                      doc.text("Inflation-adjusted target details", 55, yPos);
                      yPos += 8;
                      
                      const boxWidth = (pageWidth - 42) / 3;
                      
                      // Row 1: Current Cost, Inflation-Adjusted Target, Target Date
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14, yPos, boxWidth, 28, 2, 2, 'F');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.text("Current Cost", 18, yPos + 8);
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(12);
                      doc.setFont("helvetica", "bold");
                      doc.text(`₹${goalData.goalAmount.toLocaleString("en-IN")}`, 18, yPos + 19);
                      
                      doc.setFillColor(...primaryColor);
                      doc.roundedRect(14 + boxWidth + 7, yPos, boxWidth, 28, 2, 2, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Inflation-Adjusted Target", 18 + boxWidth + 7, yPos + 8);
                      doc.setFontSize(12);
                      doc.setFont("helvetica", "bold");
                      doc.text(`₹${(goalData.inflatedValue || goalData.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, 18 + boxWidth + 7, yPos + 19);
                      
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14 + (boxWidth + 7) * 2, yPos, boxWidth, 28, 2, 2, 'F');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Target Date", 18 + (boxWidth + 7) * 2, yPos + 8);
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(12);
                      doc.setFont("helvetica", "bold");
                      const targetDateStr = goalData.targetMonth ? `${monthNames[goalData.targetMonth - 1]} ${goalData.targetYear}` : goalData.targetYear?.toString() || "N/A";
                      doc.text(targetDateStr, 18 + (boxWidth + 7) * 2, yPos + 19);
                      
                      yPos += 35;
                      
                      // Row 2: Investment Plan, Timeline
                      const halfWidth = (pageWidth - 35) / 2;
                      doc.setFillColor(248, 246, 243);
                      doc.setDrawColor(220, 220, 220);
                      doc.setLineWidth(0.3);
                      doc.roundedRect(14, yPos, halfWidth, 32, 2, 2, 'FD');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Investment Plan", 18, yPos + 8);
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(10);
                      doc.setFont("helvetica", "bold");
                      doc.text(goalData.investmentType === "sip" ? "Monthly SIP" : "Lumpsum", 18, yPos + 17);
                      doc.setTextColor(...primaryColor);
                      doc.setFontSize(14);
                      doc.text(`₹${(investmentAmt || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}${goalData.investmentType === "sip" ? "/month" : ""}`, 18, yPos + 28);
                      
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14 + halfWidth + 7, yPos, halfWidth, 32, 2, 2, 'FD');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Timeline", 18 + halfWidth + 7, yPos + 8);
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(10);
                      doc.setFont("helvetica", "bold");
                      doc.text(`${formatYears(goalData.years) || 1} years`, 18 + halfWidth + 7, yPos + 17);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.setFont("helvetica", "normal");
                      doc.text(`Inflation rate: ${((goalData.inflationRate || 0.06) * 100).toFixed(1)}%`, 18 + halfWidth + 7, yPos + 26);
                      
                      yPos += 42;
                      
                      // ===== SECTION 3: ASSET ALLOCATION =====
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "bold");
                      doc.text("Asset Allocation", 14, yPos);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.setFont("helvetica", "normal");
                      doc.text("Markowitz-optimized portfolio", 58, yPos);
                      yPos += 8;
                      
                      if (goalData.portfolio && Object.keys(goalData.portfolio).length > 0) {
                        const allocationColors: [number, number, number][] = [
                          [124, 99, 64], [160, 128, 96], [91, 138, 114], [184, 160, 128], [74, 124, 140], [196, 176, 144]
                        ];
                        
                        Object.entries(goalData.portfolio).forEach(([asset, weight], index) => {
                          const percentage = (Number(weight) * 100);
                          const barWidth = (pageWidth - 80) * (percentage / 100);
                          
                          // Color dot + Asset label
                          doc.setFillColor(...allocationColors[index % allocationColors.length]);
                          doc.circle(18, yPos + 3, 3, 'F');
                          doc.setTextColor(0, 0, 0);
                          doc.setFontSize(9);
                          doc.setFont("helvetica", "normal");
                          doc.text(asset, 24, yPos + 5);
                          doc.text(`${percentage.toFixed(1)}%`, pageWidth - 14, yPos + 5, { align: "right" });
                          
                          // Progress bar
                          doc.setFillColor(230, 230, 230);
                          doc.roundedRect(14, yPos + 8, pageWidth - 28, 5, 1.5, 1.5, 'F');
                          doc.setFillColor(...allocationColors[index % allocationColors.length]);
                          if (barWidth > 0) doc.roundedRect(14, yPos + 8, Math.max(barWidth, 3), 5, 1.5, 1.5, 'F');
                          
                          yPos += 16;
                        });
                      }
                      
                      yPos += 5;
                      
                      // ===== SECTION 4: INVESTMENT BREAKDOWN =====
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(11);
                      doc.setFont("helvetica", "bold");
                      doc.text("Investment Breakdown", 14, yPos);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.setFont("helvetica", "normal");
                      doc.text(goalData.investmentType === "sip" ? "Monthly SIP schedule" : "Lumpsum investment details", 70, yPos);
                      yPos += 8;
                      
                      // Main investment box
                      doc.setFillColor(248, 246, 243);
                      doc.setDrawColor(...primaryColor);
                      doc.setLineWidth(0.5);
                      doc.roundedRect(14, yPos, pageWidth - 28, goalData.investmentType === "sip" ? 45 : 28, 3, 3, 'FD');
                      
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(8);
                      doc.text(goalData.investmentType === "sip" ? "Monthly SIP Required" : "Lumpsum Required", pageWidth / 2, yPos + 10, { align: "center" });
                      doc.setTextColor(...primaryColor);
                      doc.setFontSize(18);
                      doc.setFont("helvetica", "bold");
                      doc.text(`₹${(investmentAmt || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}${goalData.investmentType === "sip" ? "/Month" : ""}`, pageWidth / 2, yPos + 22, { align: "center" });
                      
                      if (goalData.investmentType === "sip") {
                        // Net Investment and Estimated Returns
                        doc.setDrawColor(200, 200, 200);
                        doc.setLineWidth(0.3);
                        doc.line(20, yPos + 28, pageWidth - 20, yPos + 28);
                        
                        doc.setTextColor(...mutedColor);
                        doc.setFontSize(8);
                        doc.setFont("helvetica", "normal");
                        doc.text("Net Investment", 30, yPos + 36);
                        doc.setTextColor(0, 0, 0);
                        doc.setFontSize(10);
                        doc.setFont("helvetica", "bold");
                        doc.text(`₹${netInvestment.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, 30, yPos + 44);
                        
                        doc.setTextColor(...mutedColor);
                        doc.setFontSize(8);
                        doc.setFont("helvetica", "normal");
                        doc.text("Estimated Returns", pageWidth - 60, yPos + 36);
                        doc.setTextColor(...successColor);
                        doc.setFontSize(10);
                        doc.setFont("helvetica", "bold");
                        doc.text(`₹${estimatedReturns.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, pageWidth - 60, yPos + 44);
                        
                        yPos += 52;
                      } else {
                        yPos += 35;
                      }
                      
                      // Expected Return & Portfolio Risk
                      yPos += 5;
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14, yPos, halfWidth, 25, 2, 2, 'F');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Expected Annual Return", 18, yPos + 8);
                      doc.setTextColor(...successColor);
                      doc.setFontSize(14);
                      doc.setFont("helvetica", "bold");
                      doc.text(`${((goalData.expectedReturn || 0) * 100).toFixed(2)}%`, 18, yPos + 19);
                      
                      doc.setFillColor(248, 246, 243);
                      doc.roundedRect(14 + halfWidth + 7, yPos, halfWidth, 25, 2, 2, 'F');
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(7);
                      doc.setFont("helvetica", "normal");
                      doc.text("Portfolio Risk", 18 + halfWidth + 7, yPos + 8);
                      doc.setTextColor(...primaryColor);
                      doc.setFontSize(14);
                      doc.setFont("helvetica", "bold");
                      doc.text(`${((goalData.portfolioRisk || 0) * 100).toFixed(2)}%`, 18 + halfWidth + 7, yPos + 19);
                      
                      // ==================== PAGE 2: RECOMMENDED FUNDS ====================
                      doc.addPage();
                      
                      // Header for page 2
                      doc.setFillColor(...primaryColor);
                      doc.rect(0, 0, pageWidth, 30, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(16);
                      doc.setFont("helvetica", "bold");
                      doc.text("MoneyMentor", 14, 18);
                      doc.setFontSize(10);
                      doc.setFont("helvetica", "normal");
                      doc.text("Investment Goal Report - Continued", pageWidth - 14, 18, { align: "right" });
                      
                      yPos = 45;
                      
                      // ===== SECTION 5: RECOMMENDED FUND CATEGORIES =====
                      doc.setTextColor(0, 0, 0);
                      doc.setFontSize(12);
                      doc.setFont("helvetica", "bold");
                      doc.text("Recommended Fund Categories", 14, yPos);
                      doc.setTextColor(...mutedColor);
                      doc.setFontSize(9);
                      doc.setFont("helvetica", "normal");
                      doc.text(`Based on your ${goalData.riskProfile || "medium"} risk profile`, 14, yPos + 10);
                      yPos += 18;
                      
                      riskFunds.forEach((fund, fundIndex) => {
                        // Fund card
                        doc.setFillColor(248, 246, 243);
                        doc.roundedRect(14, yPos, pageWidth - 28, 55, 3, 3, 'F');
                        
                        // Fund header
                        doc.setFillColor(...primaryColor);
                        doc.roundedRect(14, yPos, pageWidth - 28, 14, 3, 3, 'F');
                        doc.setFillColor(248, 246, 243);
                        doc.rect(14, yPos + 10, pageWidth - 28, 4, 'F');
                        
                        doc.setTextColor(255, 255, 255);
                        doc.setFontSize(10);
                        doc.setFont("helvetica", "bold");
                        doc.text(fund.label, 20, yPos + 9);
                        
                        // Description
                        doc.setTextColor(...mutedColor);
                        doc.setFontSize(8);
                        doc.setFont("helvetica", "normal");
                        doc.text(fund.description, 20, yPos + 22);
                        
                        // Examples with checkmarks
                        let exY = yPos + 32;
                        fund.examples.forEach((ex) => {
                          doc.setFillColor(...successColor);
                          doc.circle(22, exY - 1.5, 2, 'F');
                          doc.setTextColor(255, 255, 255);
                          doc.setFontSize(6);
                          doc.text("✓", 20.5, exY);
                          
                          doc.setTextColor(0, 0, 0);
                          doc.setFontSize(8);
                          doc.setFont("helvetica", "normal");
                          doc.text(ex, 28, exY);
                          exY += 8;
                        });
                        
                        yPos += 62;
                      });
                      
                      // Footer on page 2
                      doc.setFillColor(...primaryColor);
                      doc.rect(0, pageHeight - 20, pageWidth, 20, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(8);
                      doc.text("Generated by MoneyMentor - Your Inflation-Aware Investment Partner", pageWidth / 2, pageHeight - 8, { align: "center" });
                      
                      // Footer on page 1
                      doc.setPage(1);
                      doc.setFillColor(...primaryColor);
                      doc.rect(0, pageHeight - 15, pageWidth, 15, 'F');
                      doc.setTextColor(255, 255, 255);
                      doc.setFontSize(7);
                      doc.text("Page 1 of 2 | Generated by MoneyMentor", pageWidth / 2, pageHeight - 5, { align: "center" });
                      
                      doc.save(`MoneyMentor-${goalData.goalName || goalData.goalType}-Report.pdf`);
                      
                      toast({
                        title: "Report Downloaded",
                        description: "Your detailed investment report has been saved.",
                      });
                    }}>
                      Download Report
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      <AlertDialog open={showExcessDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excess Lumpsum Detected</AlertDialogTitle>
            <AlertDialogDescription>
              Your investment exceeds the required amount. Do you want to invest the extra amount?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => handleExcessDecision(false)}>No, reduce to required</AlertDialogCancel>
            <AlertDialogAction onClick={() => handleExcessDecision(true)}>Yes, invest extra</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default InvestmentPlanner;

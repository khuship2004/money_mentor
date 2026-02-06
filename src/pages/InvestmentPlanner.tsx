import { useMemo, useState } from "react";
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
  const { addGoal, updateGoal, goals } = useGoals();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [goalId, setGoalId] = useState<string>("");
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

  // Asset-specific inflation rates (historical averages)
  const inflationRates: Record<string, number> = {
    car: 0.05, // 5%
    house: 0.08, // 8%
    education: 0.10, // 10%
    gold: 0.07, // 7%
    custom: 0.06, // 6%
  };

  

  const API_BASE_URL = "http://localhost:8000";

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
        lumpsumAvailable: lumpsumAvailable ? parseFloat(lumpsumAvailable) : undefined,
        message: data.message || "Portfolio calculated successfully",
        optimizationStatus: data.optimization_status || "unknown",
        isLocked: false,
        status: "ongoing" as const,
        createdAt: new Date().toISOString(),
        sipStartDate: investmentType === "sip" ? sipStartDate : undefined,
        sipPayments: [],
        contributions: [],
        lastInflationUpdate: new Date().toISOString(),
      };

      if (investmentType === "lumpsum" && lumpsumAvailable && parseFloat(lumpsumAvailable) > calculatedLumpsum) {
        setPendingGoalData({ ...baseGoal, lumpsumAmount: calculatedLumpsum });
        setShowExcessDialog(true);
      } else {
        addGoal(baseGoal);
        setGoalId(newGoalId);
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
        goalAmount: parseFloat(goalAmount),
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
        lumpsumAvailable: lumpsumAvailable ? parseFloat(lumpsumAvailable) : undefined,
        message: fallbackData.message,
        optimizationStatus: "rule_based",
        isLocked: false,
        status: "ongoing" as const,
        createdAt: new Date().toISOString(),
        sipStartDate: investmentType === "sip" ? sipStartDate : undefined,
        sipPayments: [],
        contributions: [],
        lastInflationUpdate: new Date().toISOString(),
      };

      addGoal(baseGoal);
      setGoalId(newGoalId);

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
    addGoal(updatedGoal);
    setGoalId(updatedGoal.id);
    setPendingGoalData(null);
    setShowExcessDialog(false);
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
                    <SelectItem value="car">Buy a Car (5% inflation)</SelectItem>
                    <SelectItem value="house">Buy a House (8% inflation)</SelectItem>
                    <SelectItem value="education">Child's Education (10% inflation)</SelectItem>
                    <SelectItem value="gold">Gold Investment (7% inflation)</SelectItem>
                    <SelectItem value="custom">Custom Goal (6% inflation)</SelectItem>
                  </SelectContent>
                </Select>
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

                  <div className="flex gap-2">
                    <Button className="flex-1" onClick={() => {
                      if (!goalId) {
                        toast({
                          title: "Goal not saved",
                          description: "Please calculate and save the plan first.",
                          variant: "destructive",
                        });
                        return;
                      }
                      const existing = goals.find((g) => g.id === goalId);
                      if (existing) {
                        const updated = {
                          ...existing,
                          isLocked: true,
                          status: "ongoing",
                          sipStartDate: investmentType === "sip" ? sipStartDate : existing.sipStartDate,
                          contributions: investmentType === "lumpsum"
                            ? [
                                {
                                  date: new Date().toISOString(),
                                  amount: existing.lumpsumAmount || 0,
                                  type: "lumpsum",
                                  status: "paid",
                                },
                              ]
                            : existing.contributions || [],
                        };
                        updateGoal(existing.id, updated);
                      }
                      toast({
                        title: "Goal added to portfolio",
                        description: "Your goal is now active and being tracked.",
                      });
                      navigate('/portfolio');
                    }}>
                      Add a Goal
                    </Button>
                    <Button variant="outline" className="flex-1" onClick={() => {
                      if (!goalId) {
                        toast({
                          title: "No report available",
                          description: "Calculate your plan first.",
                          variant: "destructive",
                        });
                        return;
                      }
                      const existing = goals.find((g) => g.id === goalId);
                      if (!existing) return;
                      const doc = new jsPDF();
                      doc.setFontSize(16);
                      doc.text("MoneyMentor Goal Report", 14, 18);
                      doc.setFontSize(11);
                      doc.text(`Goal: ${existing.goalName || existing.goalType}`, 14, 30);
                      doc.text(`Target Date: ${existing.targetMonth}/${existing.targetYear}`, 14, 38);
                      doc.text(`Goal Amount: ₹${existing.goalAmount.toLocaleString("en-IN")}`, 14, 46);
                      doc.text(`Inflation Assumption: ${(existing.inflationRate || 0) * 100}%`, 14, 54);
                      doc.text(`Inflation-adjusted Target: ₹${existing.inflatedValue?.toLocaleString("en-IN")}`, 14, 62);
                      doc.text(`Investment Type: ${existing.investmentType}`, 14, 70);
                      doc.text(`Monthly SIP / Lumpsum: ₹${(existing.investmentType === "sip" ? existing.monthlySip : existing.lumpsumAmount)?.toLocaleString("en-IN")}`, 14, 78);
                      doc.text("Asset Allocation:", 14, 90);
                      let y = 98;
                      if (existing.portfolio) {
                        Object.entries(existing.portfolio).forEach(([asset, weight]) => {
                          doc.text(`- ${asset}: ${(Number(weight) * 100).toFixed(1)}%`, 18, y);
                          y += 8;
                        });
                      }
                      doc.text("Progress till date:", 14, y + 6);
                      doc.text(`Contributed: ₹${(existing.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0).toLocaleString("en-IN")}`, 18, y + 14);
                      doc.save(`goal-report-${existing.id}.pdf`);
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

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Calculator, TrendingUp, PiggyBank, Landmark, Coins, Shield, AlertTriangle, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const InvestmentPlanner = () => {
  const [goalType, setGoalType] = useState("");
  const [goalAmount, setGoalAmount] = useState("");
  const [targetYear, setTargetYear] = useState("");
  const [riskAppetite, setRiskAppetite] = useState("");
  const [showResults, setShowResults] = useState(false);

  // Asset-specific inflation rates (historical averages)
  const inflationRates: Record<string, number> = {
    car: 0.05, // 5%
    house: 0.08, // 8%
    education: 0.10, // 10%
    retirement: 0.06, // 6%
    gold: 0.07, // 7%
    other: 0.06, // 6%
  };

  // Risk-based investment options
  const getRiskBasedOptions = (risk: string) => {
    if (risk === "low") {
      return [
        {
          name: "Fixed Deposit",
          icon: Landmark,
          returns: 7,
          returnRange: "6-8%",
          risk: "Low",
          description: "Safe and guaranteed returns",
          color: "success",
        },
        {
          name: "Debt Mutual Funds",
          icon: PiggyBank,
          returns: 7.5,
          returnRange: "7-8%",
          risk: "Low",
          description: "Stable income with low volatility",
          color: "success",
        },
      ];
    } else if (risk === "medium") {
      return [
        {
          name: "SIP (Balanced Funds)",
          icon: TrendingUp,
          returns: 12,
          returnRange: "10-14%",
          risk: "Medium",
          description: "Mix of equity and debt for balanced growth",
          color: "primary",
        },
        {
          name: "Index Funds",
          icon: TrendingUp,
          returns: 11,
          returnRange: "10-12%",
          risk: "Medium",
          description: "Market-linked diversified returns",
          color: "primary",
        },
      ];
    } else {
      return [
        {
          name: "Equity Stocks",
          icon: TrendingUp,
          returns: 18,
          returnRange: "15-22%",
          risk: "High",
          description: "High growth potential with volatility",
          color: "destructive",
        },
        {
          name: "Equity Mutual Funds",
          icon: Coins,
          returns: 16,
          returnRange: "14-18%",
          risk: "High",
          description: "Actively managed high-return portfolio",
          color: "destructive",
        },
      ];
    }
  };

  const calculateInvestmentPlan = () => {
    const currentAmount = parseFloat(goalAmount);
    const currentYear = new Date().getFullYear();
    const years = parseInt(targetYear) - currentYear;
    
    // Get inflation rate based on goal type
    const inflationRate = inflationRates[goalType] || 0.06;
    
    // Calculate future value with inflation: FV = PV × (1 + r)^n
    const futureValue = currentAmount * Math.pow(1 + inflationRate, years);
    
    return { futureValue, inflationRate, years };
  };

  const calculateMonthlyInvestment = (futureValue: number, years: number, annualReturn: number) => {
    const monthlyRate = annualReturn / 12 / 100;
    const months = years * 12;
    
    // PMT formula for monthly investment: FV × r / ((1 + r)^n - 1)
    const monthlyInvestment = (futureValue * monthlyRate) / (Math.pow(1 + monthlyRate, months) - 1);
    
    return monthlyInvestment;
  };

  const handleCalculate = () => {
    if (goalAmount && targetYear && goalType && riskAppetite) {
      setShowResults(true);
    }
  };

  const results = showResults ? calculateInvestmentPlan() : null;
  const investmentOptions = showResults && riskAppetite ? getRiskBasedOptions(riskAppetite) : [];


  return (
    <div className="min-h-screen bg-background">
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
                <Label htmlFor="goal">Goal Description</Label>
                <Select value={goalType} onValueChange={setGoalType}>
                  <SelectTrigger id="goal">
                    <SelectValue placeholder="Select your financial goal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="car">Buy a Car (5% inflation)</SelectItem>
                    <SelectItem value="house">Buy a House (8% inflation)</SelectItem>
                    <SelectItem value="education">Child's Education (10% inflation)</SelectItem>
                    <SelectItem value="retirement">Retirement Fund (6% inflation)</SelectItem>
                    <SelectItem value="gold">Gold Investment (7% inflation)</SelectItem>
                    <SelectItem value="other">Other (6% inflation)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount">Current Cost of Goal (₹)</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="e.g., 1000000"
                  value={goalAmount}
                  onChange={(e) => setGoalAmount(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="year">Target Year</Label>
                <Input
                  id="year"
                  type="number"
                  placeholder="e.g., 2030"
                  value={targetYear}
                  onChange={(e) => setTargetYear(e.target.value)}
                  min={new Date().getFullYear() + 1}
                />
              </div>

              <div className="space-y-3">
                <Label>Risk Appetite</Label>
                <RadioGroup value={riskAppetite} onValueChange={setRiskAppetite}>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="low" id="low" />
                    <Label htmlFor="low" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Shield className="h-4 w-4 text-success" />
                      <div>
                        <div className="font-medium">Low Risk</div>
                        <div className="text-xs text-muted-foreground">FD, Bonds, Debt Funds (6-8% returns)</div>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="medium" id="medium" />
                    <Label htmlFor="medium" className="flex items-center gap-2 cursor-pointer flex-1">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <div>
                        <div className="font-medium">Medium Risk</div>
                        <div className="text-xs text-muted-foreground">Balanced Funds, Index Funds (10-14% returns)</div>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
                    <RadioGroupItem value="high" id="high" />
                    <Label htmlFor="high" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Zap className="h-4 w-4 text-destructive" />
                      <div>
                        <div className="font-medium">High Risk</div>
                        <div className="text-xs text-muted-foreground">Equity Stocks, Equity Funds (15-22% returns)</div>
                      </div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <Button 
                onClick={handleCalculate} 
                className="w-full" 
                size="lg"
                disabled={!goalAmount || !targetYear || !goalType || !riskAppetite}
              >
                Calculate Investment Plan
              </Button>

              {showResults && results && (
                <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
                  <CardContent className="pt-6 space-y-4">
                    <div className="text-center space-y-2">
                      <p className="text-sm text-muted-foreground">Current Value</p>
                      <p className="text-2xl font-bold text-foreground">₹{parseFloat(goalAmount).toLocaleString('en-IN')}</p>
                    </div>
                    <div className="text-center space-y-2">
                      <p className="text-sm text-muted-foreground">Predicted Future Value ({results.years} years)</p>
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

            {showResults && results && investmentOptions.map((option, index) => {
              const Icon = option.icon;
              const monthlyAmount = calculateMonthlyInvestment(results.futureValue, results.years, option.returns);
              const totalInvested = monthlyAmount * results.years * 12;
              const returns = results.futureValue - totalInvested;
              const returnPercentage = (returns / totalInvested) * 100;

              return (
                <Card key={index} className="hover:shadow-lg transition-shadow border-2">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className="h-5 w-5 text-primary" />
                        <CardTitle className="text-lg">{option.name}</CardTitle>
                      </div>
                      <Badge variant={option.risk === "Low" ? "secondary" : option.risk === "Medium" ? "default" : "destructive"}>
                        {option.risk} Risk
                      </Badge>
                    </div>
                    <CardDescription>{option.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Expected Returns</p>
                        <p className="text-lg font-bold text-success">{option.returnRange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Monthly Investment Required</p>
                        <p className="text-lg font-bold text-primary">
                          ₹{monthlyAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                        </p>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-accent/20 rounded-lg space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Total to Invest</span>
                        <span className="font-semibold">₹{totalInvested.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Expected Returns</span>
                        <span className="font-semibold text-success">₹{returns.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Total Return</span>
                        <span className="font-semibold text-success">+{returnPercentage.toFixed(1)}%</span>
                      </div>
                    </div>

                    <Button variant="outline" className="w-full">
                      Choose this plan
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestmentPlanner;

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calculator, TrendingUp, PiggyBank, Landmark, Coins } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const InvestmentPlanner = () => {
  const [goalAmount, setGoalAmount] = useState("");
  const [targetYear, setTargetYear] = useState("");
  const [showResults, setShowResults] = useState(false);

  const handleCalculate = () => {
    if (goalAmount && targetYear) {
      setShowResults(true);
    }
  };

  const investmentOptions = [
    {
      name: "Fixed Deposit",
      icon: Landmark,
      returns: "6-7%",
      risk: "Low",
      monthlyInvestment: "₹12,500",
      description: "Safe and guaranteed returns",
      color: "success",
    },
    {
      name: "SIP (Mutual Funds)",
      icon: TrendingUp,
      returns: "12-15%",
      risk: "Medium",
      monthlyInvestment: "₹8,500",
      description: "Market-linked equity returns",
      color: "primary",
    },
    {
      name: "Gold Investment",
      icon: Coins,
      returns: "8-10%",
      risk: "Low-Medium",
      monthlyInvestment: "₹10,000",
      description: "Inflation hedge with stability",
      color: "accent",
    },
    {
      name: "Equity Stocks",
      icon: TrendingUp,
      returns: "15-20%",
      risk: "High",
      monthlyInvestment: "₹6,500",
      description: "High returns with volatility",
      color: "destructive",
    },
  ];

  const futureValue = goalAmount ? (parseFloat(goalAmount) * 1.52).toFixed(2) : "0";

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
                <Select>
                  <SelectTrigger id="goal">
                    <SelectValue placeholder="Select your goal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="car">Buy a Car</SelectItem>
                    <SelectItem value="house">Buy a House</SelectItem>
                    <SelectItem value="education">Child's Education</SelectItem>
                    <SelectItem value="retirement">Retirement Fund</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount">Current Value (₹)</Label>
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
                />
              </div>

              <Button onClick={handleCalculate} className="w-full" size="lg">
                Calculate Investment Plan
              </Button>

              {showResults && (
                <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
                  <CardContent className="pt-6">
                    <div className="text-center space-y-2">
                      <p className="text-sm text-muted-foreground">Estimated Future Value</p>
                      <p className="text-3xl font-bold text-primary">₹{futureValue}L</p>
                      <Badge variant="secondary">+52% due to inflation</Badge>
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>

          {/* Investment Recommendations */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">Recommended Investment Options</h2>
            {investmentOptions.map((option, index) => {
              const Icon = option.icon;
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow">
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
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Expected Returns</p>
                        <p className="text-lg font-bold text-success">{option.returns}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Monthly Investment</p>
                        <p className="text-lg font-bold text-primary">{option.monthlyInvestment}</p>
                      </div>
                    </div>
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

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, PieChart, Target, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const Portfolio = () => {
  const assetAllocation = [
    { name: "Equity", percentage: 40, color: "bg-chart-1", value: "₹4L" },
    { name: "Fixed Deposits", percentage: 30, color: "bg-chart-2", value: "₹3L" },
    { name: "Gold", percentage: 20, color: "bg-chart-3", value: "₹2L" },
    { name: "Bonds", percentage: 10, color: "bg-chart-4", value: "₹1L" },
  ];

  const portfolioStats = [
    { label: "Total Portfolio Value", value: "₹10,00,000", icon: PieChart },
    { label: "Expected Annual Returns", value: "12.5%", icon: TrendingUp },
    { label: "Risk Score", value: "Medium", icon: Shield },
    { label: "Goals on Track", value: "3/4", icon: Target },
  ];

  const goalProgress = [
    { goal: "Car Purchase", progress: 45, target: "₹15L", current: "₹6.75L", year: 2030 },
    { goal: "House Down Payment", progress: 25, target: "₹85L", current: "₹21.25L", year: 2035 },
    { goal: "Gold Investment", progress: 60, target: "500g", current: "300g", year: 2028 },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Portfolio Insights</h1>
          <p className="text-muted-foreground">Track your investments and goal progress</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {portfolioStats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index}>
                <CardHeader className="pb-2">
                  <CardDescription className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {stat.label}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-primary">{stat.value}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Asset Allocation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-primary" />
                Asset Allocation
              </CardTitle>
              <CardDescription>How your portfolio is distributed</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {assetAllocation.map((asset, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${asset.color}`} />
                      <span className="font-medium">{asset.name}</span>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">{asset.value}</p>
                      <p className="text-xs text-muted-foreground">{asset.percentage}%</p>
                    </div>
                  </div>
                  <Progress value={asset.percentage} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Risk vs Return */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Risk vs Return Analysis
              </CardTitle>
              <CardDescription>Your portfolio's risk-return profile</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Current Risk Level</span>
                  <Badge variant="secondary">Medium</Badge>
                </div>
                <Progress value={60} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Expected Annual Return</span>
                  <span className="font-bold text-success">12.5%</span>
                </div>
                <Progress value={75} className="h-2" />
              </div>

              <div className="pt-4 border-t space-y-2">
                <h4 className="font-semibold text-sm">Recommendations</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-success">•</span>
                    Your portfolio is well-balanced for medium-term goals
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent">•</span>
                    Consider increasing equity allocation for higher returns
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary">•</span>
                    Gold investment provides good inflation protection
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Inflation-Adjusted Goal Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Inflation-Adjusted Goal Progress
            </CardTitle>
            <CardDescription>How your goals are progressing considering inflation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {goalProgress.map((goal, index) => (
                <div key={index} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">{goal.goal}</h4>
                      <p className="text-sm text-muted-foreground">Target: {goal.year}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">{goal.current}</p>
                      <p className="text-xs text-muted-foreground">of {goal.target}</p>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Progress value={goal.progress} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{goal.progress}% Complete</span>
                      <Badge variant="outline" className="text-xs">
                        On Track
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Portfolio;

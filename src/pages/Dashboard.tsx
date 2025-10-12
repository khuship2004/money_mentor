import { TrendingUp, TrendingDown, Car, Home, Coins, Target } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

const Dashboard = () => {
  const inflationRate = 6.5;
  
  const goals = [
    {
      id: 1,
      name: "Car",
      icon: Car,
      currentValue: "₹10L",
      targetValue: "₹15L",
      targetYear: 2030,
      progress: 45,
      monthlyInvestment: "₹8,500",
    },
    {
      id: 2,
      name: "House",
      icon: Home,
      currentValue: "₹50L",
      targetValue: "₹85L",
      targetYear: 2035,
      progress: 25,
      monthlyInvestment: "₹35,000",
    },
    {
      id: 3,
      name: "Gold",
      icon: Coins,
      currentValue: "100g",
      targetValue: "500g",
      targetYear: 2028,
      progress: 60,
      monthlyInvestment: "₹5,000",
    },
  ];

  const predictions = [
    { item: "Car (₹10L today)", predicted: "₹15.2L", year: 2030, change: 52 },
    { item: "House (₹50L today)", predicted: "₹85.3L", year: 2035, change: 71 },
    { item: "Gold (100g)", predicted: "₹7.2L", year: 2030, change: 44 },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Track your financial goals</p>
          </div>
          <Badge variant="outline" className="text-lg px-4 py-2">
            Inflation: {inflationRate}%
            {inflationRate > 5 ? (
              <TrendingUp className="ml-2 h-4 w-4 text-destructive" />
            ) : (
              <TrendingDown className="ml-2 h-4 w-4 text-success" />
            )}
          </Badge>
        </div>

        {/* Inflation Alert Card */}
        <Card className="border-accent/50 bg-gradient-to-br from-card to-accent/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-accent" />
              Current Inflation Rate
            </CardTitle>
            <CardDescription>India's current inflation rate and its impact</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-accent mb-2">{inflationRate}%</div>
            <p className="text-sm text-muted-foreground">
              Your purchasing power decreases by approximately ₹{inflationRate * 100} for every ₹10,000 annually
            </p>
          </CardContent>
        </Card>

        {/* Price Predictions */}
        <div>
          <h2 className="text-xl font-semibold mb-4 text-foreground">Predicted Future Prices</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {predictions.map((pred, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-base">{pred.item}</CardTitle>
                  <CardDescription>Expected in {pred.year}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary mb-1">{pred.predicted}</div>
                  <Badge variant="secondary" className="text-xs">
                    +{pred.change}% increase
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Goals Tracker */}
        <div>
          <h2 className="text-xl font-semibold mb-4 text-foreground">Your Financial Goals</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map((goal) => {
              const Icon = goal.icon;
              return (
                <Card key={goal.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Icon className="h-5 w-5 text-primary" />
                        {goal.name}
                      </CardTitle>
                      <Target className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <CardDescription>Target: {goal.targetYear}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Current</span>
                      <span className="font-semibold">{goal.currentValue}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Target</span>
                      <span className="font-semibold">{goal.targetValue}</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Progress</span>
                        <span>{goal.progress}%</span>
                      </div>
                      <Progress value={goal.progress} className="h-2" />
                    </div>
                    <div className="pt-2 border-t">
                      <div className="text-xs text-muted-foreground">Monthly Investment</div>
                      <div className="text-lg font-bold text-primary">{goal.monthlyInvestment}</div>
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

export default Dashboard;

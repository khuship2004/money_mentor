import { TrendingUp, TrendingDown, Target, ArrowRight, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useGoals } from "@/contexts/GoalsContext";
import { useNavigate } from "react-router-dom";
import { useMemo } from "react";

const Dashboard = () => {
  const { goals } = useGoals();
  const navigate = useNavigate();
  const avgInflationRate = 6.5;
  const avgLiveInflation = useMemo(() => {
    if (!goals.length) return avgInflationRate;
    const average = goals.reduce((sum, g) => sum + (g.inflationRate || 0), 0) / goals.length;
    return Number((average * 100).toFixed(1));
  }, [goals]);

  const totalGoalAmount = goals.reduce((sum, g) => sum + g.goalAmount, 0);
  const totalInflatedValue = goals.reduce((sum, g) => sum + (g.inflatedValue || 0), 0);
  const totalInflationImpact = totalInflatedValue - totalGoalAmount;
  const onTrackGoals = goals.filter(g => (g.monthlySip || g.lumpsumAmount || 0) > 0).length;

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground">Track your financial goals and portfolio</p>
          </div>
          <Badge variant="outline" className="text-lg px-4 py-2">
            Inflation: {avgInflationRate}%
            {avgInflationRate > 5 ? (
              <TrendingUp className="ml-2 h-4 w-4 text-destructive" />
            ) : (
              <TrendingDown className="ml-2 h-4 w-4 text-success" />
            )}
          </Badge>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Goals</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{goals.length}</p>
              <p className="text-xs text-muted-foreground mt-1">Total financial goals</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Goal Amount</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">₹{totalGoalAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
              <p className="text-xs text-muted-foreground mt-1">Current value</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Inflation Impact</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-primary">₹{totalInflationImpact.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
              <p className="text-xs text-muted-foreground mt-1">Additional cost due to inflation</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">On Track Goals</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-success">{onTrackGoals}/{goals.length}</p>
              <p className="text-xs text-muted-foreground mt-1">With active investments</p>
            </CardContent>
          </Card>
        </div>

        {/* Inflation Rate Cards - clickable → navigate to goal page */}
        <Card>
          <CardHeader>
            <CardTitle>Inflation-Specific Projections</CardTitle>
            <CardDescription>Sector-wise inflation rates and their impact on your goals</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { key: "gold", label: "Gold Inflation", rate: 7.0, icon: "🪙", description: "Historical gold price inflation rate" },
                { key: "vehicle", label: "Vehicle / Consumer Goods", rate: 5.0, icon: "🚗", description: "Average vehicle & consumer price inflation" },
                { key: "real-estate", label: "Real Estate", rate: 8.0, icon: "🏠", description: "Property & housing inflation rate" },
              ].map((card) => {
                const matchingGoal = goals.find(g =>
                  (card.key === "gold" && g.goalType === "gold") ||
                  (card.key === "vehicle" && g.goalType === "car") ||
                  (card.key === "real-estate" && g.goalType === "house")
                );
                return (
                  <Card
                    key={card.key}
                    className={`border hover:shadow-md transition-all ${matchingGoal ? "cursor-pointer hover:border-primary/50" : ""}`}
                    onClick={() => matchingGoal && navigate(`/goals/${matchingGoal.id}`)}
                  >
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-semibold flex items-center gap-2">
                        <span className="text-lg">{card.icon}</span>
                        {card.label}
                      </CardTitle>
                      <CardDescription>{card.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-2xl font-bold text-primary">{card.rate.toFixed(1)}%</p>
                      {matchingGoal ? (
                        <div className="space-y-1">
                          <p className="text-xs text-muted-foreground">
                            Goal: ₹{matchingGoal.goalAmount.toLocaleString("en-IN")} → ₹{(matchingGoal.inflatedValue || matchingGoal.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                          </p>
                          <p className="text-xs text-muted-foreground italic">This value reflects inflation-adjusted pricing based on historical trends</p>
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground">Portfolio-wide inflation: {avgLiveInflation}%</p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {goals.length === 0 ? (
          <Card className="border-2 border-dashed">
            <CardContent className="pt-12 pb-12 text-center">
              <Target className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-xl font-semibold text-foreground mb-2">No Goals Created Yet</h3>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">Start building your financial future by creating your first goal.</p>
              <Button size="lg" onClick={() => navigate('/planner')}>
                Create Your First Goal
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Goals Tracker */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-foreground">Your Financial Goals</h2>
                <Button variant="outline" onClick={() => navigate('/portfolio')}>
                  View Detailed Portfolio
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {goals.map((goal, index) => {
                  const inflatedValue = goal.inflatedValue || goal.goalAmount;
                  const inflation = ((inflatedValue - goal.goalAmount) / goal.goalAmount) * 100;
                  const statusBadge = goal.optimizationStatus === "optimal" ? "Optimized" : "Rule-Based";

                  return (
                    <Card
                      key={goal.id || index}
                      className="hover:shadow-lg transition-shadow hover:border-primary/50 cursor-pointer"
                      onClick={() => navigate(`/goals/${goal.id}`)}
                    >
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center gap-2 capitalize">
                            <Target className="h-5 w-5 text-primary" />
                            {goal.goalName || goal.goalType}
                          </CardTitle>
                          <Badge variant="outline" className="text-xs">{statusBadge}</Badge>
                        </div>
                        <CardDescription>Target: {goal.targetMonth ? `${goal.targetMonth}/${goal.targetYear}` : goal.targetYear} ({goal.years} years)</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Current Value</span>
                          <span className="font-semibold">₹{goal.goalAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Future Value</span>
                          <span className="font-semibold text-primary">₹{inflatedValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Inflation Impact</span>
                          <span className="font-semibold">+{inflation.toFixed(1)}%</span>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-xs text-muted-foreground">
                            <span>Inflation</span>
                            <span>{inflation.toFixed(1)}%</span>
                          </div>
                          <Progress value={Math.min(inflation, 100)} className="h-2" />
                        </div>
                        <div className="pt-2 border-t">
                          <div className="text-xs text-muted-foreground mb-1">
                            {goal.investmentType === "sip" ? "Monthly SIP" : "Lumpsum"}
                          </div>
                          <div className="text-lg font-bold text-primary">
                            ₹{(goal.investmentType === "sip" ? (goal.monthlySip || 0) : (goal.lumpsumAmount || 0)).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

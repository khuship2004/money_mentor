import { TrendingUp, TrendingDown, Target, ArrowRight, BarChart3, MapPin, GraduationCap, Info } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useGoals } from "@/contexts/GoalsContext";
import { useNavigate } from "react-router-dom";
import { useMemo, useState, useEffect } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface InflationDisplayData {
  rate: number;
  description: string;
  period: string;
  cagr?: number;
  geometric_mean?: number;
  regression_rate?: number;
  regression_r_squared?: number;
  weighted_average?: number;
  method_used?: string;
  data_points_used?: string | number;
  city_wise?: Record<string, number>;
  categories?: Record<string, any>;
}

const API_BASE_URL = "http://localhost:8000";

const formatYears = (years?: number) => {
  if (!years) return "0";
  const rounded = Math.round(years * 2) / 2;
  return rounded % 1 === 0 ? rounded.toString() : rounded.toFixed(1);
};

const Dashboard = () => {
  const { goals } = useGoals();
  const navigate = useNavigate();
  
  // State for inflation rates from backend models
  const [inflationData, setInflationData] = useState<Record<string, InflationDisplayData>>({
    gold: { rate: 14.03, description: "Gold price inflation based on historical trends", period: "2014-2026" },
    house: { rate: 7.26, description: "Housing Price Index based inflation", period: "2010-2025" },
    car: { rate: 5.5, description: "Vehicle and consumer goods price inflation", period: "2010-2024" },
    education: { rate: 11.5, description: "Children education cost inflation", period: "2005-2025" }
  });

  // Fetch inflation rates from backend on component mount
  useEffect(() => {
    const fetchInflationRates = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/inflation-rates-simple`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === "success" && data.display) {
            setInflationData(data.display);
          }
        }
      } catch {
        // Using default inflation rates when backend is unavailable
      }
    };
    fetchInflationRates();
  }, []);

  const avgInflationRate = useMemo(() => {
    const rates = Object.values(inflationData).map(d => d.rate);
    return rates.length > 0 ? Number((rates.reduce((a, b) => a + b, 0) / rates.length).toFixed(1)) : 6.5;
  }, [inflationData]);

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
          <Badge variant="outline" className="text-xl px-4 py-2 font-semibold">
            Inflation: {avgInflationRate}%
            {avgInflationRate > 5 ? (
              <TrendingUp className="ml-2 h-5 w-5 text-amber-700" />
            ) : (
              <TrendingDown className="ml-2 h-5 w-5 text-amber-700" />
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
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              Inflation-Specific Projections
            </CardTitle>
            <CardDescription>Sector-wise inflation rates from ML models using multiple calculation methods</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { 
                  key: "gold", 
                  goalKey: "gold",
                  label: "Gold Inflation", 
                  icon: "🪙", 
                  dataKey: "gold" as const
                },
                { 
                  key: "vehicle", 
                  goalKey: "car",
                  label: "Vehicle / Consumer Goods", 
                  icon: "🚗", 
                  dataKey: "car" as const
                },
                { 
                  key: "real-estate", 
                  goalKey: "house",
                  label: "Real Estate", 
                  icon: "🏠", 
                  dataKey: "house" as const
                },
                { 
                  key: "education", 
                  goalKey: "education",
                  label: "Children Education", 
                  icon: "🎓", 
                  dataKey: "education" as const
                },
              ].map((card) => {
                const rateData = inflationData[card.dataKey];
                const matchingGoal = goals.find(g => g.goalType === card.goalKey);
                const hasDetailedData = rateData?.cagr !== undefined || rateData?.city_wise || rateData?.categories;
                
                return (
                  <Card
                    key={card.key}
                    className={`border hover:shadow-md transition-all ${matchingGoal ? "cursor-pointer hover:border-primary/50" : ""}`}
                  >
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-semibold flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{card.icon}</span>
                          {card.label}
                        </div>
                        {hasDetailedData && (
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={(e) => e.stopPropagation()}>
                                <Info className="h-4 w-4 text-muted-foreground" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-md">
                              <DialogHeader>
                                <DialogTitle className="flex items-center gap-2">
                                  <span className="text-xl">{card.icon}</span>
                                  {card.label} - Detailed Analysis
                                </DialogTitle>
                                <DialogDescription>{rateData?.description}</DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4">
                                {/* Calculation Methods */}
                                <div className="space-y-2">
                                  <h4 className="font-semibold text-sm flex items-center gap-2">
                                    <BarChart3 className="h-4 w-4" />
                                    Calculation Methods
                                  </h4>
                                  <div className="grid grid-cols-2 gap-2 text-sm">
                                    {rateData?.cagr !== undefined && (
                                      <div className="p-2 bg-muted rounded-md">
                                        <p className="text-xs text-muted-foreground">CAGR</p>
                                        <p className="font-semibold">{rateData.cagr?.toFixed(2)}%</p>
                                      </div>
                                    )}
                                    {rateData?.geometric_mean !== undefined && (
                                      <div className="p-2 bg-muted rounded-md">
                                        <p className="text-xs text-muted-foreground">Geometric Mean</p>
                                        <p className="font-semibold">{rateData.geometric_mean?.toFixed(2)}%</p>
                                      </div>
                                    )}
                                    {rateData?.regression_rate !== undefined && (
                                      <div className="p-2 bg-muted rounded-md">
                                        <p className="text-xs text-muted-foreground">Regression Rate</p>
                                        <p className="font-semibold">{rateData.regression_rate?.toFixed(2)}%</p>
                                      </div>
                                    )}
                                    {rateData?.weighted_average !== undefined && (
                                      <div className="p-2 bg-muted rounded-md">
                                        <p className="text-xs text-muted-foreground">Weighted Avg</p>
                                        <p className="font-semibold">{rateData.weighted_average?.toFixed(2)}%</p>
                                      </div>
                                    )}
                                  </div>

                                </div>

                                {/* City-wise data for Real Estate */}
                                {rateData?.city_wise && Object.keys(rateData.city_wise).length > 0 && (
                                  <div className="space-y-2">
                                    <h4 className="font-semibold text-sm flex items-center gap-2">
                                      <MapPin className="h-4 w-4" />
                                      City-wise Rates
                                    </h4>
                                    <div className="grid grid-cols-2 gap-2 text-sm max-h-48 overflow-y-auto">
                                      {Object.entries(rateData.city_wise)
                                        .sort(([, a], [, b]) => b - a)
                                        .map(([city, rate]) => (
                                          <div key={city} className="flex justify-between p-2 bg-muted rounded-md">
                                            <span className="text-muted-foreground">{city}</span>
                                            <span className="font-semibold">{rate.toFixed(1)}%</span>
                                          </div>
                                        ))}
                                    </div>
                                  </div>
                                )}

                                {/* Education categories */}
                                {rateData?.categories && (
                                  <div className="space-y-2">
                                    <h4 className="font-semibold text-sm flex items-center gap-2">
                                      <GraduationCap className="h-4 w-4" />
                                      Education Categories
                                    </h4>
                                    <div className="space-y-3 text-sm max-h-48 overflow-y-auto">
                                      {Object.entries(rateData.categories).map(([category, data]: [string, any]) => (
                                        <div key={category} className="p-2 bg-muted rounded-md">
                                          <p className="font-semibold capitalize mb-1">{category.replace('_', ' ')}</p>
                                          {typeof data === 'object' ? (
                                            <div className="grid grid-cols-2 gap-1 text-xs">
                                              {Object.entries(data).map(([key, value]) => (
                                                <div key={key} className="flex justify-between">
                                                  <span className="text-muted-foreground capitalize">{key.replace('_', ' ')}</span>
                                                  <span>{typeof value === 'number' ? `${value.toFixed(1)}%` : value}</span>
                                                </div>
                                              ))}
                                            </div>
                                          ) : (
                                            <span>{data}%</span>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                <div className="text-xs text-muted-foreground pt-2 border-t">
                                  {rateData?.method_used && <p>Primary Method: {rateData.method_used}</p>}
                                  {rateData?.data_points_used && <p>Data Points: {rateData.data_points_used}</p>}
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        )}
                      </CardTitle>
                      <CardDescription className="text-xs">{rateData?.description || "Inflation rate"}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2" onClick={() => matchingGoal && navigate(`/goals/${matchingGoal.id}`)}>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <div className="flex items-baseline gap-2 cursor-help">
                              <p className="text-2xl font-bold text-primary">{rateData?.rate?.toFixed(1) || "N/A"}%</p>
                              <span className="text-xs text-muted-foreground">{rateData?.method_used || "CAGR"}</span>
                            </div>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p className="text-xs">Best estimate using {rateData?.method_used || "CAGR"}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                      

                      
                      {matchingGoal ? (
                        <div className="space-y-1 pt-2 border-t">
                          <p className="text-xs text-muted-foreground">
                            Goal: ₹{matchingGoal.goalAmount.toLocaleString("en-IN")} → ₹{(matchingGoal.inflatedValue || matchingGoal.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                          </p>
                          <p className="text-xs text-muted-foreground italic">Based on ML model predictions</p>
                        </div>
                      ) : (
                        <p className="text-xs text-muted-foreground pt-2 border-t">No active goal for this category</p>
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
                        <CardDescription>Target: {goal.targetMonth ? `${goal.targetMonth}/${goal.targetYear}` : goal.targetYear} ({formatYears(goal.years)} years)</CardDescription>
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

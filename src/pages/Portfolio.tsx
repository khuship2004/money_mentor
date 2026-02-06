import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { PieChart, Target, Shield, ArrowRight, Pencil, Trash2, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useGoals } from "@/contexts/GoalsContext";
import { useNavigate } from "react-router-dom";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

const Portfolio = () => {
  const { goals, removeGoal, updateGoal } = useGoals();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [deleteGoalId, setDeleteGoalId] = useState<string | null>(null);
  const [editGoalId, setEditGoalId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState({ amount: "", year: "", month: "", risk: "", sipStartDate: "" });
  const [sipPromptGoalId, setSipPromptGoalId] = useState<string | null>(null);
  const [inflationPopup, setInflationPopup] = useState<{ goalId: string; updatedValue: number; delta: number; accumulated: number } | null>(null);

  const totalPortfolioValue = goals.reduce((sum, goal) => sum + (goal.lumpsumAmount || 0), 0);
  const totalInflationImpact = goals.reduce((sum, g) => sum + ((g.inflatedValue || 0) - g.goalAmount), 0);

  const goalStats = [
    { label: "Total Portfolio Value", value: `₹${totalPortfolioValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, icon: PieChart },
    { label: "Active Goals", value: goals.length.toString(), icon: Target },
    { label: "Total Inflation Impact", value: `₹${totalInflationImpact.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, icon: Shield },
  ];

  const monthKey = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;

  useEffect(() => {
    if (!goals.length) return;

    const now = new Date();
    let updatedGoalId: string | null = null;
    let updatedValue = 0;
    let delta = 0;

    goals.forEach((goal) => {
      if (!goal.inflatedValue) return;
      const lastUpdate = goal.lastInflationUpdate ? new Date(goal.lastInflationUpdate) : new Date();
      const inflationRate = goal.inflationRate || 0.06;

      if (goal.goalType === "gold") {
        const days = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60 * 24));
        if (days >= 1) {
          const dailyRate = inflationRate / 365;
          const newValue = goal.inflatedValue * Math.pow(1 + dailyRate, days);
          updateGoal(goal.id, { inflatedValue: newValue, lastInflationUpdate: now.toISOString() });
          updatedGoalId = goal.id;
          updatedValue = newValue;
        }
      } else {
        const months = (now.getFullYear() - lastUpdate.getFullYear()) * 12 + (now.getMonth() - lastUpdate.getMonth());
        if (months >= 1) {
          const monthlyRate = inflationRate / 12;
          const newValue = goal.inflatedValue * Math.pow(1 + monthlyRate, months);
          updateGoal(goal.id, { inflatedValue: newValue, lastInflationUpdate: now.toISOString() });
          updatedGoalId = goal.id;
          updatedValue = newValue;
        }
      }
    });

    if (updatedGoalId) {
      const updatedGoal = goals.find((g) => g.id === updatedGoalId);
      const contributed = (updatedGoal?.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
      delta = contributed - updatedValue;
      setInflationPopup({ goalId: updatedGoalId, updatedValue, delta, accumulated: contributed });
    }
  }, [goals, updateGoal]);

  useEffect(() => {
    const now = new Date();
    const currentMonthKey = monthKey(now);
    const promptGoal = goals.find((goal) => {
      if (goal.investmentType !== "sip" || !goal.sipStartDate) return false;
      const start = new Date(goal.sipStartDate);
      if (start > now) return false;
      const hasPayment = (goal.sipPayments || []).some((p) => p.month === currentMonthKey);
      return !hasPayment;
    });
    if (promptGoal) setSipPromptGoalId(promptGoal.id);
  }, [goals]);

  const ongoingGoals = useMemo(() => goals.filter((goal) => {
    if (!goal.isLocked && goal.status !== "ongoing") return false;
    const contributed = (goal.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
    const completed = goal.inflatedValue ? contributed >= goal.inflatedValue : false;
    return !completed;
  }), [goals]);

  const completedGoals = useMemo(() => goals.filter((goal) => {
    if (!goal.isLocked && goal.status !== "ongoing" && goal.status !== "completed") return false;
    const contributed = (goal.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
    const completed = goal.inflatedValue ? contributed >= goal.inflatedValue : false;
    return completed;
  }), [goals]);

  const editingGoal = editGoalId ? goals.find((g) => g.id === editGoalId) : null;

  const handleEditOpen = (goalId: string) => {
    const goal = goals.find((g) => g.id === goalId);
    if (!goal) return;
    if (goal.isLocked) {
      toast({
        title: "Goal locked",
        description: "This goal is locked once added to your portfolio.",
      });
      return;
    }
    setEditValues({
      amount: goal.goalAmount.toString(),
      year: goal.targetYear.toString(),
      month: goal.targetMonth ? goal.targetMonth.toString() : "",
      risk: goal.riskProfile,
      sipStartDate: goal.sipStartDate || "",
    });
    setEditGoalId(goalId);
  };

  const handleEditSave = () => {
    if (!editGoalId) return;
    const goal = goals.find((g) => g.id === editGoalId);
    if (!goal) return;
    updateGoal(editGoalId, {
      ...goal,
      goalAmount: parseFloat(editValues.amount),
      targetYear: parseInt(editValues.year),
      targetMonth: editValues.month ? parseInt(editValues.month) : goal.targetMonth,
      riskProfile: editValues.risk,
      sipStartDate: goal.investmentType === "sip" ? editValues.sipStartDate : goal.sipStartDate,
    });
    setEditGoalId(null);
  };

  const handleSipResponse = (paid: boolean) => {
    if (!sipPromptGoalId) return;
    const goal = goals.find((g) => g.id === sipPromptGoalId);
    if (!goal) return;
    const now = new Date();
    const currentMonthKey = monthKey(now);
    const payment = {
      month: currentMonthKey,
      amount: goal.monthlySip || 0,
      status: paid ? "paid" : "pending",
    } as const;
    const updatedPayments = [...(goal.sipPayments || []), payment];
    const updatedContributions = [...(goal.contributions || [])];
    if (paid) {
      updatedContributions.push({ date: now.toISOString(), amount: payment.amount, type: "sip", status: "paid" });
    }
    updateGoal(goal.id, { sipPayments: updatedPayments, contributions: updatedContributions });
    setSipPromptGoalId(null);
  };

  const handleDeleteConfirm = () => {
    if (!deleteGoalId) return;
    removeGoal(deleteGoalId);
    setDeleteGoalId(null);
  };

  if (!goals || goals.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Portfolio Insights</h1>
            <p className="text-muted-foreground">Track your investments and goal progress</p>
          </div>

          <Card className="border-2 border-dashed">
            <CardContent className="pt-12 pb-12 text-center">
              <Target className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-xl font-semibold text-foreground mb-2">No Goals Yet</h3>
              <p className="text-muted-foreground mb-6">Start by creating your first financial goal in the Investment Planner</p>
              <Button 
                size="lg"
                onClick={() => navigate('/planner')}
              >
                Go to Investment Planner
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Portfolio Insights</h1>
          <p className="text-muted-foreground">Track your investments and goal progress</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {goalStats.map((stat, index) => {
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

        {/* Inflation Impact */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Inflation Impact
            </CardTitle>
            <CardDescription>Initial estimate vs current inflation-adjusted value</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {goals.map((goal) => (
              <div key={goal.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-semibold">{goal.goalName || goal.goalType}</p>
                  <p className="text-xs text-muted-foreground">Initial: ₹{goal.goalAmount.toLocaleString("en-IN")}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">₹{(goal.inflatedValue || goal.goalAmount).toLocaleString("en-IN")}</p>
                  <p className="text-xs text-muted-foreground">Impact: ₹{(((goal.inflatedValue || goal.goalAmount) - goal.goalAmount)).toLocaleString("en-IN")}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Ongoing Goals */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Ongoing Goals
            </CardTitle>
            <CardDescription>Progress, inflation-adjusted value, and SIP status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {ongoingGoals.length === 0 ? (
              <p className="text-sm text-muted-foreground">No ongoing goals right now.</p>
            ) : ongoingGoals.map((goal) => {
              const contributed = (goal.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
              const progress = goal.inflatedValue ? Math.min((contributed / goal.inflatedValue) * 100, 100) : 0;
              const currentMonth = monthKey(new Date());
              const sipStatus = goal.investmentType === "sip"
                ? (goal.sipPayments || []).find((p) => p.month === currentMonth)?.status || "pending"
                : "n/a";

              return (
                <div key={goal.id} className="space-y-3 pb-6 border-b last:border-b-0 last:pb-0">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold">{goal.goalName || goal.goalType}</h4>
                        <Badge variant="outline" className="text-xs capitalize">{goal.riskProfile} risk</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        Target: {goal.targetMonth ? `${goal.targetMonth}/${goal.targetYear}` : goal.targetYear}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="icon" onClick={() => handleEditOpen(goal.id)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="icon" onClick={() => setDeleteGoalId(goal.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                      <Button onClick={() => navigate(`/goals/${goal.id}`)}>
                        View Details
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-3 bg-accent/10 rounded-lg">
                      <p className="text-xs text-muted-foreground">Inflation-adjusted value</p>
                      <p className="text-lg font-bold text-primary">₹{(goal.inflatedValue || goal.goalAmount).toLocaleString("en-IN")}</p>
                    </div>
                    <div className="p-3 bg-accent/10 rounded-lg">
                      <p className="text-xs text-muted-foreground">SIP Status</p>
                      <p className="text-lg font-bold capitalize">{sipStatus}</p>
                    </div>
                    <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                      <p className="text-xs text-muted-foreground">Monthly SIP / Lumpsum</p>
                      <p className="text-lg font-bold text-primary">₹{(goal.investmentType === "sip" ? goal.monthlySip : goal.lumpsumAmount)?.toLocaleString("en-IN")}</p>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <Progress value={progress} className="h-2" />
                    <p className="text-xs text-muted-foreground text-right">{Math.round(progress)}% Progress</p>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Completed Goals */}
        <Card>
          <CardHeader>
            <CardTitle>Completed Goals</CardTitle>
            <CardDescription>Full report for completed milestones</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {completedGoals.length === 0 ? (
              <p className="text-sm text-muted-foreground">No completed goals yet.</p>
            ) : (
              completedGoals.map((goal) => {
                const totalPaid = (goal.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
                const difference = totalPaid - (goal.inflatedValue || goal.goalAmount);

                return (
                  <div key={goal.id} className="space-y-3 pb-6 border-b last:border-b-0 last:pb-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold">{goal.goalName || goal.goalType}</h4>
                        <p className="text-xs text-muted-foreground">Completed at {goal.targetMonth ? `${goal.targetMonth}/${goal.targetYear}` : goal.targetYear}</p>
                      </div>
                      <Badge variant="secondary">Completed</Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div className="p-3 bg-accent/10 rounded-lg">
                        <p className="text-xs text-muted-foreground">Inflation-adjusted target</p>
                        <p className="text-lg font-bold">₹{(goal.inflatedValue || goal.goalAmount).toLocaleString("en-IN")}</p>
                      </div>
                      <div className="p-3 bg-accent/10 rounded-lg">
                        <p className="text-xs text-muted-foreground">Total contributions</p>
                        <p className="text-lg font-bold">₹{totalPaid.toLocaleString("en-IN")}</p>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                        <p className="text-xs text-muted-foreground">Final outcome</p>
                        <p className="text-lg font-bold">{difference >= 0 ? `Surplus ₹${difference.toLocaleString("en-IN")}` : `Shortfall ₹${Math.abs(difference).toLocaleString("en-IN")}`}</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-semibold text-muted-foreground mb-2">Month-wise contributions</p>
                      <div className="space-y-2">
                        {(goal.sipPayments || []).map((payment, idx) => (
                          <div key={`${payment.month}-${idx}`} className="flex items-center justify-between text-sm p-2 border rounded-lg">
                            <span>{payment.month}</span>
                            <span className="font-semibold">₹{payment.amount.toLocaleString("en-IN")}</span>
                            <Badge variant={payment.status === "paid" ? "default" : "secondary"}>{payment.status}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        {/* Action Button */}
        <div className="flex gap-2 justify-center">
          <Button 
            onClick={() => navigate('/planner', { state: { fromAddGoal: true } })}
          >
            Add Another Goal
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>

      <AlertDialog open={Boolean(deleteGoalId)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this goal?</AlertDialogTitle>
            <AlertDialogDescription>This action cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeleteGoalId(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={Boolean(editGoalId)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Goal</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Amount (₹)</Label>
              <Input value={editValues.amount} onChange={(e) => setEditValues({ ...editValues, amount: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>Target Month</Label>
                <Input value={editValues.month} onChange={(e) => setEditValues({ ...editValues, month: e.target.value })} placeholder="MM" />
              </div>
              <div className="space-y-2">
                <Label>Target Year</Label>
                <Input value={editValues.year} onChange={(e) => setEditValues({ ...editValues, year: e.target.value })} placeholder="YYYY" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Risk Level</Label>
              <Input value={editValues.risk} onChange={(e) => setEditValues({ ...editValues, risk: e.target.value })} placeholder="low / medium / high" />
            </div>
            {editingGoal?.investmentType === "sip" && (
              <div className="space-y-2">
                <Label>SIP Start Date</Label>
                <Input type="date" value={editValues.sipStartDate} onChange={(e) => setEditValues({ ...editValues, sipStartDate: e.target.value })} />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditGoalId(null)}>Cancel</Button>
            <Button onClick={handleEditSave}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={Boolean(sipPromptGoalId)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Monthly SIP Reminder</AlertDialogTitle>
            <AlertDialogDescription>Has your SIP for this month been deducted?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => handleSipResponse(false)}>No</AlertDialogCancel>
            <AlertDialogAction onClick={() => handleSipResponse(true)}>Yes</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={Boolean(inflationPopup)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Inflation Update</AlertDialogTitle>
            <AlertDialogDescription>
              {inflationPopup && (
                <div className="space-y-2">
                  <p>Current accumulated amount: ₹{inflationPopup.accumulated.toLocaleString("en-IN")}</p>
                  <p>Updated inflation-adjusted required amount: ₹{inflationPopup.updatedValue.toLocaleString("en-IN")}</p>
                  <p>
                    {inflationPopup.delta >= 0
                      ? `Current surplus: ₹${inflationPopup.delta.toLocaleString("en-IN")}`
                      : `Current shortfall: ₹${Math.abs(inflationPopup.delta).toLocaleString("en-IN")}`}
                  </p>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction onClick={() => setInflationPopup(null)}>Got it</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Portfolio;

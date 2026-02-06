import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useGoals } from "@/contexts/GoalsContext";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { ArrowLeft, Calendar, Target, CheckCircle2 } from "lucide-react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const COLORS = ["#7c6340", "#a08060", "#5b8a72", "#b8a080", "#4a7c8c", "#c4b090"];

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

const formatMonthYear = (month?: number, year?: number) => {
  if (!month || !year) return year?.toString() || "";
  const date = new Date(year, month - 1, 1);
  return date.toLocaleString("en-IN", { month: "short", year: "numeric" });
};

const GoalDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { goals, updateGoal } = useGoals();
  const [editOpen, setEditOpen] = useState(false);
  const [editValues, setEditValues] = useState({ amount: "", month: "", year: "", risk: "", sipStartDate: "" });

  const goal = goals.find((g) => g.id === id);

  const allocationData = useMemo(() => {
    if (!goal) return [];
    if (goal.portfolio && Object.keys(goal.portfolio).length > 0) {
      return Object.entries(goal.portfolio).map(([name, value]) => ({
        name,
        value: Math.round(value * 100),
      }));
    }
    return [];
  }, [goal]);

  if (!goal) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-5xl mx-auto p-4 md:p-6">
          <Card className="border-2 border-dashed">
            <CardContent className="py-12 text-center">
              <p className="text-lg font-semibold">Goal not found</p>
              <Button onClick={() => navigate("/dashboard")} className="mt-4">Back to Dashboard</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const goalName = goal.goalName || goal.goalType;
  const targetLabel = formatMonthYear(goal.targetMonth, goal.targetYear);
  const investmentLabel = goal.investmentType === "sip" ? "Monthly SIP" : "Lumpsum";
  const investmentAmount = goal.investmentType === "sip" ? goal.monthlySip : goal.lumpsumAmount;
  const totalContributed = (goal.contributions || []).filter((c) => c.status !== "pending").reduce((sum, c) => sum + c.amount, 0);
  const progress = goal.inflatedValue ? Math.min((totalContributed / goal.inflatedValue) * 100, 100) : 0;
  const riskFunds = RISK_FUND_MAP[goal.riskProfile] || RISK_FUND_MAP.medium;

  const handleEditOpen = () => {
    setEditValues({
      amount: goal.goalAmount.toString(),
      month: goal.targetMonth ? goal.targetMonth.toString() : "",
      year: goal.targetYear.toString(),
      risk: goal.riskProfile,
      sipStartDate: goal.sipStartDate || "",
    });
    setEditOpen(true);
  };

  const handleEditSave = () => {
    updateGoal(goal.id, {
      ...goal,
      goalAmount: parseFloat(editValues.amount),
      targetMonth: editValues.month ? parseInt(editValues.month) : goal.targetMonth,
      targetYear: parseInt(editValues.year),
      riskProfile: editValues.risk,
      sipStartDate: goal.investmentType === "sip" ? editValues.sipStartDate : goal.sipStartDate,
    });
    setEditOpen(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Button variant="ghost" onClick={() => navigate(-1)} className="mb-2">
              <ArrowLeft className="mr-2 h-4 w-4" />Back
            </Button>
            <h1 className="text-3xl font-bold text-foreground capitalize">{goalName}</h1>
            <p className="text-muted-foreground">Goal details and portfolio breakdown</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="capitalize">{goal.riskProfile} risk</Badge>
            <Button variant="outline" onClick={handleEditOpen}>Edit Goal</Button>
          </div>
        </div>

        <Card className="border-2 border-dashed border-primary/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />Current Inflation Impact
            </CardTitle>
            <CardDescription>How inflation affects your financial goals</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-primary mb-1">{((goal.inflationRate || 0) * 100).toFixed(1)}% p.a.</p>
            <p className="text-sm text-muted-foreground mb-4">Your purchasing power decreases by approximately ₹{Math.round((goal.inflationRate || 0.06) * 10000).toLocaleString("en-IN")} for every ₹10,000 annually</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-accent/10">
                <p className="text-xs text-muted-foreground">Total Goal Value Today</p>
                <p className="text-xl font-bold">₹{goal.goalAmount.toLocaleString("en-IN")}</p>
              </div>
              <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                <p className="text-xs text-muted-foreground">Inflation-Adjusted Value</p>
                <p className="text-xl font-bold text-primary">₹{(goal.inflatedValue || goal.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}</p>
                <p className="text-xs text-muted-foreground mt-1">This value reflects inflation-adjusted pricing based on historical trends</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-primary" />Goal Summary</CardTitle>
              <CardDescription>Inflation-adjusted target details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-accent/10">
                  <p className="text-xs text-muted-foreground">Current Cost</p>
                  <p className="text-xl font-bold">₹{goal.goalAmount.toLocaleString("en-IN")}</p>
                </div>
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                  <p className="text-xs text-muted-foreground">Inflation-Adjusted Target</p>
                  <p className="text-xl font-bold text-primary">₹{(goal.inflatedValue || goal.goalAmount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}</p>
                </div>
                <div className="p-4 rounded-lg bg-accent/10">
                  <p className="text-xs text-muted-foreground">Target Date</p>
                  <p className="text-xl font-bold flex items-center gap-2"><Calendar className="h-4 w-4 text-primary" />{targetLabel}</p>
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-semibold">Progress</p>
                <Progress value={progress} className="h-2" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Contributed: ₹{totalContributed.toLocaleString("en-IN")}</span>
                  <span>{Math.round(progress)}% complete</span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg border">
                  <p className="text-xs text-muted-foreground">Investment Plan</p>
                  <p className="text-lg font-bold">{investmentLabel}</p>
                  <p className="text-2xl font-bold text-primary">₹{(investmentAmount || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}{goal.investmentType === "sip" && <span className="text-sm font-normal text-muted-foreground">/month</span>}</p>
                </div>
                <div className="p-4 rounded-lg border">
                  <p className="text-xs text-muted-foreground">Timeline</p>
                  <p className="text-lg font-bold">{goal.years} years</p>
                  <p className="text-xs text-muted-foreground">Inflation rate: {((goal.inflationRate || 0) * 100).toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Asset Allocation</CardTitle>
              <CardDescription>Markowitz-optimized portfolio</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {allocationData.length > 0 ? (
                <>
                  <div className="h-52">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={allocationData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={70}>
                          {allocationData.map((_, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}
                        </Pie>
                        <Tooltip formatter={(value: number) => `${value}%`} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2">
                    {allocationData.map((item, idx) => (
                      <div key={item.name} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                          <span className="font-medium">{item.name}</span>
                        </div>
                        <span className="text-muted-foreground">{item.value}%</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">No optimized allocation available. Recalculate in the Investment Planner.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recommended Fund Categories</CardTitle>
            <CardDescription>Based on your {goal.riskProfile} risk profile</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {riskFunds.map((fund) => (
                <Card key={fund.label} className="border hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2 bg-primary/5 rounded-t-lg">
                    <CardTitle className="text-base text-primary">{fund.label}</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-2">
                    <p className="text-sm text-muted-foreground">{fund.description}</p>
                    <div className="space-y-1">
                      {fund.examples.map((ex) => (
                        <div key={ex} className="flex items-center gap-2 text-xs"><CheckCircle2 className="h-3 w-3 text-success flex-shrink-0" /><span>{ex}</span></div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Investment Breakdown</CardTitle>
            <CardDescription>{goal.investmentType === "sip" ? "Monthly SIP schedule" : "Lumpsum investment details"}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
              <div className="text-center space-y-1">
                <p className="text-sm text-muted-foreground">{goal.investmentType === "sip" ? "Monthly SIP Required" : "Lumpsum Required"}</p>
                <p className="text-3xl font-bold text-primary">₹{(investmentAmount || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}{goal.investmentType === "sip" && <span className="text-sm font-normal text-muted-foreground">/Month</span>}</p>
              </div>
              {goal.investmentType === "sip" && (
                <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4 text-sm">
                  <div><p className="text-muted-foreground">Net Investment</p><p className="font-semibold">₹{((goal.monthlySip || 0) * (goal.years || 1) * 12).toLocaleString("en-IN", { maximumFractionDigits: 0 })}</p></div>
                  <div><p className="text-muted-foreground">Estimated Returns</p><p className="font-semibold text-success">₹{Math.max(0, (goal.inflatedValue || 0) - (goal.monthlySip || 0) * (goal.years || 1) * 12).toLocaleString("en-IN", { maximumFractionDigits: 0 })}</p></div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Edit Goal</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Amount (₹)</Label><Input type="number" value={editValues.amount} onChange={(e) => setEditValues({ ...editValues, amount: e.target.value })} /></div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>Target Month</Label>
                <Select value={editValues.month} onValueChange={(v) => setEditValues({ ...editValues, month: v })}><SelectTrigger><SelectValue placeholder="Month" /></SelectTrigger><SelectContent>{["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].map((m, i) => (<SelectItem key={i + 1} value={String(i + 1)}>{m}</SelectItem>))}</SelectContent></Select>
              </div>
              <div className="space-y-2"><Label>Target Year</Label><Input type="number" value={editValues.year} onChange={(e) => setEditValues({ ...editValues, year: e.target.value })} placeholder="YYYY" /></div>
            </div>
            <div className="space-y-2">
              <Label>Risk Level</Label>
              <Select value={editValues.risk} onValueChange={(v) => setEditValues({ ...editValues, risk: v })}><SelectTrigger><SelectValue placeholder="Risk" /></SelectTrigger><SelectContent><SelectItem value="low">Low</SelectItem><SelectItem value="medium">Medium</SelectItem><SelectItem value="high">High</SelectItem></SelectContent></Select>
            </div>
            {goal.investmentType === "sip" && (<div className="space-y-2"><Label>SIP Start Date</Label><Input type="date" value={editValues.sipStartDate} onChange={(e) => setEditValues({ ...editValues, sipStartDate: e.target.value })} /></div>)}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setEditOpen(false)}>Cancel</Button><Button onClick={handleEditSave}>Save Changes</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GoalDetails;

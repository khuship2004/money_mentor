import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { PiggyBank, TrendingUp, Target, Shield, ArrowRight } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-accent/10">
      <div className="max-w-7xl mx-auto px-4 py-16 md:py-24">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <PiggyBank className="h-16 w-16 text-primary" />
            <h1 className="text-5xl md:text-6xl font-bold text-foreground">MoneyMentor</h1>
          </div>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            Your intelligent personal finance assistant that predicts inflation and helps you plan investments to achieve your future goals
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Link to="/auth">
              <Button size="lg" className="gap-2 text-lg px-8">
                Get Started
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link to="/auth">
              <Button size="lg" variant="outline" className="gap-2 text-lg px-8">
                Learn More
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-20">
          {[
            {
              icon: TrendingUp,
              title: "Inflation Prediction",
              description: "Real-time inflation tracking and future price predictions for your goals",
            },
            {
              icon: Target,
              title: "Goal Planning",
              description: "Set financial goals and track your progress with inflation adjustments",
            },
            {
              icon: Shield,
              title: "Investment Options",
              description: "Get personalized recommendations across FD, SIP, Gold, and Equity",
            },
            {
              icon: PiggyBank,
              title: "Smart Savings",
              description: "Calculate required monthly investments to achieve your targets",
            },
          ].map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-card rounded-xl p-6 border-2 border-border hover:border-primary/50 transition-all hover:shadow-lg"
              >
                <Icon className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-semibold text-foreground mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Index;

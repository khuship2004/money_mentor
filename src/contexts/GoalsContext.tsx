import React, { createContext, useContext, useState, useEffect } from 'react';

export interface Goal {
  id: string;
  goalType: string;
  goalName?: string;
  goalAmount: number;
  targetYear: number;
  targetMonth?: number;
  riskProfile: string;
  investmentType: string;
  inflationRate?: number;
  inflatedValue?: number;
  years?: number;
  portfolio?: Record<string, number>;
  expectedReturn?: number;
  portfolioRisk?: number;
  monthlySip?: number;
  lumpsumAmount?: number;
  lumpsumAvailable?: number;
  message?: string;
  optimizationStatus?: string;
  isLocked?: boolean;
  status?: "ongoing" | "completed";
  createdAt?: string;
  sipStartDate?: string;
  sipPayments?: Array<{ month: string; amount: number; status: "paid" | "pending" }>;
  contributions?: Array<{ date: string; amount: number; type: "sip" | "lumpsum"; status?: "paid" | "pending" }>;
  lastInflationUpdate?: string;
}

interface GoalsContextType {
  goals: Goal[];
  addGoal: (goal: Goal) => void;
  removeGoal: (id: string) => void;
  updateGoal: (id: string, goal: Partial<Goal>) => void;
  clearGoals: () => void;
}

const GoalsContext = createContext<GoalsContextType | undefined>(undefined);

export const GoalsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [goals, setGoals] = useState<Goal[]>(() => {
    // Load from localStorage on mount
    const saved = localStorage.getItem('userGoals');
    if (!saved) return [];
    let parsed: Goal[] = JSON.parse(saved);

    // Migration: remove broken goals created by old duplicate-addGoal bug
    // Those goals have no portfolio data AND no inflationRate
    const before = parsed.length;
    parsed = parsed.filter(g => {
      const hasPortfolio = g.portfolio && Object.keys(g.portfolio).length > 0;
      const hasInflation = typeof g.inflationRate === 'number' && g.inflationRate > 0;
      // Keep if it has EITHER portfolio data or a valid inflation rate
      return hasPortfolio || hasInflation;
    });

    // Deduplicate: if two goals share exact same goalType + targetYear + goalAmount
    // keep only the one that has portfolio data (the correct one)
    const seen = new Map<string, Goal>();
    for (const g of parsed) {
      const key = `${g.goalType}-${g.targetYear}-${g.goalAmount}`;
      const existing = seen.get(key);
      if (!existing) {
        seen.set(key, g);
      } else {
        // Keep the one with portfolio data
        const existingHas = existing.portfolio && Object.keys(existing.portfolio).length > 0;
        const currentHas = g.portfolio && Object.keys(g.portfolio).length > 0;
        if (currentHas && !existingHas) {
          seen.set(key, g);
        }
      }
    }
    parsed = Array.from(seen.values());

    if (parsed.length !== before) {
      // Persist the cleaned-up list immediately
      localStorage.setItem('userGoals', JSON.stringify(parsed));
    }
    return parsed;
  });

  // Save to localStorage whenever goals change
  useEffect(() => {
    localStorage.setItem('userGoals', JSON.stringify(goals));
  }, [goals]);

  const addGoal = (goal: Goal) => {
    const newGoal = {
      ...goal,
      id: goal.id || `goal-${Date.now()}`
    };
    setGoals([...goals, newGoal]);
  };

  const removeGoal = (id: string) => {
    setGoals(goals.filter(g => g.id !== id));
  };

  const updateGoal = (id: string, updatedGoal: Partial<Goal>) => {
    setGoals(goals.map(g => g.id === id ? { ...g, ...updatedGoal, id: g.id } : g));
  };

  const clearGoals = () => {
    setGoals([]);
  };

  return (
    <GoalsContext.Provider value={{ goals, addGoal, removeGoal, updateGoal, clearGoals }}>
      {children}
    </GoalsContext.Provider>
  );
};

export const useGoals = () => {
  const context = useContext(GoalsContext);
  if (!context) {
    throw new Error('useGoals must be used within GoalsProvider');
  }
  return context;
};

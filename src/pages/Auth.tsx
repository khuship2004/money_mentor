import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PiggyBank } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const Auth = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");

  useEffect(() => {
    const session = localStorage.getItem("authSession");
    if (session) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const loadUsers = () => {
    const stored = localStorage.getItem("authUsers");
    if (!stored) return [] as Array<{ name: string; email: string; password: string }>;
    return JSON.parse(stored) as Array<{ name: string; email: string; password: string }>;
  };

  const saveUsers = (users: Array<{ name: string; email: string; password: string }>) => {
    localStorage.setItem("authUsers", JSON.stringify(users));
  };

  const handleSubmit = async (e: React.FormEvent, action: "login" | "signup") => {
    e.preventDefault();
    setIsLoading(true);

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (action === "login") {
      if (!emailRegex.test(loginEmail) || !loginPassword) {
        setIsLoading(false);
        toast({
          title: "Invalid login details",
          description: "Please enter a valid email and password.",
          variant: "destructive",
        });
        return;
      }
      const users = loadUsers();
      const user = users.find((u) => u.email.toLowerCase() === loginEmail.toLowerCase());
      const demoMatch = loginEmail === "demo@moneymentor.com" && loginPassword === "demo123";
      if (!user && !demoMatch) {
        setIsLoading(false);
        toast({
          title: "Authentication failed",
          description: "Account not found. Please sign up first.",
          variant: "destructive",
        });
        return;
      }
      if (user && user.password !== loginPassword) {
        setIsLoading(false);
        toast({
          title: "Authentication failed",
          description: "Incorrect password.",
          variant: "destructive",
        });
        return;
      }
    }

    if (action === "signup") {
      if (!signupName || !emailRegex.test(signupEmail)) {
        setIsLoading(false);
        toast({
          title: "Invalid signup details",
          description: "Please provide your name and a valid email address.",
          variant: "destructive",
        });
        return;
      }
      if (signupPassword.length < 6 || signupPassword !== signupConfirm) {
        setIsLoading(false);
        toast({
          title: "Password issue",
          description: "Passwords must match and be at least 6 characters long.",
          variant: "destructive",
        });
        return;
      }
      const users = loadUsers();
      const exists = users.some((u) => u.email.toLowerCase() === signupEmail.toLowerCase());
      if (exists) {
        setIsLoading(false);
        toast({
          title: "Account exists",
          description: "Please log in with your existing account.",
          variant: "destructive",
        });
        return;
      }
      saveUsers([...users, { name: signupName, email: signupEmail, password: signupPassword }]);
    }

    // Simulate authentication
    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem("authSession", JSON.stringify({
        email: action === "login" ? loginEmail : signupEmail,
        name: action === "login" ? "User" : signupName,
        loginAt: new Date().toISOString(),
      }));
      toast({
        title: action === "login" ? "Welcome back!" : "Account created!",
        description: `Successfully ${action === "login" ? "logged in" : "signed up"}`,
      });
      navigate("/dashboard");
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <PiggyBank className="h-10 w-10 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">MoneyMentor</h1>
          </div>
          <p className="text-muted-foreground">Your personal finance assistant</p>
        </div>

        <Card className="border-2">
          <CardHeader>
            <CardTitle>Access Your Account</CardTitle>
            <CardDescription>
              Sample credentials - Email: <span className="font-semibold">demo@moneymentor.com</span> | Password: <span className="font-semibold">demo123</span>
            </CardDescription>
          </CardHeader>

          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <form onSubmit={(e) => handleSubmit(e, "login")}>
                <CardContent className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="you@example.com"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="••••••••"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      required
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Logging in..." : "Login"}
                  </Button>
                </CardFooter>
              </form>
            </TabsContent>

            <TabsContent value="signup">
              <form onSubmit={(e) => handleSubmit(e, "signup")}>
                <CardContent className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-name">Full Name</Label>
                    <Input
                      id="signup-name"
                      type="text"
                      placeholder="John Doe"
                      value={signupName}
                      onChange={(e) => setSignupName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="you@example.com"
                      value={signupEmail}
                      onChange={(e) => setSignupEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <Input
                      id="signup-password"
                      type="password"
                      placeholder="••••••••"
                      value={signupPassword}
                      onChange={(e) => setSignupPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-confirm">Confirm Password</Label>
                    <Input
                      id="signup-confirm"
                      type="password"
                      placeholder="••••••••"
                      value={signupConfirm}
                      onChange={(e) => setSignupConfirm(e.target.value)}
                      required
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Creating account..." : "Sign Up"}
                  </Button>
                </CardFooter>
              </form>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default Auth;

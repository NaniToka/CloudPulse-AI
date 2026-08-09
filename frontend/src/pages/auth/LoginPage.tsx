import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Zap, Loader2 } from "lucide-react";
import { loginSchema, type LoginFormValues } from "@/lib/validations/auth";
import { useLogin } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const [showPw, setShowPw] = useState(false);
  const { mutate: login, isPending, error } = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = (data: LoginFormValues) => login(data);

  const apiError =
    error && "response" in (error as any)
      ? ((error as any).response?.data?.detail as string)
      : null;

  return (
    <div className="glass rounded-2xl p-8 space-y-7">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 lg:hidden mb-4">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-gradient">
            <Zap className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="font-bold gradient-text">CloudPulse AI</span>
        </div>
        <h1 className="text-2xl font-semibold text-foreground">Welcome back</h1>
        <p className="text-sm text-muted-foreground">Sign in to your workspace</p>
      </div>

      {/* API Error */}
      {apiError && (
        <div className="rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
          {apiError}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Email
          </label>
          <input
            {...register("email")}
            type="email"
            placeholder="you@company.com"
            autoComplete="email"
            className={cn(
              "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
              errors.email
                ? "border-danger/50 focus:border-danger"
                : "border-white/10 focus:border-brand-blue/50"
            )}
          />
          {errors.email && (
            <p className="text-xs text-danger">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Password
          </label>
          <div className="relative">
            <input
              {...register("password")}
              type={showPw ? "text" : "password"}
              placeholder="••••••••"
              autoComplete="current-password"
              className={cn(
                "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
                errors.password
                  ? "border-danger/50 focus:border-danger"
                  : "border-white/10 focus:border-brand-blue/50"
              )}
            />
            <button
              type="button"
              onClick={() => setShowPw(!showPw)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-xs text-danger">{errors.password.message}</p>
          )}
        </div>

        <div className="flex justify-end">
          <button type="button" className="text-xs text-brand-blue hover:underline">
            Forgot password?
          </button>
        </div>

        <Button type="submit" size="lg" className="w-full" disabled={isPending}>
          {isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Signing in…
            </>
          ) : (
            "Sign in"
          )}
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => {
            login({ email: "admin@cloudpulse.io", password: "Password123!" });
          }}
          disabled={isPending}
          className="w-full text-xs border-brand-blue/30 text-brand-blue hover:bg-brand-blue/10 gap-1.5"
        >
          <Zap className="h-3.5 w-3.5" /> 1-Click Demo Login (admin@cloudpulse.io)
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Don't have an account?{" "}
        <Link to="/register" className="text-brand-blue hover:underline font-medium">
          Start free trial →
        </Link>
      </p>

    </div>
  );
}

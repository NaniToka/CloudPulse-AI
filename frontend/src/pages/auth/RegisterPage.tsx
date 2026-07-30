import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Zap, Loader2 } from "lucide-react";
import { registerSchema, type RegisterFormValues } from "@/lib/validations/auth";
import { useRegister } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ];
  const score = checks.filter(Boolean).length;
  const labels = ["", "Weak", "Fair", "Good", "Strong"];
  const colors = ["", "bg-danger", "bg-warning", "bg-brand-blue", "bg-success"];

  if (!password) return null;
  return (
    <div className="space-y-1.5">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={cn(
              "h-1 flex-1 rounded-full transition-colors duration-300",
              i <= score ? colors[score] : "bg-white/10"
            )}
          />
        ))}
      </div>
      <p className={cn("text-xs", score >= 3 ? "text-success" : score >= 2 ? "text-warning" : "text-danger")}>
        {labels[score]}
      </p>
    </div>
  );
}

export default function RegisterPage() {
  const [showPw, setShowPw] = useState(false);
  const { mutate: register_, isPending, error } = useRegister();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  const password = watch("password", "");

  const onSubmit = (data: RegisterFormValues) => {
    const { confirm_password, ...payload } = data;
    register_(payload);
  };

  const apiError =
    error && "response" in (error as any)
      ? ((error as any).response?.data?.detail as string)
      : null;

  return (
    <div className="glass rounded-2xl p-8 space-y-7">
      <div className="space-y-2">
        <div className="flex items-center gap-2 lg:hidden mb-4">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-gradient">
            <Zap className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="font-bold gradient-text">CloudPulse AI</span>
        </div>
        <h1 className="text-2xl font-semibold text-foreground">Create your account</h1>
        <p className="text-sm text-muted-foreground">Start your free trial — no credit card required.</p>
      </div>

      {apiError && (
        <div className="rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
          {apiError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          {(["first_name", "last_name"] as const).map((field) => (
            <div key={field} className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {field === "first_name" ? "First name" : "Last name"}
              </label>
              <input
                {...register(field)}
                placeholder={field === "first_name" ? "Ada" : "Lovelace"}
                className={cn(
                  "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
                  errors[field] ? "border-danger/50" : "border-white/10 focus:border-brand-blue/50"
                )}
              />
              {errors[field] && <p className="text-xs text-danger">{errors[field]?.message}</p>}
            </div>
          ))}
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Email</label>
          <input
            {...register("email")}
            type="email"
            placeholder="you@company.com"
            className={cn(
              "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
              errors.email ? "border-danger/50" : "border-white/10 focus:border-brand-blue/50"
            )}
          />
          {errors.email && <p className="text-xs text-danger">{errors.email.message}</p>}
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Organization (optional)</label>
          <input
            {...register("organization_name")}
            placeholder="Acme Corp"
            className="w-full h-11 rounded-lg bg-bg-overlay border border-white/10 focus:border-brand-blue/50 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Password</label>
          <div className="relative">
            <input
              {...register("password")}
              type={showPw ? "text" : "password"}
              placeholder="••••••••"
              className={cn(
                "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
                errors.password ? "border-danger/50" : "border-white/10 focus:border-brand-blue/50"
              )}
            />
            <button type="button" onClick={() => setShowPw(!showPw)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          <PasswordStrength password={password} />
          {errors.password && <p className="text-xs text-danger">{errors.password.message}</p>}
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Confirm password</label>
          <input
            {...register("confirm_password")}
            type="password"
            placeholder="••••••••"
            className={cn(
              "w-full h-11 rounded-lg bg-bg-overlay border px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-colors",
              errors.confirm_password ? "border-danger/50" : "border-white/10 focus:border-brand-blue/50"
            )}
          />
          {errors.confirm_password && <p className="text-xs text-danger">{errors.confirm_password.message}</p>}
        </div>

        <Button type="submit" size="lg" className="w-full mt-2" disabled={isPending}>
          {isPending ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating account…</> : "Create account →"}
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="text-brand-blue hover:underline font-medium">Sign in</Link>
      </p>
    </div>
  );
}

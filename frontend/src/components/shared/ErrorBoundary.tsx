import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home, ServerCrash } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught React ErrorBoundary exception:", error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  private handleGoHome = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = "/dashboard";
  };

  public render() {
    if (this.state.hasError) {
      const isNetworkError =
        this.state.error?.message?.toLowerCase().includes("network") ||
        this.state.error?.message?.toLowerCase().includes("failed to fetch") ||
        this.state.error?.message?.toLowerCase().includes("connection");

      return (
        <div className="min-h-screen w-full bg-bg-void flex items-center justify-center p-6">
          <div className="max-w-xl w-full glass rounded-2xl p-8 border border-white/10 shadow-2xl space-y-6 text-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-16 h-16 rounded-2xl bg-danger/10 border border-danger/30 flex items-center justify-center mx-auto text-danger shadow-lg shadow-danger/20">
              {isNetworkError ? (
                <ServerCrash className="w-8 h-8" />
              ) : (
                <AlertTriangle className="w-8 h-8" />
              )}
            </div>

            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-foreground tracking-tight">
                {isNetworkError
                  ? "Backend Connection Error"
                  : "Application Component Error"}
              </h1>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {isNetworkError
                  ? "Unable to reach the CloudPulse-AI backend API. Please ensure the backend server is running on http://localhost:8000."
                  : "An unexpected client exception occurred while rendering this module."}
              </p>
            </div>

            {this.state.error && (
              <div className="text-left bg-bg-overlay rounded-xl p-4 border border-white/5 space-y-2">
                <p className="text-xs font-semibold text-rose-400 font-mono">
                  {this.state.error.name}: {this.state.error.message}
                </p>
                {this.state.errorInfo && (
                  <details className="text-[11px] text-muted-foreground/70 font-mono whitespace-pre-wrap max-h-36 overflow-y-auto">
                    <summary className="cursor-pointer text-xs text-brand-blue hover:underline mb-1">
                      View Component Stack
                    </summary>
                    {this.state.errorInfo.componentStack}
                  </details>
                )}
              </div>
            )}

            <div className="flex items-center justify-center gap-3 pt-2">
              <Button
                onClick={this.handleReset}
                variant="default"
                className="gap-2 bg-brand-gradient text-white hover:opacity-90 shadow-md"
              >
                <RefreshCw className="w-4 h-4" />
                Reload Application
              </Button>

              <Button
                onClick={this.handleGoHome}
                variant="outline"
                className="gap-2 bg-bg-elevated border-white/10 text-foreground hover:bg-white/5"
              >
                <Home className="w-4 h-4" />
                Dashboard Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

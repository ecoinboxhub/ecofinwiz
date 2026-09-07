import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home, ChevronDown, ChevronUp, X } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";
import { useTranslations } from "../i18n/useTranslations";
import * as Sentry from "@sentry/react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo });

    console.error("ErrorBoundary caught:", error, errorInfo);

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    Sentry.captureException(error, {
      extra: {
        componentStack: errorInfo.componentStack,
      },
    });
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = "/";
  };

  private toggleDetails = () => {
    this.setState(prev => ({ showDetails: !prev.showDetails }));
  };

  private clearError = () => {
    this.setState({ hasError: false, error: null, errorInfo: null, showDetails: false });
  };

  render() {
    const { hasError, error, errorInfo, showDetails } = this.state;
    const { t } = useTranslations();
    const { language } = useLanguage();

    if (!hasError) {
      return this.props.children;
    }

    if (this.props.fallback) {
      return this.props.fallback;
    }

    const errorMessage = error?.message || t("errorBoundary.defaultMessage");
    const errorStack = errorInfo?.componentStack || "";

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-white font-semibold text-lg">{t("errorBoundary.title")}</h1>
                <p className="text-white/80 text-sm">{t("errorBoundary.subtitle")}</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-4">
            <div className="bg-red-50 border border-red-100 rounded-xl p-4">
              <p className="text-red-700 text-sm">{errorMessage}</p>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={this.handleReload}
                className="btn-primary flex-1 min-w-[140px]"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                {t("errorBoundary.reload")}
              </button>
              <button
                onClick={this.handleGoHome}
                className="btn-secondary flex-1 min-w-[140px]"
              >
                <Home className="w-4 h-4 mr-2" />
                {t("errorBoundary.goHome")}
              </button>
            </div>

            <button
              onClick={this.toggleDetails}
              className="w-full text-left text-sm text-gray-500 hover:text-gray-700 flex items-center justify-between py-2"
            >
              <span>{t("errorBoundary.showDetails")}</span>
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showDetails && (
              <div className="bg-gray-900 rounded-xl p-4 text-xs text-green-300 overflow-x-auto max-h-64 overflow-y-auto">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono">Error Stack</span>
                  <button
                    onClick={this.clearError}
                    className="text-gray-400 hover:text-white"
                    aria-label="Dismiss"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <pre className="font-mono whitespace-pre-wrap break-all">{errorStack}</pre>
              </div>
            )}
          </div>

          <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 text-center">
            <p className="text-xs text-gray-400">
              {t("errorBoundary.reported")}
            </p>
          </div>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
import { useCallback } from "react";

interface ErrorContext {
  component?: string;
  action?: string;
  userId?: string;
  [key: string]: any;
}

/**
 * Hook for handling errors with Sentry integration
 */
export function useErrorHandler() {
  const handleError = useCallback((error: Error, context?: ErrorContext) => {
    console.error("Application error:", error, context);

    const errorPayload = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
      url: typeof window !== "undefined" ? window.location.href : "unknown",
      ...context,
    };

    if (typeof window !== "undefined" && (window as any).Sentry) {
      (window as any).Sentry.captureException(error, { extra: errorPayload });
    }

    if (import.meta.env.DEV) {
      console.group("Error Details");
      console.error(error);
      console.log("Context:", context);
      console.groupEnd();
    }
  }, []);

  const handleAsyncError = useCallback(async (
    promise: Promise<any>,
    context?: ErrorContext
  ) => {
    try {
      return await promise;
    } catch (error) {
      handleError(error instanceof Error ? error : new Error(String(error)), context);
      throw error;
    }
  }, [handleError]);

  return { handleError, handleAsyncError };
}

export default useErrorHandler;
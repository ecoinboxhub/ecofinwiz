import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { LanguageProvider } from "./context/LanguageContext";
import App from "./App";
import "./index.css";
import * as Sentry from "@sentry/react";

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const ENVIRONMENT = import.meta.env.VITE_APP_ENV || "development";
const RELEASE = import.meta.env.VITE_APP_VERSION || "0.0.0";

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    release: RELEASE,
    integrations: [
      Sentry.browserTracingIntegration({
        routingInstrumentation: Sentry.reactRouterV7Instrumentation(
          BrowserRouter,
        ),
      }),
    ],
    tracesSampleRate: 0.25,
    profilesSampleRate: 0.10,
    replaysOnErrorSampleRate: 1.0,
    replaysSessionSampleRate: 0.1,
    beforeSend(event, hint) {
      // Filter out expected errors
      if (event.exception) {
        for (const exception of event.exception.values || []) {
          if (exception.type === "NetworkError" || exception.type === "AbortError") {
            return null;
          }
        }
      }
      return event;
    },
  });
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js", { scope: "/", updateViaCache: "none" })
      .catch(() => {});
  });
}

ReactDOM.createRoot(document.getElementById("app")!, {
  onUncaughtError: (error) => {
    console.error("[BOOT-FAIL] message:", (error as Error).message);
    console.error("[BOOT-FAIL] stack:", (error as Error).stack);
  },
}).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <LanguageProvider>
          <App />
        </LanguageProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);

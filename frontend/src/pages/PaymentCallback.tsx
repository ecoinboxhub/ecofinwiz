import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { CheckCircle, XCircle } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";

export default function PaymentCallback() {
  useEffect(() => { document.title = "Payment - Finwize"; }, []);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { t } = useTranslations();
  const [status, setStatus] = useState<"verifying" | "success" | "failed">("verifying");

  useEffect(() => {
    const reference = searchParams.get("reference") || searchParams.get("trxref") || searchParams.get("payment_ref");
    if (!reference) return setStatus("failed");

    client.post("/payment/verify", { reference })
      .then(({ data }) => {
        setStatus(data.status === "success" ? "success" : "failed");
      })
      .catch(() => setStatus("failed"));
  }, [searchParams]);

  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <div className="card text-center py-12 space-y-4">
        {status === "verifying" && (
          <div className="animate-pulse space-y-3">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto" />
            <p className="text-gray-500 font-medium">{t("paymentCallback.verifying")}</p>
          </div>
        )}

        {status === "success" && (
          <>
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
            <h2 className="text-xl font-bold text-gray-800">{t("paymentCallback.success")}</h2>
            <p className="text-sm text-gray-400">{t("paymentCallback.successMessage")}</p>
          </>
        )}

        {status === "failed" && (
          <>
            <XCircle className="w-16 h-16 text-rose-500 mx-auto" />
            <h2 className="text-xl font-bold text-gray-800">{t("paymentCallback.failed")}</h2>
            <p className="text-sm text-gray-400">{t("paymentCallback.failedMessage")}</p>
          </>
        )}

        <button onClick={() => navigate(status === "success" ? "/" : "/pricing")} className="btn-primary w-full mt-4">
          {status === "success" ? t("paymentCallback.goHome") : t("paymentCallback.retry")}
        </button>
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { Plus, Download, Send, FileText } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function Invoices() {
  const { t } = useTranslations();
  const [invoices, setInvoices] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ client_name: "", client_email: "", amount: "", due_date: "" });

  useEffect(() => { client.get("/invoices").then(({ data }) => setInvoices(Array.isArray(data) ? data : [])).catch(() => {}); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/invoices", {
        client_name: form.client_name, client_email: form.client_email,
        line_items: [{ description: "Services", quantity: 1, unit_price: Number(form.amount) }],
        due_date: form.due_date,
      });
      setShowForm(false);
      setForm({ client_name: "", client_email: "", amount: "", due_date: "" });
      client.get("/invoices").then(({ data }) => setInvoices(Array.isArray(data) ? data : []));
      toast.success("Invoice created");
    } catch { toast.error("Failed to create invoice"); }
  };

  const statusColor: Record<string, string> = { draft: "badge-gold", sent: "badge-sky", paid: "badge-green", overdue: "badge-rose", cancelled: "badge bg-gray-100 text-gray-500" };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("invoices.title")}</h1>
          <p className="text-sm text-gray-400">{t("invoices.count", invoices.length.toString())}</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary !p-3 !rounded-xl" aria-label={t("invoices.new")}><Plus className="w-5 h-5" /></button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3">
          <h3 className="font-semibold text-gray-800">{t("invoices.new")}</h3>
          <input className="input-field" placeholder={t("invoices.clientName")} value={form.client_name} onChange={e => setForm({ ...form, client_name: e.target.value })} required />
          <input type="email" className="input-field" placeholder={t("invoices.clientEmail")} value={form.client_email} onChange={e => setForm({ ...form, client_email: e.target.value })} required />
          <input type="number" className="input-field" placeholder={t("invoices.amountPlaceholder")} value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} required min="0" step="0.01" />
          <input type="date" className="input-field" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} required />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">{t("invoices.create")}</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">{t("common.cancel")}</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {invoices.length === 0 ? (
          <div className="text-center py-10">
            <FileText className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("invoices.empty")}</p>
            <p className="text-xs text-gray-300 mt-1">Create an invoice to bill your clients</p>
          </div>
        ) : invoices.map((inv: any) => (
          <div key={inv.id} className="card !p-4">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="font-medium text-gray-800 text-sm">{inv.client_name || inv.client_name}</p>
                <p className="text-xs text-gray-400">{inv.invoice_number || `#${inv.id?.slice(0, 8)}`}</p>
              </div>
              <span className={statusColor[inv.status] || "badge-gold"}>{t("invoices." + (inv.status || "draft"))}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold text-gray-800">${Number(inv.total_amount || inv.amount).toLocaleString()}</span>
              <span className="text-xs text-gray-400">{t("invoices.due")}{inv.due_date ? new Date(inv.due_date).toLocaleDateString() : t("invoices.na")}</span>
            </div>
            <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100">
              <button className="text-xs flex items-center gap-1 text-sky-500 font-medium"><Download className="w-3 h-3" /> {t("invoices.pdf")}</button>
              <button className="text-xs flex items-center gap-1 text-gold-500 font-medium"><Send className="w-3 h-3" /> {t("invoices.send")}</button>
            </div>
          </div>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/mentor/chat"
        personaName="Chidi"
        personaRole="AI Business Mentor"
        accent="from-gold-400 to-gold-600"
        iconBg="bg-gradient-to-r from-gold-500 to-gold-600"
        placeholder="Ask Chidi about your invoices..."
        prompts={["Create an invoice for Acme for $500", "List my invoices", "How do I chase unpaid invoices?"]}
      />
    </div>
  );
}

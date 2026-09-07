import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { CheckCircle2, Circle, Plus, Calendar, Flag, FileText, FileSpreadsheet } from "lucide-react";
import client from "../api/client";
import { useTranslations } from "../i18n/useTranslations";
import ChatWidget from "../components/ChatWidget";

export default function BusinessTasks() {
  const { t } = useTranslations();
  const [tasks, setTasks] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", due_date: "" });

  useEffect(() => { client.get("/tasks").then(({ data }) => setTasks(Array.isArray(data) ? data : [])).catch(() => {}); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/tasks", form);
      setShowForm(false);
      setForm({ title: "", description: "", priority: "medium", due_date: "" });
      client.get("/tasks").then(({ data }) => setTasks(Array.isArray(data) ? data : []));
      toast.success("Task created");
    } catch { toast.error("Failed to create task"); }
  };

  const toggleStatus = async (id: string, current: string) => {
    try { await client.patch(`/tasks/${id}`, { status: current === "completed" ? "pending" : "completed" }); } catch { toast.error("Failed to update task"); }
  };

  const priorityColor: Record<string, string> = { high: "text-rose-500", medium: "text-gold-500", low: "text-sky-500" };

  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{t("businessTasks.title")}</h1>
          <p className="text-sm text-gray-400">{t("businessTasks.subtitle")}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card !p-4 text-center">
          <FileText className="w-8 h-8 text-gold-500 mx-auto mb-2" />
          <p className="text-sm font-medium text-gray-800">{t("businessTasks.tasks")}</p>
          <p className="text-xs text-gray-400">{t("businessTasks.active", tasks.length.toString())}</p>
        </div>
        <a href="/invoices" className="card !p-4 text-center block">
          <FileSpreadsheet className="w-8 h-8 text-sky-500 mx-auto mb-2" />
          <p className="text-sm font-medium text-gray-800">{t("businessTasks.invoices")}</p>
          <p className="text-xs text-gray-400">{t("businessTasks.viewAll")}</p>
        </a>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">{t("businessTasks.tasksTitle")}</h2>
        <button onClick={() => setShowForm(true)} className="btn-primary !p-2 !rounded-xl"><Plus className="w-4 h-4" /></button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card space-y-3">
          <h3 className="font-semibold text-gray-800">{t("businessTasks.new")}</h3>
          <input className="input-field" placeholder={t("businessTasks.titlePlaceholder")} value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
          <textarea className="input-field min-h-[80px]" placeholder={t("businessTasks.descPlaceholder")} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          <select className="input-field" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}>
            <option value="low">{t("businessTasks.low")}</option>
            <option value="medium">{t("businessTasks.medium")}</option>
            <option value="high">{t("businessTasks.high")}</option>
          </select>
          <input type="date" className="input-field" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} />
          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">{t("businessTasks.add")}</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">{t("common.cancel")}</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {tasks.length === 0 ? (
          <div className="text-center py-10">
            <FileText className="w-12 h-12 text-gray-200 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">{t("businessTasks.empty")}</p>
            <p className="text-xs text-gray-300 mt-1">Create your first task to get started</p>
          </div>
        ) : tasks.map((task: any) => (
          <div key={task.id} className="card !p-3 flex items-center gap-3">
            <button onClick={() => toggleStatus(task.id, task.status)} className="flex-shrink-0">
              {task.status === "completed" ? <CheckCircle2 className="w-5 h-5 text-green-500" /> : <Circle className="w-5 h-5 text-gray-300" />}
            </button>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${task.status === "completed" ? "text-gray-400 line-through" : "text-gray-800"}`}>{task.title}</p>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Flag className={`w-3 h-3 ${priorityColor[task.priority] || "text-gray-400"}`} />
                {task.due_date && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{new Date(task.due_date).toLocaleDateString()}</span>}
              </div>
            </div>
            <span className={`badge text-xs ${task.status === "completed" ? "badge-green" : task.status === "in_progress" ? "badge-sky" : "badge-gold"}`}>
              {task.status || t("businessTasks.pending")}
            </span>
          </div>
        ))}
      </div>

      <ChatWidget
        endpoint="/ai/mentor/chat"
        personaName="Chidi"
        personaRole="AI Business Mentor"
        accent="from-gold-400 to-gold-600"
        iconBg="bg-gradient-to-r from-gold-500 to-gold-600"
        placeholder="Ask Chidi about your tasks..."
        prompts={["Create a task to call suppliers", "List my open tasks", "How should I prioritize?"]}
      />
    </div>
  );
}

import { X } from "lucide-react";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export default function ConfirmDialog({ open, title, message, confirmLabel = "Confirm", cancelLabel = "Cancel", onConfirm, onCancel, loading }: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" onClick={onCancel}>
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-5 max-w-sm w-full space-y-4" onClick={(e) => e.stopPropagation()} role="alertdialog" aria-labelledby="confirm-title">
        <div className="flex items-center justify-between">
          <h3 id="confirm-title" className="font-semibold text-gray-800 dark:text-gray-100">{title}</h3>
          <button onClick={onCancel} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg" aria-label={cancelLabel}><X className="w-4 h-4 text-gray-400" /></button>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} className="btn-secondary !py-2 !px-4 text-sm" disabled={loading}>{cancelLabel}</button>
          <button onClick={onConfirm} className="btn-primary !py-2 !px-4 text-sm flex items-center gap-2" disabled={loading}>
            {loading && <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

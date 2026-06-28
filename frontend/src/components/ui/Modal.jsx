/*
 * Minimal modal primitive used by inspection screens.
 */
import React, { useEffect } from "react";
import { X } from "lucide-react";

export default function Modal({ open, onClose, title, children, testId, footer, widthClass = "max-w-lg" }) {
  useEffect(() => {
    if (!open) return undefined;
    const handler = (e) => e.key === "Escape" && onClose?.();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      data-testid={testId}
      className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
    >
      <div className={`w-full ${widthClass} glass rounded-xl shadow-panel`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-ink-700/70">
          <h3 className="text-base font-semibold text-white">{title}</h3>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-1.5 rounded-md hover:bg-ink-800 text-steel-300 hover:text-white transition-colors"
            data-testid={testId ? `${testId}-close` : "modal-close"}
          >
            <X className="size-4" />
          </button>
        </div>
        <div className="px-6 py-5 max-h-[70vh] overflow-auto">{children}</div>
        {footer && (
          <div className="px-6 py-4 border-t border-ink-700/70 flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

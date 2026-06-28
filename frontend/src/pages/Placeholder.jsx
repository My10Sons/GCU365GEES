/*
 * Repository Traceability:
 * - Source Document: DI-SPRINT-00 (Web Setup — placeholder pages for inspection,
 *   review queue, damage cases, reports, admin configuration).
 */
import React from "react";
import { Construction } from "lucide-react";
import { T } from "../constants/testIds";

export default function Placeholder({ title, sprint, doc, summary }) {
  return (
    <div data-testid={T.placeholderRoot} className="px-8 py-12 max-w-3xl">
      <div className="flex items-start gap-4">
        <div className="size-12 rounded-md bg-ink-800 border border-ink-700 flex items-center justify-center">
          <Construction className="size-5 text-amber400" />
        </div>
        <div className="flex-1">
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">
            Placeholder — {sprint}
          </div>
          <h1 className="text-2xl font-semibold text-white mt-1">{title}</h1>
          <p className="text-sm text-steel-300 mt-3 leading-relaxed">
            {summary}
          </p>
          <div className="mt-5 font-mono text-[11px] text-steel-400">
            Source: {doc}
          </div>
        </div>
      </div>
    </div>
  );
}

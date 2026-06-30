import React, { useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { HelpCircle, X, Languages, BookOpen, ListChecks, Lightbulb } from "lucide-react";
import { HELP, topicForPath } from "../constants/helpContent";
import { T } from "../constants/testIds";

export default function HelpDrawer() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);
  const [lang, setLang] = useState("en");

  const topic = topicForPath(pathname);
  const data = HELP[topic] || HELP.dashboard;
  const rtl = lang === "ar";
  const tx = (o) => (o ? o[lang] || o.en : "");

  return (
    <>
      <button
        data-testid={T.helpButton}
        onClick={() => setOpen(true)}
        title="Help & tips for this page"
        className="fixed bottom-6 right-6 z-40 size-12 grid place-items-center rounded-full bg-signal hover:bg-signal/90 text-white shadow-lg shadow-signal/30 transition-transform hover:scale-105"
      >
        <HelpCircle className="size-6" />
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-[2px]" onClick={() => setOpen(false)} />
          <aside
            data-testid={T.helpDrawer}
            dir={rtl ? "rtl" : "ltr"}
            className="relative w-full max-w-md h-full bg-ink-900 border-l border-ink-700 shadow-2xl overflow-y-auto animate-[slideIn_.2s_ease-out]"
            style={{ animationName: "none" }}
          >
            <div className="sticky top-0 bg-ink-900/95 backdrop-blur border-b border-ink-700 px-5 py-4 flex items-center gap-3">
              <BookOpen className="size-5 text-signal-soft shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-[10px] uppercase tracking-wider text-steel-400">Help &amp; tips</div>
                <div className="text-sm font-semibold text-white truncate">{tx(data.title)}</div>
              </div>
              <button
                data-testid={T.helpLang}
                onClick={() => setLang(rtl ? "en" : "ar")}
                title="Toggle English / Arabic"
                className="px-2 py-1.5 rounded-md text-[11px] font-medium bg-ink-800 border border-ink-700 text-steel-200 hover:bg-ink-700/80 flex items-center gap-1"
              >
                <Languages className="size-3.5" /> {rtl ? "EN" : "ع"}
              </button>
              <button
                data-testid={T.helpDrawerClose}
                onClick={() => setOpen(false)}
                className="size-8 grid place-items-center rounded-md text-steel-300 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 hover:text-white"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className={`px-5 py-5 space-y-5 ${rtl ? "text-right" : ""}`}>
              <p className="text-sm text-steel-200 leading-relaxed">{tx(data.intro)}</p>

              {data.steps?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400 mb-2">
                    <ListChecks className="size-3.5" /> {rtl ? "الخطوات" : "Steps"}
                  </div>
                  <ol className={`space-y-2.5 ${rtl ? "pr-1" : "pl-1"}`}>
                    {data.steps.map((s, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm text-steel-200">
                        <span className="shrink-0 size-5 grid place-items-center rounded-full bg-signal/20 border border-signal/40 text-[11px] font-semibold text-signal-soft">{i + 1}</span>
                        <span className="leading-relaxed">{tx(s)}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {data.tips?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400 mb-2">
                    <Lightbulb className="size-3.5" /> {rtl ? "نصائح" : "Tips"}
                  </div>
                  <ul className="space-y-2">
                    {data.tips.map((t, i) => (
                      <li key={i} className="text-xs text-steel-300 bg-ink-800/60 border border-ink-700/70 rounded-md px-3 py-2 leading-relaxed">{tx(t)}</li>
                    ))}
                  </ul>
                </div>
              )}

              <Link
                data-testid={T.helpOpenFull}
                to="/help"
                onClick={() => setOpen(false)}
                className="inline-flex items-center gap-2 text-xs font-medium text-signal-soft hover:text-signal"
              >
                <BookOpen className="size-3.5" /> {rtl ? "افتح الدليل الكامل" : "Open the full guide"}
              </Link>
            </div>
          </aside>
        </div>
      )}
    </>
  );
}

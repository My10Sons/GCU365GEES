import React, { useState } from "react";
import { BookOpen, Languages, ListChecks, Lightbulb, ChevronDown, ShieldCheck } from "lucide-react";
import { HELP, HELP_TOPICS } from "../constants/helpContent";
import { T } from "../constants/testIds";

export default function Help() {
  const [lang, setLang] = useState("en");
  const [openKey, setOpenKey] = useState("trip");
  const rtl = lang === "ar";
  const tx = (o) => (o ? o[lang] || o.en : "");

  return (
    <div data-testid={T.helpPage} className="px-8 py-8 max-w-3xl" dir={rtl ? "rtl" : "ltr"}>
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <BookOpen className="size-6 text-steel-300" /> {rtl ? "المساعدة والدليل" : "Help & Guide"}
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl">
            {rtl
              ? "دليل موجز لكل أداة في النظام. لكل شاشة زر مساعدة (؟) يعرض نصائح خاصة بها."
              : "A short guide to every tool. Each screen also has a “?” button with tips for that page."}
          </p>
        </div>
        <button
          data-testid={T.helpLang}
          onClick={() => setLang(rtl ? "en" : "ar")}
          title="Toggle English / Arabic"
          className="shrink-0 px-3 py-2 rounded-md text-xs font-medium bg-ink-800 border border-ink-700 text-steel-200 hover:bg-ink-700/80 flex items-center gap-1.5"
        >
          <Languages className="size-3.5" /> {rtl ? "English" : "العربية"}
        </button>
      </div>

      <div className="mt-6 rounded-lg border border-emerald400/30 bg-emerald-400/5 px-4 py-3 flex items-start gap-2.5">
        <ShieldCheck className="size-4 mt-0.5 text-emerald400 shrink-0" />
        <p className="text-xs text-steel-300 leading-relaxed">
          {rtl
            ? "نتائج الذكاء الاصطناعي استرشادية فقط. لا تُتخذ قرارات المسؤولية أو الرسوم أو الإصلاح هنا — تُدار في أنظمة CROMS والصيانة."
            : "AI results are advisory only. Final liability, charges and repair decisions are not made here — they live in CROMS and Maintenance."}
        </p>
      </div>

      <div className="mt-6 space-y-3">
        {HELP_TOPICS.map((key) => {
          const data = HELP[key];
          const isOpen = openKey === key;
          return (
            <div key={key} className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
              <button
                data-testid={`help-topic-${key}`}
                onClick={() => setOpenKey(isOpen ? null : key)}
                className="w-full px-5 py-4 flex items-center gap-3 text-start hover:bg-ink-800/50 transition-colors"
              >
                <span className="flex-1 text-sm font-semibold text-white">{tx(data.title)}</span>
                <ChevronDown className={`size-4 text-steel-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
              </button>
              {isOpen && (
                <div className={`px-5 pb-5 space-y-4 ${rtl ? "text-right" : ""}`}>
                  <p className="text-sm text-steel-200 leading-relaxed">{tx(data.intro)}</p>
                  {data.steps?.length > 0 && (
                    <div>
                      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400 mb-2">
                        <ListChecks className="size-3.5" /> {rtl ? "الخطوات" : "Steps"}
                      </div>
                      <ol className="space-y-2.5">
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
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

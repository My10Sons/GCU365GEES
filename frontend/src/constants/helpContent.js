// Bilingual (EN/AR), task-focused help content for operators. Shared by the in-context
// Help drawer and the central Help & Guide page.

export const HELP_TOPICS = [
  "dashboard", "trip", "inspections", "review", "cases", "reports", "settings", "admin",
];

export const HELP = {
  dashboard: {
    title: { en: "Dashboard", ar: "لوحة المعلومات" },
    intro: {
      en: "Your starting point — an overview of activity and quick access to every tool.",
      ar: "نقطة البداية — نظرة عامة على النشاط ووصول سريع إلى جميع الأدوات.",
    },
    steps: [
      { en: "Use the left menu to open a tool (Trip Inspection, Review Queue, Damage Cases…).", ar: "استخدم القائمة الجانبية لفتح أداة (فحص الرحلة، قائمة المراجعة، حالات الضرر…)." },
      { en: "Your tenant and role appear at the top-right.", ar: "يظهر المستأجر والدور في أعلى اليمين." },
      { en: "Switch light / dark mode with the sun/moon button.", ar: "بدّل بين الوضع الفاتح والداكن عبر زر الشمس/القمر." },
    ],
    tips: [
      { en: "A greyed-out, “locked” menu item means your role doesn’t have access to it.", ar: "العنصر المعطّل (\"مقفل\") يعني أن دورك لا يملك صلاحية الوصول إليه." },
    ],
  },
  trip: {
    title: { en: "Trip Inspection", ar: "فحص الرحلة" },
    intro: {
      en: "Run a guided before/after walkaround and get an advisory damage report you can hand to the customer.",
      ar: "نفّذ فحصًا محيطيًا (قبل/بعد) واحصل على تقرير ضرر استرشادي يمكن تسليمه للعميل.",
    },
    steps: [
      { en: "Pick the angles to inspect — Front, Rear, Left, Right, Roof — and Interior if needed.", ar: "اختر الزوايا للفحص — الأمام، الخلف، اليسار، اليمين، السقف — والداخلية عند الحاجة." },
      { en: "For each area, add a Before photo and an After photo.", ar: "لكل منطقة، أضف صورة قبل وصورة بعد." },
      { en: "Choose Fast (quick) or Thorough (most accurate). Fast automatically re-checks any uncertain area on the accurate model.", ar: "اختر سريع (أسرع) أو دقيق (الأكثر دقة). يعيد الوضع السريع فحص أي منطقة غير مؤكدة تلقائيًا على النموذج الدقيق." },
      { en: "Press Analyze — each area’s result appears the moment it’s ready.", ar: "اضغط تحليل — تظهر نتيجة كل منطقة فور جاهزيتها." },
      { en: "Review the findings, condition score, cleanliness and estimated repair cost (SAR).", ar: "راجع النتائج ودرجة الحالة والنظافة وتكلفة الإصلاح المقدّرة (ريال سعودي)." },
      { en: "Export a branded PDF (English / Arabic) for the handover.", ar: "صدّر ملف PDF يحمل هويتك (إنجليزي/عربي) للتسليم." },
    ],
    tips: [
      { en: "A full 5-angle walkaround gives the most complete handover record.", ar: "الفحص الكامل بخمس زوايا يمنح أكمل سجل تسليم." },
      { en: "A “Pro-verified” badge means that area was double-checked on the high-accuracy model.", ar: "شارة \"مُتحقَّق بدقة\" تعني أن المنطقة فُحصت مجددًا على النموذج عالي الدقة." },
      { en: "High-value new damage automatically opens a Damage Case in the review queue.", ar: "الضرر الجديد مرتفع القيمة يفتح حالة ضرر تلقائيًا في قائمة المراجعة." },
      { en: "Results are advisory — final charges and repair decisions are made elsewhere.", ar: "النتائج استرشادية — تُتخذ قرارات الرسوم والإصلاح في مكان آخر." },
    ],
  },
  inspections: {
    title: { en: "Inspections", ar: "الفحوصات" },
    intro: {
      en: "Browse inspection sessions and the AI damage findings detected for each.",
      ar: "تصفّح جلسات الفحص ونتائج الضرر المكتشفة بالذكاء الاصطناعي لكل منها.",
    },
    steps: [
      { en: "Scroll or filter the list to find a session.", ar: "مرّر أو صفّ القائمة للعثور على جلسة." },
      { en: "Open a session to see its captured images and detected findings.", ar: "افتح جلسة لرؤية الصور الملتقطة والنتائج المكتشفة." },
    ],
    tips: [
      { en: "Findings here feed the Review Queue and Damage Cases.", ar: "تغذّي النتائج هنا قائمة المراجعة وحالات الضرر." },
    ],
  },
  review: {
    title: { en: "Review Queue", ar: "قائمة المراجعة" },
    intro: {
      en: "Check AI findings that need a human decision before they’re trusted.",
      ar: "راجع نتائج الذكاء الاصطناعي التي تتطلب قرارًا بشريًا قبل اعتمادها.",
    },
    steps: [
      { en: "Open an item to see the photo and the AI’s suggestion.", ar: "افتح عنصرًا لرؤية الصورة واقتراح الذكاء الاصطناعي." },
      { en: "Accept or reject the finding based on what you see.", ar: "اقبل النتيجة أو ارفضها بناءً على ما تراه." },
    ],
    tips: [
      { en: "Low-confidence findings are routed here automatically.", ar: "تُوجَّه النتائج منخفضة الثقة إلى هنا تلقائيًا." },
    ],
  },
  cases: {
    title: { en: "Damage Cases", ar: "حالات الضرر" },
    intro: {
      en: "Track a damage case through its lifecycle, from open to resolved.",
      ar: "تابع حالة الضرر عبر دورة حياتها، من الفتح حتى الإغلاق.",
    },
    steps: [
      { en: "Open a case to see its linked findings, status and history.", ar: "افتح حالة لرؤية نتائجها المرتبطة وحالتها وسجلّها." },
      { en: "Advance the status as the case progresses.", ar: "حدّث الحالة مع تقدّم المعالجة." },
    ],
    tips: [
      { en: "Cases can be created automatically from high-value Trip Inspection damage.", ar: "يمكن إنشاء الحالات تلقائيًا من ضرر فحص الرحلة مرتفع القيمة." },
    ],
  },
  reports: {
    title: { en: "Reports", ar: "التقارير" },
    intro: {
      en: "View summary metrics and export operational reports.",
      ar: "اطّلع على المؤشرات الموجزة وصدّر التقارير التشغيلية.",
    },
    steps: [
      { en: "Pick a report or date range, then review the figures.", ar: "اختر تقريرًا أو نطاقًا زمنيًا، ثم راجع الأرقام." },
    ],
    tips: [],
  },
  settings: {
    title: { en: "Tenant Settings", ar: "إعدادات المستأجر" },
    intro: {
      en: "Manage your company branding and walkaround policy (admins).",
      ar: "أدر هوية شركتك وسياسة الفحص المحيطي (للمسؤولين).",
    },
    steps: [
      { en: "Upload your logo and set the company / branch name.", ar: "ارفع شعارك واضبط اسم الشركة / الفرع." },
      { en: "Use the live PDF preview to see how exported reports will look.", ar: "استخدم معاينة PDF المباشرة لرؤية شكل التقارير المصدّرة." },
      { en: "Toggle whether a full 5-angle walkaround is required before analysis.", ar: "فعّل أو ألغِ اشتراط فحص محيطي كامل بخمس زوايا قبل التحليل." },
    ],
    tips: [
      { en: "Branding appears on every exported PDF report.", ar: "تظهر هويتك على كل تقرير PDF مصدّر." },
    ],
  },
  admin: {
    title: { en: "Administration", ar: "الإدارة" },
    intro: {
      en: "Advanced configuration and administration.",
      ar: "الإعدادات والإدارة المتقدمة.",
    },
    steps: [
      { en: "Manage configuration available to your role.", ar: "أدر الإعدادات المتاحة لدورك." },
    ],
    tips: [],
  },
};

export function topicForPath(pathname) {
  const p = pathname || "/";
  if (p === "/" || p === "") return "dashboard";
  for (const key of HELP_TOPICS) {
    if (p.startsWith(`/${key}`)) return key;
  }
  if (p.startsWith("/trip")) return "trip";
  return "dashboard";
}

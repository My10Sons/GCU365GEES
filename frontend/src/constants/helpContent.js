// Bilingual (EN/AR), task-focused help content for operators. Shared by the in-context
// Help drawer and the central Help & Guide page.

export const HELP_TOPICS = [
  "dashboard", "trip", "vehicles", "inspections", "review", "cases", "reports",
  "ai-usage", "developer", "settings", "admin",
];

export const HELP = {
  dashboard: {
    title: { en: "Dashboard", ar: "لوحة المعلومات" },
    intro: {
      en: "Your starting point — an overview of activity, fleet risk, and quick access to every tool.",
      ar: "نقطة البداية — نظرة عامة على النشاط ومخاطر الأسطول ووصول سريع إلى جميع الأدوات.",
    },
    steps: [
      { en: "Use the left menu to open a tool (Trip Inspection, Vehicles, Review Queue, Damage Cases…).", ar: "استخدم القائمة الجانبية لفتح أداة (فحص الرحلة، المركبات، قائمة المراجعة، حالات الضرر…)." },
      { en: "Check the Fleet risk overview — the top riskiest vehicles (repeat offenders) are listed with their recent damage record.", ar: "راجع نظرة مخاطر الأسطول — تُعرض المركبات الأعلى خطورة (المتكررة الضرر) مع سجل أضرارها الأخير." },
      { en: "Your tenant and role appear at the top-right.", ar: "يظهر المستأجر والدور في أعلى اليمين." },
      { en: "Switch light / dark mode with the sun/moon button.", ar: "بدّل بين الوضع الفاتح والداكن عبر زر الشمس/القمر." },
    ],
    tips: [
      { en: "A greyed-out, “locked” menu item means your role doesn’t have access to it.", ar: "العنصر المعطّل (\"مقفل\") يعني أن دورك لا يملك صلاحية الوصول إليه." },
      { en: "Click a vehicle in the risk overview to open its full damage history.", ar: "انقر على مركبة في نظرة المخاطر لفتح سجل أضرارها الكامل." },
    ],
  },
  trip: {
    title: { en: "Trip Inspection", ar: "فحص الرحلة" },
    intro: {
      en: "Run a guided before/after walkaround and get an advisory damage report you can hand to the customer.",
      ar: "نفّذ فحصًا محيطيًا (قبل/بعد) واحصل على تقرير ضرر استرشادي يمكن تسليمه للعميل.",
    },
    steps: [
      { en: "If the rental system pushed a check-out / check-in, a “Rentals awaiting inspection” banner appears — press Use to pre-fill the rental agreement, plate and customer.", ar: "إذا أرسل نظام التأجير حدث تسليم/استلام، يظهر شريط \"إيجارات بانتظار الفحص\" — اضغط استخدام لتعبئة رقم العقد واللوحة والعميل تلقائيًا." },
      { en: "Pick the angles to inspect — Front, Rear, Left, Right, Roof — and Interior if needed.", ar: "اختر الزوايا للفحص — الأمام، الخلف، اليسار، اليمين، السقف — والداخلية عند الحاجة." },
      { en: "For each area, add a Before photo and an After photo.", ar: "لكل منطقة، أضف صورة قبل وصورة بعد." },
      { en: "Optionally add a plate / VIN close-up — the plate is read automatically (OCR) and filled into the report fields.", ar: "اختياريًا أضف صورة قريبة للوحة أو رقم الهيكل — تُقرأ اللوحة تلقائيًا (OCR) وتُعبّأ في حقول التقرير." },
      { en: "Choose Fast (quick) or Thorough (most accurate). Fast automatically re-checks any uncertain area on the accurate model.", ar: "اختر سريع (أسرع) أو دقيق (الأكثر دقة). يعيد الوضع السريع فحص أي منطقة غير مؤكدة تلقائيًا على النموذج الدقيق." },
      { en: "Press Analyze — each area’s result appears the moment it’s ready.", ar: "اضغط تحليل — تظهر نتيجة كل منطقة فور جاهزيتها." },
      { en: "Review the findings, condition score, cleanliness, estimated repair cost (SAR) and any verification warnings.", ar: "راجع النتائج ودرجة الحالة والنظافة وتكلفة الإصلاح المقدّرة (ريال سعودي) وأي تحذيرات تحقق." },
      { en: "Export a branded PDF (English / Arabic) for the handover.", ar: "صدّر ملف PDF يحمل هويتك (إنجليزي/عربي) للتسليم." },
    ],
    tips: [
      { en: "Every photo passes a 10-point verification: blur, wrong angle, framing, same-vehicle match, edited / AI-generated images, screen re-capture, and EXIF metadata (missing, stale or wrong before-after order). Any warning means: review the photos manually before charging.", ar: "تمر كل صورة بتحقق من ١٠ نقاط: الضبابية، الزاوية الخاطئة، الإطار، تطابق المركبة، الصور المعدّلة أو المولّدة بالذكاء الاصطناعي، إعادة التصوير من شاشة، وبيانات EXIF (مفقودة أو قديمة أو ترتيب قبل/بعد خاطئ). أي تحذير يعني: راجع الصور يدويًا قبل احتساب الرسوم." },
      { en: "With “Save to vehicle history” on, the result links to the vehicle registry (by plate / VIN) and builds the vehicle’s damage timeline and risk profile.", ar: "عند تفعيل \"حفظ في سجل المركبة\"، تُربط النتيجة بسجل المركبات (باللوحة/رقم الهيكل) ويُبنى الخط الزمني لأضرار المركبة وملف مخاطرها." },
      { en: "A full 5-angle walkaround gives the most complete handover record.", ar: "الفحص الكامل بخمس زوايا يمنح أكمل سجل تسليم." },
      { en: "A “Pro-verified” badge means that area was double-checked on the high-accuracy model.", ar: "شارة \"مُتحقَّق بدقة\" تعني أن المنطقة فُحصت مجددًا على النموذج عالي الدقة." },
      { en: "High-value new damage automatically opens a Damage Case in the review queue.", ar: "الضرر الجديد مرتفع القيمة يفتح حالة ضرر تلقائيًا في قائمة المراجعة." },
      { en: "When an inspection is finalized with a Rental ID, the matching open rental closes automatically.", ar: "عند إنهاء فحص برقم عقد إيجار، يُغلق الإيجار المفتوح المطابق تلقائيًا." },
      { en: "Results are advisory — final charges and repair decisions are made elsewhere.", ar: "النتائج استرشادية — تُتخذ قرارات الرسوم والإصلاح في مكان آخر." },
    ],
  },
  vehicles: {
    title: { en: "Vehicles", ar: "المركبات" },
    intro: {
      en: "Your fleet registry, built automatically from analyzed trips — every vehicle’s damage history and risk level in one place.",
      ar: "سجل أسطولك، يُبنى تلقائيًا من الرحلات المحلّلة — سجل أضرار كل مركبة ومستوى خطورتها في مكان واحد.",
    },
    steps: [
      { en: "Search or browse by plate, VIN or model.", ar: "ابحث أو تصفّح باللوحة أو رقم الهيكل أو الطراز." },
      { en: "Open a vehicle to see its damage-history timeline — every analyzed trip with its verdict, new issues and estimated costs.", ar: "افتح مركبة لرؤية الخط الزمني لأضرارها — كل رحلة محلّلة بحكمها ومشاكلها الجديدة وتكاليفها المقدّرة." },
      { en: "Check the risk banner: HIGH / repeat-offender vehicles had several damaged trips in the recent window.", ar: "راجع شريط المخاطر: المركبات عالية الخطورة/المتكررة الضرر سجّلت عدة رحلات متضررة في الفترة الأخيرة." },
    ],
    tips: [
      { en: "Vehicles are created and linked automatically when a trip with a readable or entered plate / VIN is finalized — no manual data entry.", ar: "تُنشأ المركبات وتُربط تلقائيًا عند إنهاء رحلة بلوحة أو رقم هيكل مقروء أو مُدخل — دون إدخال يدوي." },
      { en: "Use the risk level to adjust the deposit on the vehicle’s next rental.", ar: "استخدم مستوى الخطورة لتعديل مبلغ التأمين في الإيجار التالي للمركبة." },
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
      { en: "Use the Blur button on an image to hide faces and bystander plates before sharing (privacy).", ar: "استخدم زر التمويه على الصورة لإخفاء الوجوه ولوحات المارة قبل المشاركة (الخصوصية)." },
    ],
    tips: [
      { en: "Findings here feed the Review Queue and Damage Cases.", ar: "تغذّي النتائج هنا قائمة المراجعة وحالات الضرر." },
      { en: "Blurring is permanent for the shared copy — the action is recorded in the audit log.", ar: "التمويه دائم للنسخة المشاركة — ويُسجَّل الإجراء في سجل التدقيق." },
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
      { en: "Export a Najm-style claim package (PDF + JSON) for insurance submission — it bundles the findings, photos references and cost estimates under a claim reference.", ar: "صدّر حزمة مطالبة بنمط نجم (PDF + JSON) لتقديمها للتأمين — تجمع النتائج ومراجع الصور وتقديرات التكلفة تحت رقم مطالبة." },
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
  "ai-usage": {
    title: { en: "AI Usage & Budget", ar: "استهلاك الذكاء الاصطناعي والميزانية" },
    intro: {
      en: "Track AI token consumption, real per-model costs (SAR) and control spending with a monthly budget.",
      ar: "تابع استهلاك رموز الذكاء الاصطناعي والتكاليف الفعلية لكل نموذج (ريال) وتحكّم بالإنفاق عبر ميزانية شهرية.",
    },
    steps: [
      { en: "Review usage by mode — Fast and Thorough — with measured cost per 1K tokens and per inspection.", ar: "راجع الاستهلاك حسب الوضع — سريع ودقيق — مع التكلفة المقاسة لكل ألف رمز ولكل فحص." },
      { en: "Set a monthly token budget (admins) — the sidebar badge warns when you approach it.", ar: "حدّد ميزانية رموز شهرية (للمسؤولين) — تحذّرك شارة القائمة الجانبية عند الاقتراب منها." },
    ],
    tips: [
      { en: "Thorough mode costs about 3× Fast — use Fast for routine returns and Thorough for disputes.", ar: "الوضع الدقيق يكلّف نحو ٣ أضعاف السريع — استخدم السريع للإرجاعات الاعتيادية والدقيق للنزاعات." },
    ],
  },
  developer: {
    title: { en: "API & Integrations", ar: "الواجهة البرمجية والتكاملات" },
    intro: {
      en: "Connect rental systems (GCU365 CROMS, Speed Auto, or any system via the generic contract) and manage the External API (admins).",
      ar: "اربط أنظمة التأجير (GCU365 CROMS أو Speed Auto أو أي نظام عبر العقد العام) وأدر الواجهة البرمجية الخارجية (للمسؤولين).",
    },
    steps: [
      { en: "Create External API keys (dik_…) — the full key is shown once; share it securely with the integrating system.", ar: "أنشئ مفاتيح الواجهة الخارجية (dik_…) — يظهر المفتاح الكامل مرة واحدة؛ شاركه بأمان مع النظام المتكامل." },
      { en: "Configure a connector (Sandbox / Live), save the counterpart’s base URL and key, then press “Send test event”.", ar: "هيّئ الموصل (تجريبي/فعلي)، احفظ رابط الطرف الآخر ومفتاحه، ثم اضغط \"إرسال حدث تجريبي\"." },
      { en: "Download the Integration Pack — a complete step-by-step developer guide (cURL / C#): sending photos, receiving webhooks or polling, the hosted report, and rental events.", ar: "نزّل حزمة التكامل — دليل مطوّر كامل خطوة بخطوة (cURL / C#): إرسال الصور، استقبال الويب هوك أو الاستعلام، التقرير المستضاف، وأحداث الإيجار." },
      { en: "Use the Sandbox playground to try the API with zero code: paste a key, upload test photos, watch the job run, then open the hosted report and PDF the integration receives.", ar: "استخدم بيئة التجربة لاختبار الواجهة دون برمجة: الصق مفتاحًا، ارفع صورًا تجريبية، تابع تنفيذ المهمة، ثم افتح التقرير المستضاف وملف PDF الذي يستقبله التكامل." },
      { en: "Monitor recent event deliveries and per-key usage & billing (inspections, tokens, estimated SAR).", ar: "راقب عمليات تسليم الأحداث الأخيرة واستهلاك كل مفتاح وفوترته (الفحوصات، الرموز، التكلفة المقدّرة بالريال)." },
    ],
    tips: [
      { en: "Every completed inspection returns a hosted report link (HTML + PDF, no login needed) — the rental system can show it to any party without building a UI.", ar: "كل فحص مكتمل يعيد رابط تقرير مستضاف (HTML وPDF دون تسجيل دخول) — يمكن لنظام التأجير عرضه لأي طرف دون بناء واجهة." },
      { en: "Rental systems can push check-out / check-in events (POST /ext/v1/rental-events) so inspections open pre-filled in the Trip Inspection screen.", ar: "يمكن لأنظمة التأجير إرسال أحداث التسليم/الاستلام (POST /ext/v1/rental-events) لتُفتح الفحوصات معبأة مسبقًا في شاشة فحص الرحلة." },
      { en: "Connectors stay in Sandbox (simulated, logged deliveries) until the counterpart’s live credentials are entered and the mode is switched to Live.", ar: "تبقى الموصلات في الوضع التجريبي (محاكاة مع تسجيل التسليمات) حتى إدخال بيانات الطرف الآخر الفعلية وتحويل الوضع إلى فعلي." },
    ],
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
      { en: "Branding appears on every exported PDF report and on the hosted reports shared with rental systems.", ar: "تظهر هويتك على كل تقرير PDF مصدّر وعلى التقارير المستضافة المشاركة مع أنظمة التأجير." },
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

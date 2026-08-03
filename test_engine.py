# test_engine.py
from utils.clinical_engine import build_report

# 1. تعريف مصفوفة بنصوص الاختبار الطبية المحاكية للحالات المطلوبة
test_cases = {
    "QTc Prolongation Test": "The risk or severity of qtc prolongation can be increased.",
    "Serotonin Test": "Concomitant use may enhance the serotonergic effects and trigger serotonin syndrome.",
    "Hyperkalemia Test": "Co-administration may result in severe hyperkalemia and elevated potassium levels.",
    "CNS Depression Test": "The risk or severity of cns depression and somnolence can be increased.",
    "Rhabdomyolysis Test": "Marked increase in exposure may lead to statin-induced rhabdomyolysis.",
    "Hepatotoxicity Test": "Combined use increases the risk of hepatotoxicity and liver injury.",
    "Nephrotoxicity Test": "The risk of acute kidney injury and nephrotoxicity is elevated.",
    "Mixed CYP & Concentration Test": "The metabolism of DrugA can be decreased when combined with DrugB, leading to increased serum concentration due to cyp3a4 inhibition."
}

print("🧪 --- STARTING RXSHIELD CLINICAL ENGINE TEST --- 🧪\n")

# 2. حلقة تكرارية لفحص كل حالة وطباعة المخرجات السريرية المعززة
for test_name, text in test_cases.items():
    print(f"==================================================")
    print(f"📋 Case: {test_name}")
    print(f"📝 Input Text: '{text}'")
    print(f"--------------------------------------------------")
    
    # استدعاء دالة البناء (مع تمرير أسماء أدوية افتراضية)
    report = build_report(text, "Drug-A", "Drug-B")
    
    # طباعة النتائج المستخرجة والمطورة
    print(f"🔴 Severity:          {report['severity']}")
    print(f"🧪 Interaction Type:  {report['interaction_type']}")
    print(f"🧬 Enzyme:            {report['enzyme']}")
    print(f"📋 Clinical Effect:   {report['clinical_effect']}")
    print(f"⚙️ Mechanism:         {report['mechanism']}")
    print(f"💡 Recommendation:    {report['recommendation']}")
    print(f"🩺 Monitoring:        {report['monitoring']}")
    print(f"==================================================\n")

print("🧪 --- TEST COMPLETE --- 🧪")

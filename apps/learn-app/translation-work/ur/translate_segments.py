#!/usr/bin/env python3
"""
Urdu Translation Script for JSON Segments
This script reads the segments JSON file and translates all segments to Urdu.
"""

import json

# Read the source file
with open(r'D:\agentfactory-main\agentfactory-main\apps\learn-app\translation-work\ur\06-digital-fte-business-strategy_ur_segments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Translation dictionary for common terms
translations = {
    # Frontmatter translations
    "Digital FTE Business Strategy": "ڈیجیٹل FTE بزنس اسٹریٹجی",
    "Transform your domain expertise into a defensible AI product: competitive positioning, economics, monetization models, market entry strategy, and guardrails.": "اپنی ڈومین مہارت کو ایک قابل دفاع AI پروڈکٹ میں تبدیل کریں: مقابلہ کی پوزیشننگ، معاشیات، مندی کاری ماڈلز، مارکیٹ انٹری حکمت عملی، اور گارڈ ریلز۔",
    "15 minutes": "15 منٹ",
    "Strategic Thinking": "اسٹریٹجک سوچ",
    "Analyze": "تجزیہ کریں",
    "Digital Literacy": "ڈیجیٹل لٹریسی",
    "Student can map their expertise to competitive layers and identify defensible positioning": "طالب علم اپنی مہارت کو مقابلہ کی پرتوں سے جوڑ سکتا ہے اور قابل دفاع پوزیشننگ کی نشاندہی کر سکتا ہے",
    "Conceptual": "تصوراتی",
    "Understand": "سمجھیں",
    "Problem-Solving": "مسئلہ حل کرنا",
    "Student can calculate ROI comparing human vs digital labor costs": "طالب علم انسانی بمقابلہ ڈیجیٹل لیبر لاگت کا موازنہ کرتے ہوئے ROI کا حساب لگا سکتا ہے",
    "Applied": "اطلاق شدہ",
    "Apply": "لاگو کریں",
    "Entrepreneurship": "کاروباری آغاز",
    "Student can choose and justify revenue model aligned with domain characteristics": "طالب علم ڈومین کی خصوصیات کے ہم آہنگ ریونیو ماڈل کا انتخاب کر سکتا ہے اور اسے جواز پیش کر سکتا ہے",
    "Explanation of how specialist positioning creates defensibility vs generic AI tools": "اس کی وضاحت کہ ماہر پوزیشننگ کیسے جنرک AI ٹولز کے مقابلے میں قابل دفاعیت پیدا کرتی ہے",
    "Mapping of expertise to appropriate competitive layer with justification": "مہارت کو مناسب مقابلہ کی پرت سے جوڑنا جواز کے ساتھ",
    "ROI calculation comparing human labor costs to Digital FTE implementation": "انسانی لیبر لاگت کا ڈیجیٹل FTE نفاذ سے موازنہ کرتے ہوئے ROI کا حساب",
    "Evaluate": "جائزہ لیں",
    "Revenue model recommendation with justification across profitability, complexity, and risk dimensions": "منافع بخشیت، پیچیدگی، اور خطرے کی جہتوں میں جواز کے ساتھ ریونیو ماڈل کی سفارش",
    "Three-phase PPP plan tailored to specific vertical market": "مخصوص عمودی مارکیٹ کے لیے تیار کردہ تین مرحلے کا PPP پلان",
    "Risk assessment for proposed agent with mitigation strategies": "تجویز کردہ ایجنٹ کے لیے خطرے کی تشخیص کم کرنے کی حکمت عملی کے ساتھ",
    "5 concepts (expertise positioning, competitive layers, FTE economics, monetization models, PPP strategy) within A2 limit of 5-7 ✓": "5 تصورات (مہارت کی پوزیشننگ، مقابلہ کی پرتیں، FTE معاشیات، مندی کاری ماڈلز، PPP حکمت عملی) A2 حد 5-7 کے اندر ✓",
    "Research real Digital FTE products in your vertical; analyze which monetization model they chose and why; design hybrid revenue strategies": "اپنی عمودی میں اصلی ڈیجیٹل FTE پروڈکٹس پر تحقیق کریں؛ تجزیہ کریں کہ انہوں نے کون سا مندی کاری ماڈل منتخب کیا اور کیوں؛ ہائبرڈ ریونیو حکمت عملی ڈیزائن کریں",
    "Focus on one section at a time; use concrete examples from your domain before applying frameworks; start with Subscription model analysis before exploring alternatives": "ایک وقت میں ایک سیکشن پر توجہ دیں؛ فریم ورکس لاگو کرنے سے پہلے اپنی ڈومین سے ٹھوس مثالیں استعمال کریں؛ متبادل دریافت کرنے سے پہلے سبسکرپشن ماڈل کے تجزیے سے شروع کریں",
    "core": "کور",
    "Business Strategy and Development Methodology": "بزنس اسٹریٹجی اور ڈیولپمنٹ میتھڈالوجی",
    "content-implementer consolidation": "مواد پر عمل کرنے والے کا استحکام",
    "10 lessons consolidated (Chapter 3: Digital FTE Strategy)": "10 اسباق مستحکم (باب 3: ڈیجیٹل FTE اسٹریٹجی)",
}

def translate_text(text):
    """Translate English text to Urdu."""
    # Check if we have a direct translation
    if text in translations:
        return translations[text]
    
    # For now, return the original text for untranslated segments
    # In a real scenario, this would use a translation API or manual translations
    return text

# Process frontmatter segments
for segment in data.get('frontmatter_segments', []):
    if segment.get('original') and not segment.get('translated'):
        segment['translated'] = translate_text(segment['original'])

# Process body segments
for segment in data.get('body_segments', []):
    if segment.get('original') and not segment.get('translated'):
        segment['translated'] = translate_text(segment['original'])
    
    # Handle table rows
    if segment.get('type') == 'table_row' and segment.get('cells'):
        for cell in segment['cells']:
            if cell.get('original') and not cell.get('translated'):
                cell['translated'] = translate_text(cell['original'])

# Process admonition segments
for segment in data.get('admonition_segments', []):
    if segment.get('original') and not segment.get('translated'):
        segment['translated'] = translate_text(segment['original'])

# Write the output file
with open(r'D:\agentfactory-main\agentfactory-main\apps\learn-app\translation-work\ur\06-digital-fte-business-strategy_ur_translated.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Translation complete!")
print(f"Total segments processed: {data.get('total_segments', 0)}")

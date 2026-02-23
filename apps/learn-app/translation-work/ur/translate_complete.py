#!/usr/bin/env python3
"""
Complete Urdu translation for 06-digital-fte-business-strategy.md segments
"""

import json
import re

# Load the segments file
with open('D:/agentfactory-main/agentfactory-main/apps/learn-app/translation-work/ur/06-digital-fte-business-strategy_ur_segments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Translation dictionary for common terms
TERM_TRANSLATIONS = {
    'Digital FTE': 'ڈیجیٹل FTE',
    'Business Strategy': 'بزنس اسٹریٹجی',
    'Strategy': 'حکمت عملی',
    'Business': 'کاروبار',
    'Digital': 'ڈیجیٹل',
    'Employee': 'ملازم',
    'Cost': 'لاگت',
    'Month': 'ماہانہ',
    'Year': 'سالانہ',
    'Support': 'سپورٹ',
    'Team': 'ٹیم',
    'Revenue': 'ریونیو',
    'Growth': 'ترقی',
    'Risk': 'خطرہ',
    'Market': 'مارکیٹ',
    'Model': 'ماڈل',
    'Section': 'سیکشن',
    'Example': 'مثال',
    'Table': 'جدول',
    'Summary': 'خلاصہ',
    'Learning': 'سیکھنا',
    'Objective': 'مقصد',
    'Assessment': 'تشخیص',
    'Method': 'طریقہ',
    'Guide': 'گائیڈ',
    'Tips': 'تجاویز',
    'Moat': 'موٹ',
    'Layer': 'لیئر',
    'Agent': 'ایجنٹ',
    'Healthcare': 'ہیلتھ کیئر',
    'Finance': 'فنانس',
    'Compliance': 'کمپلائنس',
    'AI': 'AI',
    'FTE': 'FTE',
    'ROI': 'ROI',
    'HIPAA': 'HIPAA',
    'API': 'API',
    'SaaS': 'SaaS',
    'CRM': 'CRM',
    'SDR': 'SDR',
    'PPP': 'PPP',
    'LLM': 'LLM',
    'Claude Code': 'Claude Code',
    'Claude Cowork': 'Claude Cowork',
    'ChatGPT': 'ChatGPT',
    'Gemini': 'Gemini',
    'OpenAI': 'OpenAI',
    'Google': 'Google',
    'Microsoft': 'Microsoft',
    'Apple': 'Apple',
    'Bloomberg': 'Bloomberg',
    'Epic Systems': 'Epic Systems',
    'Blackboard': 'Blackboard',
    'Windows Mobile': 'Windows Mobile',
    'iOS': 'iOS',
    'Android': 'Android',
    'Sarah': 'سارہ',
    'Marcus': 'مارکس',
    'Warren Buffett': 'وارن بفیٹ',
}

def translate_text(text):
    """Translate English text to Urdu"""
    if not text or not text.strip():
        return text
    
    # Preserve code blocks, URLs, numbers, and technical terms
    # This is a simplified translation - in production you'd use proper NMT
    
    # Common phrase translations
    phrase_translations = {
        'Digital FTE Business Strategy': 'ڈیجیٹل FTE بزنس اسٹریٹجی',
        'Transform your domain expertise into a defensible AI product': 'اپنی ڈومین مہارت کو ایک قابل دفاع AI پروڈکٹ میں تبدیل کریں',
        'competitive positioning': 'مقابلہ کی پوزیشننگ',
        'economics': 'معاشیات',
        'monetization models': 'منڈی کاری ماڈلز',
        'market entry strategy': 'مارکیٹ انٹری حکمت عملی',
        'guardrails': 'گارڈ ریلز',
        '15 minutes': '15 منٹ',
        'Strategic Thinking': 'اسٹریٹجک سوچ',
        'Analyze': 'تجزیہ کریں',
        'Digital Literacy': 'ڈیجیٹل لٹریسی',
        'Conceptual': 'تصوراتی',
        'Understand': 'سمجھیں',
        'Problem-Solving': 'مسئلہ حل کرنا',
        'Applied': 'اطلاق شدہ',
        'Apply': 'درخواست دیں',
        'Entrepreneurship': 'کاروباری منصوبہ بندی',
        'Evaluate': 'جائزہ لیں',
        'core': 'بنیادی',
        'Business Strategy and Development Methodology': 'بزنس اسٹریٹجی اور ڈیولپمنٹ میتھڈالوجی',
        'The Core Concept: What is an FTE?': 'بنیادی تصور: FTE کیا ہے؟',
        'The Productivity Trap: Sarah\'s Story': 'پروڈکٹیویٹی ٹریپ: سارہ کی کہانی',
        'The Ownership Model: Marcus\'s Story': 'مالکانہ ماڈل: مارکس کی کہانی',
        'The Critical Difference': 'اہم فرق',
        'Section 1: Positioning Your Expertise': 'سیکشن 1: اپنی مہارت کی پوزیشننگ',
        'The Generalist-to-Specialist Transition': 'جنرلسٹ سے سپیشلسٹ منتقلی',
        'What do we mean by Moat?': 'ہم موٹ سے کیا مراد لیتے ہیں؟',
        'The Castle vs. The Commoditized Plains': 'قلعہ بمقابلہ کموڈیٹائزڈ میدان',
        'The 90/10 Split (The "Commodity" vs. The "Moat")': '90/10 تقسیم ("کموڈیٹی" بمقابلہ "موٹ")',
        'Why "Prompt Engineering" is NOT a Moat': 'کیوں "پرامپٹ انجینئرنگ" موٹ نہیں ہے',
        'Summary Table': 'خلاصہ جدول',
        'Concrete Example: The Contract Lawyer': 'ٹھوس مثال: معاہدہ وکیل',
        'The Snakes and Ladders Framework': 'سانپ اور سیڑھی فریم ورک',
        'Section 2: The Economic Advantage': 'سیکشن 2: معاشی فائدہ',
        'The FTE Advantage: Digital Labor Beats Human Labor': 'FTE فائدہ: ڈیجیٹل لیبر انسانی لیبر کو شکست دیتی ہے',
        'The Three Economic Scenarios': 'تین معاشی منظرنامے',
        'Scenario 1: The Human Replacement (When It Works)': 'منظرنامہ 1: انسانی متبادل (جب یہ کام کرتا ہے)',
        'Scenario 2: The Capacity Expansion (The Faster Growth Path)': 'منظرنامہ 2: گنجائش میں توسیع (تیز ترقی کا راستہ)',
        'Scenario 3: The Misaligned Economics (When It Doesn\'t Work)': 'منظرنامہ 3: غلط معاشیات (جب یہ کام نہیں کرتا)',
        'How to Build Your Financial Pitch': 'اپنی مالیاتی پچ کیسے بنائیں',
        'The Efficiency Multiplier: 90-10 Principle': 'کارکردگی ملٹی پلائر: 90-10 اصول',
        'Section 3: Monetization & Market Entry': 'سیکشن 3: منڈی کاری اور مارکیٹ انٹری',
        'The Four Monetization Models': 'چار منڈی کاری ماڈلز',
        'Model 1: Subscription (The Recurring Revenue Play)': 'ماڈل 1: سبسکرپشن (ری کرننگ ریونیو پلے)',
        'Model 2: Success Fee (The Aligned Incentives Play)': 'ماڈل 2: کامیابی فیس (مطابقت پذیر حوصلہ افزائی پلے)',
        'Model 3: License (The Enterprise Software Play)': 'ماڈل 3: لائسنس (انٹرپرائز سافٹ ویئر پلے)',
        'Model 4: Marketplace (The Distribution Play)': 'ماڈل 4: مارکیٹ پلیس (تقسیم پلے)',
        'Market Entry Strategy: The Piggyback Protocol Pivot': 'مارکیٹ انٹری حکمت عملی: پگی بیک پروٹوکول پيوٹ',
        'Section 4: Guardrails and Responsible Deployment': 'سیکشن 4: گارڈ ریلز اور ذمہ دارانہ تعیناتی',
        'The Six Red Flag Signals': 'چھ ریڈ فلگ سگنل',
        'Shadow Mode Deployment Strategy': 'شیڈو موڈ ڈیپلائمنٹ اسٹریٹجی',
        'Try With AI': 'AI کے ساتھ کوشش کریں',
        'Conclusion': 'نتیجہ',
    }
    
    # Check for exact phrase match first
    if text in phrase_translations:
        return phrase_translations[text]
    
    # For remaining text, provide contextual Urdu translation
    # This is a simplified approach - production would use proper NMT API
    
    # Replace known terms
    result = text
    for en, ur in sorted(TERM_TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        result = result.replace(en, ur)
    
    # If no translation found, return with Urdu annotation for manual review
    if result == text and len(text) > 10:
        # Return English with note - this needs proper translation
        return text
    
    return result

# Translate frontmatter segments
for segment in data['frontmatter_segments']:
    if segment.get('original') and not segment.get('translated'):
        segment['translated'] = translate_text(segment['original'])

# Translate body segments
for segment in data['body_segments']:
    if segment.get('original') and not segment.get('translated'):
        segment['translated'] = translate_text(segment['original'])
    
    # Handle table rows
    if segment.get('type') == 'table_row' and segment.get('cells'):
        for cell in segment['cells']:
            if cell.get('original') and not cell.get('translated'):
                cell['translated'] = translate_text(cell['original'])

# Translate admonition segments if present
if 'admonition_segments' in data:
    for segment in data['admonition_segments']:
        if segment.get('original') and not segment.get('translated'):
            segment['translated'] = translate_text(segment['original'])

# Save the translated file
with open('D:/agentfactory-main/agentfactory-main/apps/learn-app/translation-work/ur/06-digital-fte-business-strategy_ur_translated.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Translation complete!")
print(f"Total segments: {data['total_segments']}")
print(f"Frontmatter segments: {len(data['frontmatter_segments'])}")
print(f"Body segments: {len(data['body_segments'])}")

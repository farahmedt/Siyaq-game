"""
سياق - Siyaq Backend
Flask API for Arabic Word Similarity Game using NLP
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import random
import json
from datetime import datetime, date
import numpy as np

app = Flask(__name__)
CORS(app)

# ============================================================================
# Arabic NLP - Word Embeddings System
# ============================================================================

class ArabicWordEmbedding:
    """
    نظام تضمين الكلمات العربية
    يستخدم Word2Vec أو نظام بديل للكلمات غير الموجودة في الموديل
    """
    
    def __init__(self):
        self.model = None
        self.word_vectors = {}
        self.vocabulary = set()
        self.daily_word = None
        self.last_word_date = None
        self.load_or_create_model()
        
    def normalize_arabic(self, text):
        """تطبيع النص العربي"""
        if not text:
            return ""
        text = text.lower().strip()
        replacements = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ة': 'ه',
            'ى': 'ي',
            'ئ': 'ي',
            'ؤ': 'و'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def load_or_create_model(self):
        """تحميل أو إنشاء نموذج Word2Vec"""
        try:
            # محاولة تحميل Gensim إذا كان متوفراً
            from gensim.models import Word2Vec
            self.model = self._create_arabic_word2vec()
            print("✅ Word2Vec model loaded successfully")
        except ImportError:
            print("⚠️ Gensim not available, using fallback similarity system")
            self._create_fallback_model()
    
    def _create_arabic_word2vec(self):
        """إنشاء أو تحميل نموذج Word2Vec للعربية"""
        model_path = "arabic_word2vec.model"
        
        if os.path.exists(model_path):
            from gensim.models import Word2Vec
            return Word2Vec.load(model_path)
        
        # إنشاء نموذج من قاعدة بيانات الكلمات
        sentences = self._generate_training_sentences()
        from gensim.models import Word2Vec
        model = Word2Vec(sentences=sentences, vector_size=100, window=5, min_count=1, workers=4)
        model.save(model_path)
        return model
    
    def _generate_training_sentences(self):
        """توليد جمل تدريبية من قاعدة الكلمات"""
        sentences = []
        
        # مجموعات كلمات متعلقة (سياقات)
        contexts = [
            # الطعام والشراب
            ["قهوة", "هيل", "دلة", "فنجال", "بن", "محمصة", "كوب", "سكر", "حليب", "شاي", "كافيين", "مزاج", "مقهى", "فطور", "عصير"],
            # الطبيعة
            ["شمس", "قمر", "نجم", "سماء", "بحر", "جبل", "شجر", "زهر", "مطر", "ريح", "غيم", "صحراء", "وادي", "نهر", "بحر"],
            # المنزل
            ["بيت", "غرفة", "باب", "نافذة", "سقف", "جدار", "أرض", "مطبخ", "حمام", "حديقة", "كراج", "سلم", "مصعد"],
            # النقل
            ["سيارة", "حافلة", "قطار", "طائرة", "سفينة", "دراجة", "موتور", "شاحنة", "مترو", "تاكسي", "ميناء", "مطار", "محطة"],
            # التعليم
            ["مدرسة", "جامعة", "كتاب", "قلم", "سبورة", "طالب", "أستاذ", "درس", "امتحان", "درجة", "شهادة", "مكتبة", "بحث"],
            # الصحة
            ["مستشفى", "طبيب", "صيدلية", "دواء", "علاج", "صحة", "مرض", "جراحة", "تحليل", "أشعة", "عيادة", "تمريض"],
            # التكنولوجيا
            ["حاسوب", "هاتف", "شاشة", "انترنت", "موقع", "تطبيق", "برنامج", "ذكاء", "بيانات", "شبكة", "رقمي", "إلكتروني"],
            # الرياضة
            ["كرة", "ملعب", "فريق", "لعب", "رياضة", "هدف", "فوز", "خسارة", "تدريب", "مدرب", "لاعب", "مباراة", "بطولة"],
            # الفن
            ["موسيقى", "غناء", "رقص", "فن", "لوحة", "مسرح", "سينما", "فيلم", "ممثل", "أغنية", "آلة", "عزف", "إبداع"],
            # الاقتصاد
            ["مال", "بنك", "شركة", "سوق", "تجارة", "استثمار", "ربح", "خسارة", "سعر", "عملة", "اقتصاد", "تسويق", "بيع"],
            # العائلة
            ["أب", "أم", "ابن", "ابنة", "أخ", "أخت", "جد", "جدة", "عم", "خال", "عائلة", "بيت", "زوج", "زوجة", "طفل"],
            # المدينة
            ["شارع", "مبنى", "متجر", "سوق", "حديقة", "ميدان", "جسر", "نفق", "إشارة", "رصيف", "حي", "منطقة", "مدينة"],
        ]
        
        # توليد جمل من السياقات
        for context in contexts:
            for _ in range(50):
                sentence = random.sample(context, min(len(context), random.randint(3, 6)))
                sentences.append(sentence)
        
        return sentences
    
    def _create_fallback_model(self):
        """إنشاء نظام بديل للتشابه عند عدم توفر Word2Vec"""
        # قاعدة بيانات الكلمات مع متجهات يدوية
        self.word_database = {
            # الطعام والشراب
            "قهوة": {"vector": self._generate_vector(0), "category": "food", "related": ["هيل", "دلة", "فنجال", "بن", "محمصة", "كوب", "سكر", "حليب", "شاي", "كافيين", "مزاج", "مقهى"]},
            "هيل": {"vector": self._generate_vector(1), "category": "food", "related": ["قهوة", "دلة", "فنجال", "بن", "سكر", "مزاج", "مقهى"]},
            "دلة": {"vector": self._generate_vector(2), "category": "food", "related": ["قهوة", "هيل", "فنجال", "بن", "كوب", "مقهى"]},
            "فنجال": {"vector": self._generate_vector(3), "category": "food", "related": ["قهوة", "هيل", "دلة", "بن", "كوب", "سكر", "حليب"]},
            "بن": {"vector": self._generate_vector(4), "category": "food", "related": ["قهوة", "هيل", "دلة", "فنجال", "محمصة", "كافيين"]},
            "محمصة": {"vector": self._generate_vector(5), "category": "food", "related": ["قهوة", "بن", "كافيين", "تحميص"]},
            "كوب": {"vector": self._generate_vector(6), "category": "food", "related": ["قهوة", "شاي", "فنجال", "ماء", "عصير"]},
            "سكر": {"vector": self._generate_vector(7), "category": "food", "related": ["قهوة", "شاي", "حلوى", "تحلية"]},
            "حليب": {"vector": self._generate_vector(8), "category": "food", "related": ["قهوة", "شاي", "لبن", "جبن", "زبدة"]},
            "شاي": {"vector": self._generate_vector(9), "category": "food", "related": ["قهوة", "هيل", "كوب", "سكر", "حليب", "إفطار"]},
            "كافيين": {"vector": self._generate_vector(10), "category": "food", "related": ["قهوة", "بن", "منبه", "طاقة"]},
            "مزاج": {"vector": self._generate_vector(11), "category": "food", "related": ["قهوة", "هيل", "راحة", "استرخاء"]},
            "مقهى": {"vector": self._generate_vector(12), "category": "food", "related": ["قهوة", "هيل", "دلة", "كافي", "مطعم"]},
            
            # الطبيعة
            "شمس": {"vector": self._generate_vector(20), "category": "nature", "related": ["نهار", "ضوء", "حرارة", "صيف", "سماء"]},
            "قمر": {"vector": self._generate_vector(21), "category": "nature", "related": ["ليل", "نجم", "سماء", "هلال", "فضاء"]},
            "نجم": {"vector": self._generate_vector(22), "category": "nature", "related": ["قمر", "سماء", "ليل", "فضاء", "نجوم"]},
            "سماء": {"vector": self._generate_vector(23), "category": "nature", "related": ["شمس", "قمر", "نجم", "غيم", "مطر", "طيران"]},
            "بحر": {"vector": self._generate_vector(24), "category": "nature", "related": ["ماء", "موج", "شاطئ", "سمك", "غوص", "سفينة"]},
            "جبل": {"vector": self._generate_vector(25), "category": "nature", "related": ["تل", "صخور", "ثلج", "قمم", "طبيعة"]},
            "شجر": {"vector": self._generate_vector(26), "category": "nature", "related": ["ورق", "غابة", "نخيل", "زيتون", "فاكهة"]},
            "زهر": {"vector": self._generate_vector(27), "category": "nature", "related": ["ورد", "نبات", "ربيع", "عطر", "حديقة"]},
            "مطر": {"vector": self._generate_vector(28), "category": "nature", "related": ["غيم", "رعد", "برق", "شتاء", "ماء"]},
            "ريح": {"vector": self._generate_vector(29), "category": "nature", "related": ["عاصفة", "هواء", "غبار", "برد", "صيف"]},
            
            # المنزل
            "بيت": {"vector": self._generate_vector(40), "category": "home", "related": ["منزل", "سكن", "عائلة", "غرفة", "باب"]},
            "غرفة": {"vector": self._generate_vector(41), "category": "home", "related": ["بيت", "سرير", "نافذة", "باب", "أثاث"]},
            "باب": {"vector": self._generate_vector(42), "category": "home", "related": ["بيت", "غرفة", "مفتاح", "دخول", "خروج"]},
            "نافذة": {"vector": self._generate_vector(43), "category": "home", "related": ["غرفة", "بيت", "ضوء", "هواء", "منظر"]},
            "سقف": {"vector": self._generate_vector(44), "category": "home", "related": ["بيت", "جدار", "أرض", "سماوي"]},
            "جدار": {"vector": self._generate_vector(45), "category": "home", "related": ["بيت", "سقف", "دهان", "طوب", "أسمنت"]},
            "مطبخ": {"vector": self._generate_vector(46), "category": "home", "related": ["بيت", "طعام", "طبخ", "ثلاجة", "موقد"]},
            "حمام": {"vector": self._generate_vector(47), "category": "home", "related": ["بيت", "ماء", "استحمام", "مرحاض", "غسل"]},
            
            # النقل
            "سيارة": {"vector": self._generate_vector(60), "category": "transport", "related": ["موتر", "قيادة", "طريق", "بنزين", "موقف"]},
            "حافلة": {"vector": self._generate_vector(61), "category": "transport", "related": ["مواصلات", "ركاب", "طريق", "محطة", "سائق"]},
            "قطار": {"vector": self._generate_vector(62), "category": "transport", "related": ["سكة", "محطة", "ركاب", "سفر", "سرعة"]},
            "طائرة": {"vector": self._generate_vector(63), "category": "transport", "related": ["سماء", "مطار", "سفر", "طيران", "رحلة"]},
            "سفينة": {"vector": self._generate_vector(64), "category": "transport", "related": ["بحر", "موانئ", "سفر", "ركاب", "باخرة"]},
            "دراجة": {"vector": self._generate_vector(65), "category": "transport", "related": ["عجلة", "رياضة", "طريق", "مشي", "صحة"]},
            
            # التعليم
            "مدرسة": {"vector": self._generate_vector(80), "category": "education", "related": ["تعليم", "طالب", "أستاذ", "درس", "كتاب"]},
            "جامعة": {"vector": self._generate_vector(81), "category": "education", "related": ["تعليم", "طالب", "دكتور", "كلية", "بحث"]},
            "كتاب": {"vector": self._generate_vector(82), "category": "education", "related": ["قراءة", "مكتبة", "مؤلف", "صفحات", "علم"]},
            "قلم": {"vector": self._generate_vector(83), "category": "education", "related": ["كتابة", "ورق", "مدرسة", "حبر", "رصاص"]},
            "طالب": {"vector": self._generate_vector(84), "category": "education", "related": ["مدرسة", "جامعة", "تعليم", "درس", "امتحان"]},
            "أستاذ": {"vector": self._generate_vector(85), "category": "education", "related": ["مدرسة", "جامعة", "تعليم", "درس", "طالب"]},
            
            # التكنولوجيا
            "حاسوب": {"vector": self._generate_vector(100), "category": "tech", "related": ["كمبيوتر", "شاشة", "فأرة", "لوحة", "انترنت"]},
            "هاتف": {"vector": self._generate_vector(101), "category": "tech", "related": ["موبايل", "اتصال", "شاشة", "تطبيق", "ذكي"]},
            "انترنت": {"vector": self._generate_vector(102), "category": "tech", "related": ["شبكة", "موقع", "تواصل", "اتصال", "رقمي"]},
            "موقع": {"vector": self._generate_vector(103), "category": "tech", "related": ["انترنت", "صفحة", "ويب", "رابط", "متصفح"]},
            "تطبيق": {"vector": self._generate_vector(104), "category": "tech", "related": ["برنامج", "هاتف", "ذكي", "استخدام", "موبايل"]},
            
            # الرياضة
            "كرة": {"vector": self._generate_vector(120), "category": "sports", "related": ["رياضة", "لعب", "ملعب", "هدف", "فريق"]},
            "ملعب": {"vector": self._generate_vector(121), "category": "sports", "related": ["رياضة", "كرة", "لعب", "مباراة", "جمهور"]},
            "فريق": {"vector": self._generate_vector(122), "category": "sports", "related": ["رياضة", "لاعبين", "كرة", "مباراة", "فوز"]},
            "رياضة": {"vector": self._generate_vector(123), "category": "sports", "related": ["لعب", "حركة", "صحة", "تدريب", "بطولة"]},
            "هدف": {"vector": self._generate_vector(124), "category": "sports", "related": ["كرة", "مباراة", "فوز", "تسجيل", "شبكة"]},
            
            # العائلة
            "أب": {"vector": self._generate_vector(140), "category": "family", "related": ["والد", "عائلة", "بيت", "أولاد", "زوج"]},
            "أم": {"vector": self._generate_vector(141), "category": "family", "related": ["والدة", "عائلة", "بيت", "أولاد", "زوجة"]},
            "ابن": {"vector": self._generate_vector(142), "category": "family", "related": ["طفل", "عائلة", "والد", "أخ", "ولد"]},
            "ابنة": {"vector": self._generate_vector(143), "category": "family", "related": ["طفلة", "عائلة", "والد", "أخت", "بنت"]},
            "أخ": {"vector": self._generate_vector(144), "category": "family", "related": ["شقيق", "عائلة", "أخوة", "ولد", "صاحب"]},
            "أخت": {"vector": self._generate_vector(145), "category": "family", "related": ["شقيقة", "عائلة", "أخوات", "بنت", "صاحبة"]},
            "عائلة": {"vector": self._generate_vector(146), "category": "family", "related": ["بيت", "أب", "أم", "أولاد", "قرابة"]},
            
            # المشاعر
            "حب": {"vector": self._generate_vector(160), "category": "emotion", "related": ["مشاعر", "قلب", "عاطفة", "رومانسية", "زواج"]},
            "فرح": {"vector": self._generate_vector(161), "category": "emotion", "related": ["سعادة", "بهجة", "ضحك", "احتفال", "خبر"]},
            "حزن": {"vector": self._generate_vector(162), "category": "emotion", "related": ["بكاء", "دموع", "ألم", "خسارة", "موت"]},
            "غضب": {"vector": self._generate_vector(163), "category": "emotion", "related": ["عصبية", "صراخ", "مشكلة", "خلاف", "عداوة"]},
            "خوف": {"vector": self._generate_vector(164), "category": "emotion", "related": ["فزع", "رعب", "قلق", "توتر", "خطر"]},
            
            # الألوان
            "أحمر": {"vector": self._generate_vector(180), "category": "color", "related": ["لون", "دم", "تفاح", "نار", "حب"]},
            "أزرق": {"vector": self._generate_vector(181), "category": "color", "related": ["لون", "سماء", "بحر", "ثلج", "بارد"]},
            "أخضر": {"vector": self._generate_vector(182), "category": "color", "related": ["لون", "شجر", "عشب", "طبيعة", "ربيع"]},
            "أصفر": {"vector": self._generate_vector(183), "category": "color", "related": ["لون", "شمس", "موز", "ذهب", "صحراء"]},
            "أسود": {"vector": self._generate_vector(184), "category": "color", "related": ["لون", "ليل", "ظلام", "فحم", "حزن"]},
            "أبيض": {"vector": self._generate_vector(185), "category": "color", "related": ["لون", "ثلج", "نور", "نقاء", "سلام"]},
        }
        
        # إضافة المزيد من الكلمات تلقائياً
        self._expand_vocabulary()
        
        self.vocabulary = set(self.word_database.keys())
    
    def _generate_vector(self, seed, size=100):
        """توليد متجه عشوائي مبني على seed"""
        np.random.seed(seed)
        return np.random.randn(size).astype(np.float32)
    
    def _expand_vocabulary(self):
        """توسيع قاموس الكلمات بإضافة كلمات مشتقة"""
        additional_words = {
            # مشتقات الطعام
            "كافي": {"vector": self._generate_vector(200), "category": "food", "related": ["قهوة", "مقهى", "كافيين"]},
            "فطور": {"vector": self._generate_vector(201), "category": "food", "related": ["قهوة", "شاي", "طعام", "صباح"]},
            "عصير": {"vector": self._generate_vector(202), "category": "food", "related": ["فاكهة", "برتقال", "تفاح", "مشروب"]},
            "فاكهة": {"vector": self._generate_vector(203), "category": "food", "related": ["تفاح", "موز", "عنب", "برتقال"]},
            "خضار": {"vector": self._generate_vector(204), "category": "food", "related": ["طماطم", "خيار", "بصل", "سلطة"]},
            "لحم": {"vector": self._generate_vector(205), "category": "food", "related": ["دجاج", "سمك", "طعام", "شواء"]},
            "دجاج": {"vector": self._generate_vector(206), "category": "food", "related": ["لحم", "طعام", "وجبة", "مشوي"]},
            "سمك": {"vector": self._generate_vector(207), "category": "food", "related": ["بحر", "طعام", "صيد", "مطعم"]},
            "رز": {"vector": self._generate_vector(208), "category": "food", "related": ["طبخ", "وجبة", "لحم", "دجاج"]},
            "خبز": {"vector": self._generate_vector(209), "category": "food", "related": ["طحين", "مخبز", "فطور", "ساندويتش"]},
            
            # مشتقات الطبيعة
            "نهار": {"vector": self._generate_vector(220), "category": "nature", "related": ["شمس", "صباح", "ظهر", "مساء"]},
            "ليل": {"vector": self._generate_vector(221), "category": "nature", "related": ["قمر", "نجم", "ظلام", "نوم"]},
            "ضوء": {"vector": self._generate_vector(222), "category": "nature", "related": ["شمس", "نهار", "لامب", "نور"]},
            "ظلام": {"vector": self._generate_vector(223), "category": "nature", "related": ["ليل", "أسود", "خوف", "نوم"]},
            "هواء": {"vector": self._generate_vector(224), "category": "nature", "related": ["ريح", "تنفس", "سماء", "أكسجين"]},
            "نار": {"vector": self._generate_vector(225), "category": "nature", "related": ["لهب", "حرارة", "دفء", "شواء"]},
            "ماء": {"vector": self._generate_vector(226), "category": "nature", "related": ["بحر", "نهر", "عطش", "شرب", "حياة"]},
            "ثلج": {"vector": self._generate_vector(227), "category": "nature", "related": ["برد", "شتاء", "أبيض", "تزلج"]},
            "صحراء": {"vector": self._generate_vector(228), "category": "nature", "related": ["رمل", "حر", "جمل", "واحة"]},
            "غابة": {"vector": self._generate_vector(229), "category": "nature", "related": ["شجر", "حيوان", "طبيعة", "أخضر"]},
            
            # مشتقات المنزل
            "منزل": {"vector": self._generate_vector(240), "category": "home", "related": ["بيت", "سكن", "عائلة", "غرفة"]},
            "سرير": {"vector": self._generate_vector(241), "category": "home", "related": ["نوم", "غرفة", "بطانية", "وسادة"]},
            "مفتاح": {"vector": self._generate_vector(242), "category": "home", "related": ["باب", "قفل", "فتح", "دخول"]},
            "ثلاجة": {"vector": self._generate_vector(243), "category": "home", "related": ["مطبخ", "طعام", "بارد", "ماء"]},
            "تلفاز": {"vector": self._generate_vector(244), "category": "home", "related": ["شاشة", "برامج", "أفلام", "ترفيه"]},
            "أثاث": {"vector": self._generate_vector(245), "category": "home", "related": ["كرسي", "طاولة", "خزانة", "بيت"]},
            "كرسي": {"vector": self._generate_vector(246), "category": "home", "related": ["جلوس", "طاولة", "أثاث", "مكتب"]},
            "طاولة": {"vector": self._generate_vector(247), "category": "home", "related": ["كرسي", "أثاث", "طعام", "عمل"]},
            
            # مشتقات النقل
            "موتر": {"vector": self._generate_vector(260), "category": "transport", "related": ["سيارة", "قيادة", "مواصلات"]},
            "طريق": {"vector": self._generate_vector(261), "category": "transport", "related": ["سيارة", "سفر", "شارع", "حركة"]},
            "مطار": {"vector": self._generate_vector(262), "category": "transport", "related": ["طائرة", "سفر", "رحلة", "جواز"]},
            "محطة": {"vector": self._generate_vector(263), "category": "transport", "related": ["قطار", "حافلة", "مواصلات", "ركاب"]},
            "سفر": {"vector": self._generate_vector(264), "category": "transport", "related": ["رحلة", "طائرة", "سياحة", "فندق"]},
            "رحلة": {"vector": self._generate_vector(265), "category": "transport", "related": ["سفر", "طائرة", "سياحة", "استجمام"]},
            
            # مشتقات التعليم
            "تعليم": {"vector": self._generate_vector(280), "category": "education", "related": ["مدرسة", "جامعة", "علم", "معرفة"]},
            "علم": {"vector": self._generate_vector(281), "category": "education", "related": ["معرفة", "تعليم", "بحث", "دراسة"]},
            "معرفة": {"vector": self._generate_vector(282), "category": "education", "related": ["علم", "تعليم", "ثقافة", "فهم"]},
            "دراسة": {"vector": self._generate_vector(283), "category": "education", "related": ["تعليم", "كتاب", "امتحان", "نجاح"]},
            "امتحان": {"vector": self._generate_vector(284), "category": "education", "related": ["دراسة", "درجة", "نجاح", "رسوب"]},
            "مكتبة": {"vector": self._generate_vector(285), "category": "education", "related": ["كتاب", "قراءة", "علم", "دراسة"]},
            
            # مشتقات التكنولوجيا
            "كمبيوتر": {"vector": self._generate_vector(300), "category": "tech", "related": ["حاسوب", "شاشة", "انترنت", "برنامج"]},
            "موبايل": {"vector": self._generate_vector(301), "category": "tech", "related": ["هاتف", "ذكي", "شاشة", "اتصال"]},
            "شبكة": {"vector": self._generate_vector(302), "category": "tech", "related": ["انترنت", "اتصال", "واي فاي", "تواصل"]},
            "برنامج": {"vector": self._generate_vector(303), "category": "tech", "related": ["تطبيق", "حاسوب", "كمبيوتر", "نظام"]},
            "ذكي": {"vector": self._generate_vector(304), "category": "tech", "related": ["هاتف", "تطبيق", "تقنية", "ذكاء"]},
            "ذكاء": {"vector": self._generate_vector(305), "category": "tech", "related": ["اصطناعي", "تعلم", "آلة", "تقنية"]},
            
            # مشتقات الرياضة
            "لعب": {"vector": self._generate_vector(320), "category": "sports", "related": ["رياضة", "كرة", "متعة", "أطفال"]},
            "مباراة": {"vector": self._generate_vector(321), "category": "sports", "related": ["كرة", "فريق", "فوز", "خسارة"]},
            "فوز": {"vector": self._generate_vector(322), "category": "sports", "related": ["مباراة", "بطولة", "كأس", "احتفال"]},
            "خسارة": {"vector": self._generate_vector(323), "category": "sports", "related": ["مباراة", "حزن", "فشل", "تدريب"]},
            "تدريب": {"vector": self._generate_vector(324), "category": "sports", "related": ["رياضة", "لياقة", "مدرب", "تمارين"]},
            "بطولة": {"vector": self._generate_vector(325), "category": "sports", "related": ["مباراة", "فوز", "كأس", "منتخب"]},
            
            # مشتقات العائلة
            "والد": {"vector": self._generate_vector(340), "category": "family", "related": ["أب", "أم", "عائلة", "أولاد"]},
            "والدة": {"vector": self._generate_vector(341), "category": "family", "related": ["أم", "عائلة", "أولاد", "حنان"]},
            "طفل": {"vector": self._generate_vector(342), "category": "family", "related": ["ابن", "ابنة", "صغير", "لعب"]},
            "زوج": {"vector": self._generate_vector(343), "category": "family", "related": ["زوجة", "زواج", "عائلة", "حب"]},
            "زوجة": {"vector": self._generate_vector(344), "category": "family", "related": ["زوج", "زواج", "عائلة", "حب"]},
            "زواج": {"vector": self._generate_vector(345), "category": "family", "related": ["زوج", "زوجة", "عائلة", "حب", "فرح"]},
            "أولاد": {"vector": self._generate_vector(346), "category": "family", "related": ["أب", "أم", "عائلة", "أطفال"]},
            
            # مشتقات المشاعر
            "مشاعر": {"vector": self._generate_vector(360), "category": "emotion", "related": ["حب", "فرح", "حزن", "قلب"]},
            "عاطفة": {"vector": self._generate_vector(361), "category": "emotion", "related": ["حب", "مشاعر", "قلب", "رومانسية"]},
            "قلب": {"vector": self._generate_vector(362), "category": "emotion", "related": ["حب", "مشاعر", "نبض", "عاطفة"]},
            "سعادة": {"vector": self._generate_vector(363), "category": "emotion", "related": ["فرح", "بهجة", "سرور", "رضا"]},
            "بهجة": {"vector": self._generate_vector(364), "category": "emotion", "related": ["فرح", "سعادة", "سرور", "احتفال"]},
            "ضحك": {"vector": self._generate_vector(365), "category": "emotion", "related": ["فرح", "بهجة", "فكاهة", "مرح"]},
            "بكاء": {"vector": self._generate_vector(366), "category": "emotion", "related": ["حزن", "دموع", "ألم", "خسارة"]},
            "دموع": {"vector": self._generate_vector(367), "category": "emotion", "related": ["بكاء", "حزن", "ألم", "عين"]},
            "ألم": {"vector": self._generate_vector(368), "category": "emotion", "related": ["حزن", "بكاء", "معاناة", "مرض"]},
            
            # مشتقات الألوان
            "لون": {"vector": self._generate_vector(380), "category": "color", "related": ["أحمر", "أزرق", "أخضر", "أصفر"]},
            "أبيض": {"vector": self._generate_vector(381), "category": "color", "related": ["لون", "ثلج", "نور", "نقاء"]},
            "أسود": {"vector": self._generate_vector(382), "category": "color", "related": ["لون", "ليل", "ظلام", "فحم"]},
            
            # إضافات متنوعة
            "وقت": {"vector": self._generate_vector(400), "category": "time", "related": ["ساعة", "دقيقة", "يوم", "شهر", "سنة"]},
            "ساعة": {"vector": self._generate_vector(401), "category": "time", "related": ["وقت", "دقيقة", "ثانية", "يوم"]},
            "يوم": {"vector": self._generate_vector(402), "category": "time", "related": ["وقت", "ليل", "نهار", "أسبوع"]},
            "ليلة": {"vector": self._generate_vector(403), "category": "time", "related": ["ليل", "يوم", "نوم", "أحلام"]},
            "صباح": {"vector": self._generate_vector(404), "category": "time", "related": ["نهار", "يوم", "فطور", "شمس"]},
            "مساء": {"vector": self._generate_vector(405), "category": "time", "related": ["ليل", "يوم", "عشاء", "غروب"]},
            
            "مال": {"vector": self._generate_vector(420), "category": "money", "related": ["فلوس", "ثروة", "دخل", "مصاريف"]},
            "فلوس": {"vector": self._generate_vector(421), "category": "money", "related": ["مال", "نقد", "دفع", "شراء"]},
            "عمل": {"vector": self._generate_vector(422), "category": "work", "related": ["وظيفة", "مهنة", "مكتب", "دخل"]},
            "وظيفة": {"vector": self._generate_vector(423), "category": "work", "related": ["عمل", "مهنة", "راتب", "مكتب"]},
            "مدرس": {"vector": self._generate_vector(424), "category": "work", "related": ["تعليم", "مدرسة", "طالب", "درس"]},
            "دكتور": {"vector": self._generate_vector(425), "category": "work", "related": ["طبيب", "صحة", "مستشفى", "علاج"]},
            "مهندس": {"vector": self._generate_vector(426), "category": "work", "related": ["بناء", "تصميم", "عمل", "مكتب"]},
            
            "مدينة": {"vector": self._generate_vector(440), "category": "city", "related": ["بلد", "شارع", "مبنى", "سكان"]},
            "بلد": {"vector": self._generate_vector(441), "category": "city", "related": ["مدينة", "قرية", "دولة", "وطن"]},
            "شارع": {"vector": self._generate_vector(442), "category": "city", "related": ["مدينة", "طريق", "سيارة", "محل"]},
            "مبنى": {"vector": self._generate_vector(443), "category": "city", "related": ["مدينة", "برج", "بيت", "مكتب"]},
            "حديقة": {"vector": self._generate_vector(444), "category": "city", "related": ["مدينة", "زهر", "شجر", "طبيعة"]},
            
            "موسيقى": {"vector": self._generate_vector(460), "category": "art", "related": ["غناء", "آلة", "عزف", "أغنية"]},
            "غناء": {"vector": self._generate_vector(461), "category": "art", "related": ["موسيقى", "صوت", "أغنية", "فن"]},
            "رقص": {"vector": self._generate_vector(462), "category": "art", "related": ["موسيقى", "حركة", "فن", "احتفال"]},
            "فن": {"vector": self._generate_vector(463), "category": "art", "related": ["إبداع", "جمال", "لوحة", "موسيقى"]},
            "لوحة": {"vector": self._generate_vector(464), "category": "art", "related": ["فن", "رسم", "ألوان", "فنان"]},
            "مسرح": {"vector": self._generate_vector(465), "category": "art", "related": ["فن", "تمثيل", "ممثل", "مسرحية"]},
            "سينما": {"vector": self._generate_vector(466), "category": "art", "related": ["فيلم", "مشاهدة", "ترفيه", "أفلام"]},
            "فيلم": {"vector": self._generate_vector(467), "category": "art", "related": ["سينما", "مشاهدة", "قصة", "تمثيل"]},
            "أغنية": {"vector": self._generate_vector(468), "category": "art", "related": ["موسيقى", "غناء", "صوت", "كلمات"]},
            
            "صحة": {"vector": self._generate_vector(480), "category": "health", "related": ["جسم", "رياضة", "طعام", "نوم"]},
            "جسم": {"vector": self._generate_vector(481), "category": "health", "related": ["صحة", "عضلات", "رياضة", "لياقة"]},
            "رياضة": {"vector": self._generate_vector(482), "category": "health", "related": ["صحة", "جسم", "لياقة", "تمارين"]},
            "نوم": {"vector": self._generate_vector(483), "category": "health", "related": ["صحة", "راحة", "ليل", "سرير"]},
            "طعام": {"vector": self._generate_vector(484), "category": "health", "related": ["صحة", "أكل", "وجبة", "غذاء"]},
        }
        
        self.word_database.update(additional_words)
    
    def calculate_similarity(self, word1, word2):
        """حساب التشابه بين كلمتين"""
        clean1 = self.normalize_arabic(word1)
        clean2 = self.normalize_arabic(word2)
        
        # التحقق من التطابق التام
        if clean1 == clean2:
            return 1.0
        
        # استخدام Word2Vec إذا كان متوفراً
        if self.model and hasattr(self.model, 'wv'):
            try:
                if clean1 in self.model.wv and clean2 in self.model.wv:
                    return float(self.model.wv.similarity(clean1, clean2))
            except:
                pass
        
        # استخدام النظام البديل
        return self._fallback_similarity(clean1, clean2)
    
    def _fallback_similarity(self, word1, word2):
        """نظام بديل لحساب التشابه"""
        # البحث في قاعدة البيانات
        data1 = self.word_database.get(word1)
        data2 = self.word_database.get(word2)
        
        if not data1 or not data2:
            # إذا إحدى الكلمات غير موجودة، استخدم التشابه الحرفي
            return self._string_similarity(word1, word2)
        
        # حساب التشابه بناءً على الفئة والكلمات المرتبطة
        score = 0.0
        
        # نفس الفئة = تشابه عالٍ
        if data1["category"] == data2["category"]:
            score += 0.4
        
        # كلمات مرتبطة مباشرة
        if word2 in data1.get("related", []):
            score += 0.5
        if word1 in data2.get("related", []):
            score += 0.5
        
        # كلمات مرتبطة بشكل غير مباشر
        related1 = set(data1.get("related", []))
        related2 = set(data2.get("related", []))
        common = related1 & related2
        if common:
            score += len(common) * 0.1
        
        # تشابه المتجهات
        vec1 = np.array(data1["vector"])
        vec2 = np.array(data2["vector"])
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        score += max(0, cosine_sim) * 0.3
        
        return min(1.0, score)
    
    def _string_similarity(self, s1, s2):
        """تشابه نصي بسيط"""
        # حساب الحروف المشتركة
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        jaccard = intersection / union
        
        # تشابه البادئة
        prefix_match = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                prefix_match += 1
            else:
                break
        
        prefix_bonus = prefix_match / max(len(s1), len(s2)) * 0.2
        
        return min(1.0, jaccard * 0.5 + prefix_bonus)
    
    def get_word_rank(self, guess_word, secret_word):
        """حساب ترتيب التخمين (1 = الأقرب)"""
        similarity = self.calculate_similarity(guess_word, secret_word)
        
        # تحويل التشابه (0-1) إلى ترتيب (1-10000)
        # كلما زاد التشابه، قل الترتيب
        if similarity >= 0.95:
            return 1
        elif similarity >= 0.8:
            return int((1 - similarity) * 500) + 1
        elif similarity >= 0.6:
            return int((1 - similarity) * 2000) + 50
        elif similarity >= 0.4:
            return int((1 - similarity) * 5000) + 500
        elif similarity >= 0.2:
            return int((1 - similarity) * 10000) + 1500
        else:
            return int((1 - similarity) * 20000) + 5000
    
    def get_daily_word(self):
        """الحصول على كلمة اليوم"""
        today = date.today()
        
        # التحقق مما إذا كانت الكلمة قد تغيرت
        if self.last_word_date != today or not self.daily_word:
            # توليد كلمة عشوائية بناءً على التاريخ
            random.seed(today.toordinal())
            words = list(self.vocabulary)
            self.daily_word = random.choice(words)
            self.last_word_date = today
            print(f"📅 Daily word for {today}: {self.daily_word}")
        
        return self.daily_word
    
    def get_hint(self, secret_word):
        """الحصول على تلميح (كلمة قريبة)"""
        data = self.word_database.get(secret_word, {})
        related = data.get("related", [])
        
        if related:
            return random.choice(related)
        
        # إذا لم توجد كلمات مرتبطة، اختر كلمة عشوائية من نفس الفئة
        category = data.get("category", "general")
        same_category = [w for w, d in self.word_database.items() 
                        if d.get("category") == category and w != secret_word]
        
        if same_category:
            return random.choice(same_category)
        
        return None
    
    def is_valid_word(self, word):
        """التحقق من صحة الكلمة"""
        clean = self.normalize_arabic(word)
        return len(clean) >= 2 and all('\u0600' <= c <= '\u06FF' or c.isspace() for c in clean)


# ============================================================================
# Initialize NLP System
# ============================================================================

nlp = ArabicWordEmbedding()

# ============================================================================
# Game State Management
# ============================================================================

class GameState:
    """إدارة حالة اللعبة لكل جلسة"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_or_create_session(self, session_id):
        """الحصول على جلسة أو إنشاؤها"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'guesses': [],
                'hints_used': 0,
                'game_over': False,
                'won': False,
                'secret_word': nlp.get_daily_word()
            }
        return self.sessions[session_id]
    
    def reset_session(self, session_id):
        """إعادة تعيين الجلسة"""
        self.sessions[session_id] = {
            'guesses': [],
            'hints_used': 0,
            'game_over': False,
            'won': False,
            'secret_word': nlp.get_daily_word()
        }
        return self.sessions[session_id]

game_state = GameState()

# ============================================================================
# API Routes
# ============================================================================

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/api/daily-word', methods=['GET'])
def get_daily_word_api():
    """الحصول على كلمة اليوم (مخفية)"""
    return jsonify({
        'success': True,
        'message': 'Game initialized',
        'date': date.today().isoformat()
    })

@app.route('/api/guess', methods=['POST'])
def make_guess():
    """تقديم تخمين"""
    data = request.get_json()
    word = data.get('word', '').strip()
    session_id = data.get('session_id', 'default')
    
    if not word:
        return jsonify({'success': False, 'error': 'No word provided'}), 400
    
    # التحقق من أن الكلمة عربية
    if not nlp.is_valid_word(word):
        return jsonify({'success': False, 'error': 'Please enter Arabic words only'}), 400
    
    session = game_state.get_or_create_session(session_id)
    secret_word = session['secret_word']
    
    # التحقق من التكرار
    normalized_guess = nlp.normalize_arabic(word)
    existing_guesses = [nlp.normalize_arabic(g['word']) for g in session['guesses']]
    
    if normalized_guess in existing_guesses:
        return jsonify({
            'success': True,
            'duplicate': True,
            'message': 'Word already guessed'
        })
    
    # حساب الترتيب
    rank = nlp.get_word_rank(word, secret_word)
    
    # إضافة التخمين
    guess_data = {
        'word': word,
        'rank': rank,
        'is_hint': False
    }
    session['guesses'].append(guess_data)
    
    # التحقق من الفوز
    is_correct = normalized_guess == nlp.normalize_arabic(secret_word)
    if is_correct:
        session['game_over'] = True
        session['won'] = True
    
    return jsonify({
        'success': True,
        'rank': rank,
        'is_correct': is_correct,
        'guess_count': len(session['guesses']),
        'game_over': session['game_over'],
        'won': session['won']
    })

@app.route('/api/hint', methods=['POST'])
def get_hint_api():
    """الحصول على تلميح"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    session = game_state.get_or_create_session(session_id)
    
    if session['game_over']:
        return jsonify({'success': False, 'error': 'Game is over'}), 400
    
    secret_word = session['secret_word']
    hint_word = nlp.get_hint(secret_word)
    
    if not hint_word:
        return jsonify({'success': False, 'error': 'No hint available'}), 500
    
    # التحقق من عدم تكرار التلميح
    normalized_hint = nlp.normalize_arabic(hint_word)
    existing_guesses = [nlp.normalize_arabic(g['word']) for g in session['guesses']]
    
    if normalized_hint in existing_guesses:
        # اختيار تلميح آخر
        attempts = 0
        while normalized_hint in existing_guesses and attempts < 10:
            hint_word = nlp.get_hint(secret_word)
            normalized_hint = nlp.normalize_arabic(hint_word)
            attempts += 1
        
        if normalized_hint in existing_guesses:
            return jsonify({'success': False, 'error': 'No new hint available'}), 400
    
    # حساب ترتيب التلميح
    rank = nlp.get_word_rank(hint_word, secret_word)
    
    # إضافة التلميح
    hint_data = {
        'word': hint_word,
        'rank': rank,
        'is_hint': True
    }
    session['guesses'].append(hint_data)
    session['hints_used'] += 1
    
    return jsonify({
        'success': True,
        'hint': hint_word,
        'rank': rank,
        'hint_count': session['hints_used'],
        'guess_count': len(session['guesses'])
    })

@app.route('/api/give-up', methods=['POST'])
def give_up():
    """الاستسلام"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    session = game_state.get_or_create_session(session_id)
    session['game_over'] = True
    session['won'] = False
    
    return jsonify({
        'success': True,
        'secret_word': session['secret_word'],
        'guess_count': len(session['guesses']),
        'hints_used': session['hints_used']
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """إعادة تعيين اللعبة"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    session = game_state.reset_session(session_id)
    
    return jsonify({
        'success': True,
        'message': 'Game reset successfully'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """الحصول على إحصائيات اللعبة"""
    session_id = request.args.get('session_id', 'default')
    session = game_state.get_or_create_session(session_id)
    
    guesses = session['guesses']
    green = sum(1 for g in guesses if g['rank'] <= 300)
    orange = sum(1 for g in guesses if 300 < g['rank'] <= 1000)
    red = sum(1 for g in guesses if g['rank'] > 1000)
    
    return jsonify({
        'success': True,
        'total_guesses': len(guesses),
        'hints_used': session['hints_used'],
        'green_count': green,
        'orange_count': orange,
        'red_count': red,
        'game_over': session['game_over'],
        'won': session['won']
    })

@app.route('/api/test-similarity', methods=['POST'])
def test_similarity():
    """اختبار تشابه كلمتين (للتجربة)"""
    data = request.get_json()
    word1 = data.get('word1', '')
    word2 = data.get('word2', '')
    
    if not word1 or not word2:
        return jsonify({'success': False, 'error': 'Two words required'}), 400
    
    similarity = nlp.calculate_similarity(word1, word2)
    rank = nlp.get_word_rank(word1, word2)
    
    return jsonify({
        'success': True,
        'word1': word1,
        'word2': word2,
        'similarity': round(similarity, 4),
        'rank': rank
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة السيرفر"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'vocabulary_size': len(nlp.vocabulary),
        'daily_word_date': date.today().isoformat()
    })

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

"""
Siyaq Backend - Smart Arabic Semantic Engine (Optimized for Render Free Tier)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import re
from datetime import datetime, timedelta, timezone
import difflib

app = Flask(__name__)
CORS(app)

# ============================================================================
# Smart Arabic Engine & Lexicon
# ============================================================================

class SiyaqEngine:
    def __init__(self):
        # قاعدة بيانات مصغرة وذكية للكلمات المترابطة (Target Words)
        self.categories = {
            "طبيعة": ["شمس", "قمر", "نجم", "سماء", "بحر", "مطر", "غيم", "جبل", "شجر", "زهر", "نهر", "صحراء", "تراب", "ريح", "عاصفة", "ثلج"],
            "أكل": ["قهوة", "شاي", "ماء", "حليب", "سكر", "خبز", "لحم", "دجاج", "سمك", "تفاح", "موز", "عنب", "تمر", "ملح", "زيت", "عسل"],
            "بيت": ["غرفة", "باب", "نافذة", "سقف", "جدار", "مطبخ", "حمام", "سرير", "كرسي", "طاولة", "مفتاح", "فرن", "ثلاجة"],
            "تقنية": ["حاسوب", "هاتف", "انترنت", "موقع", "تطبيق", "شاشة", "لوحة", "شبكة", "رسالة", "بريد", "كاميرا", "سلك"],
            "عائلة": ["أب", "أم", "ابن", "ابنة", "أخ", "أخت", "جد", "جدة", "عم", "خال", "زوج", "زوجة", "طفل", "عائلة"],
            "مواصلات": ["سيارة", "قطار", "طائرة", "سفينة", "دراجة", "طريق", "شارع", "مطار", "محطة", "بنزين", "سفر", "مركبة"],
            "مشاعر": ["حب", "فرح", "حزن", "غضب", "خوف", "سعادة", "ألم", "شوق", "راحة", "قلق", "سلام", "أمل"],
            "تعليم": ["مدرسة", "جامعة", "كتاب", "قلم", "دفتر", "طالب", "معلم", "درس", "علم", "اختبار", "فصل"],
            "جسم": ["رأس", "عين", "أذن", "أنف", "فم", "يد", "رجل", "قلب", "دم", "عظم", "وجه", "شعر"],
            "ألوان": ["أحمر", "أزرق", "أخضر", "أصفر", "أسود", "أبيض", "برتقالي", "وردي", "رمادي", "بني"],
            "وقت": ["يوم", "ليل", "نهار", "ساعة", "دقيقة", "شهر", "سنة", "أسبوع", "صباح", "مساء", "فجر", "أمس"],
            "ملابس": ["قميص", "ثوب", "سروال", "حذاء", "قبعة", "نظارة", "حقيبة", "معطف", "ساعة", "خاتم"],
            "حيوانات": ["قط", "كلب", "أسد", "نمر", "فيل", "طير", "سمك", "حصان", "جمل", "بقرة", "غزال", "ذئب"]
        }
        
        self.word_to_cat = {}
        self.target_words = []
        for cat, words in self.categories.items():
            for w in words:
                self.word_to_cat[w] = cat
                self.target_words.append(w)
                
        self.daily_word = None
        self.last_date = None

    def get_ksa_date(self):
        # توقيت السعودية (UTC+3)
        ksa_tz = timezone(timedelta(hours=3))
        return datetime.now(ksa_tz).date()

    def get_daily_word(self):
        today = self.get_ksa_date()
        if self.last_date != today or not self.daily_word:
            # نثبت السيد (Seed) بناءً على التاريخ عشان كل الناس تطلعلهم نفس الكلمة
            random.seed(today.toordinal())
            self.daily_word = random.choice(self.target_words)
            self.last_date = today
        return self.daily_word

    def is_valid_word(self, word):
        # التأكد إن الكلمة حروف عربية فقط وبدون خرابيط
        if not re.match(r'^[\u0621-\u064A]+$', word) or len(word) < 2:
            return False
        # رفض الحروف المكررة 3 مرات ورا بعض (مثل خخخ)
        if re.search(r'(.)\1\1', word):
            return False
        return True

    def calculate_rank(self, guess, secret):
        if guess == secret:
            return 1
            
        # محرك تقييم ذكي ومستقر
        score = 0
        cat_secret = self.word_to_cat.get(secret)
        cat_guess = self.word_to_cat.get(guess)
        
        # 1. إذا كانت في نفس التصنيف
        if cat_secret and cat_secret == cat_guess:
            score += 50
            
        # 2. التشابه الحرفي (يفيد في الاشتقاقات زي: كتاب، مكتبة، كاتب)
        similarity = difflib.SequenceMatcher(None, guess, secret).ratio()
        score += int(similarity * 40)
        
        # 3. ترتيب ثابت للكلمات العشوائية بناءً على الكلمتين
        random.seed(secret + guess)
        random_factor = random.randint(1, 100)
        
        if score > 50:
            rank = random.randint(2, 300) # خضراء
        elif score > 20:
            rank = random.randint(301, 1000) # برتقالية
        else:
            rank = random.randint(1001, 50000) + random_factor # حمراء
            
        return rank

    def generate_closest_words(self, secret):
        # توليد لستة بـ 500 كلمة قريبة (لزر أقرب الكلمات)
        closest = []
        cat_secret = self.word_to_cat.get(secret)
        
        # نجيب كلمات نفس التصنيف ونعطيها رتب قريبة جداً
        if cat_secret:
            for w in self.categories[cat_secret]:
                if w != secret:
                    rank = self.calculate_rank(w, secret)
                    if rank > 300: rank = random.randint(2, 299)
                    closest.append({"word": w, "rank": rank})
                    
        # نكمل الباقي بكلمات من القاموس
        for w in self.target_words:
            if w != secret and w not in [x['word'] for x in closest]:
                closest.append({"word": w, "rank": self.calculate_rank(w, secret)})
                
        closest.sort(key=lambda x: x["rank"])
        return closest[:500]

engine = SiyaqEngine()

# ============================================================================
# Game State Management
# ============================================================================

class GameState:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id):
        daily = engine.get_daily_word()
        if session_id not in self.sessions or self.sessions[session_id]['secret_word'] != daily:
            self.sessions[session_id] = {
                'guesses': [],
                'hints_used': 0,
                'game_over': False,
                'won': False,
                'secret_word': daily,
                'closest_cache': engine.generate_closest_words(daily)
            }
        return self.sessions[session_id]

game_state = GameState()

# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    engine.get_daily_word() # تفعيل المحرك
    return jsonify({'success': True, 'status': 'healthy', 'ksa_date': str(engine.get_ksa_date())})

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    word = data.get('word', '').strip()
    session_id = data.get('session_id', 'default')
    
    if not engine.is_valid_word(word):
        return jsonify({'success': False, 'error': 'الكلمة غير صحيحة، يرجى كتابة كلمة عربية لها معنى'}), 400
        
    session = game_state.get_session(session_id)
    secret_word = session['secret_word']
    
    # التحقق من التكرار
    existing_guesses = [g['word'] for g in session['guesses']]
    if word in existing_guesses:
        return jsonify({'success': True, 'duplicate': True})
        
    rank = engine.calculate_rank(word, secret_word)
    is_correct = (word == secret_word)
    
    session['guesses'].append({'word': word, 'rank': rank, 'is_hint': False})
    
    if is_correct:
        session['game_over'] = True
        session['won'] = True
        
    return jsonify({
        'success': True,
        'rank': rank,
        'is_correct': is_correct,
        'guess_count': len([g for g in session['guesses'] if not g['is_hint']]),
        'game_over': session['game_over'],
        'won': session['won']
    })

@app.route('/api/hint', methods=['POST'])
def get_hint():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    session = game_state.get_session(session_id)
    
    if session['game_over']:
        return jsonify({'success': False, 'error': 'انتهت اللعبة'}), 400
        
    existing_words = [g['word'] for g in session['guesses']]
    closest_list = session['closest_cache']
    
    # ندور على كلمة خضراء (تحت 300) ما خمنها اللاعب للحين
    hint_word = None
    hint_rank = None
    for item in closest_list:
        if item['word'] not in existing_words and item['rank'] <= 300:
            hint_word = item['word']
            hint_rank = item['rank']
            break
            
    if not hint_word:
        return jsonify({'success': False, 'error': 'لا توجد تلميحات إضافية'}), 400
        
    session['guesses'].append({'word': hint_word, 'rank': hint_rank, 'is_hint': True})
    session['hints_used'] += 1
    
    return jsonify({
        'success': True,
        'hint': hint_word,
        'rank': hint_rank,
        'hint_count': session['hints_used'],
        'guess_count': len([g for g in session['guesses'] if not g['is_hint']])
    })

@app.route('/api/give-up', methods=['POST'])
def give_up():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    session = game_state.get_session(session_id)
    
    session['game_over'] = True
    session['won'] = False
    
    return jsonify({
        'success': True,
        'secret_word': session['secret_word']
    })

@app.route('/api/closest', methods=['POST'])
def get_closest():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    session = game_state.get_session(session_id)
    
    if not session['game_over']:
        return jsonify({'success': False, 'error': 'الكلمات القريبة تظهر بعد نهاية اللعبة فقط'}), 400
        
    return jsonify({
        'success': True,
        'words': session['closest_cache']
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    # احتفظ بالكلمة السرية لليوم نفسه بس صفر المحاولات
    if session_id in game_state.sessions:
        game_state.sessions[session_id]['guesses'] = []
        game_state.sessions[session_id]['hints_used'] = 0
        game_state.sessions[session_id]['game_over'] = False
        game_state.sessions[session_id]['won'] = False
        
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

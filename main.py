"""
Siyaq Backend - Flask API for Arabic Word Similarity Game
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import random
import json
import math
from datetime import datetime, date

app = Flask(__name__)
CORS(app)

# ============================================================================
# Pure Python Vector Operations
# ============================================================================

def vector_dot(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def vector_norm(v):
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(v1, v2):
    dot = vector_dot(v1, v2)
    norm1 = vector_norm(v1)
    norm2 = vector_norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

# ============================================================================
# Arabic NLP System
# ============================================================================

class ArabicWordEmbedding:
    def __init__(self):
        self.word_vectors = {}
        self.vocabulary = set()
        self.daily_word = None
        self.last_word_date = None
        self._create_fallback_model()
        
    def normalize_arabic(self, text):
        if not text:
            return ""
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        text = text.replace('ئ', 'ي')
        text = text.replace('ؤ', 'و')
        return text
    
    def _generate_vector(self, seed, size=100):
        random.seed(seed)
        return [random.gauss(0, 1) for _ in range(size)]
    
    def _create_fallback_model(self):
        self.word_database = {
            "قهوة": {"vector": self._generate_vector(0), "category": "food", "related": ["هيل", "دلة", "فنجال", "بن", "محمصة", "كوب", "سكر", "حليب", "شاي", "كافيين", "مزاج", "مقهى"]},
            "هيل": {"vector": self._generate_vector(1), "category": "food", "related": ["قهوة", "دلة", "فنجال", "بن", "سكر", "مزاج", "مقهى"]},
            "دلة": {"vector": self._generate_vector(2), "category": "food", "related": ["قهوة", "هيل", "فنجال", "بن", "كوب", "مقهى"]},
            "فنجال": {"vector": self._generate_vector(3), "category": "food", "related": ["قهوة", "هيل", "دلة", "بن", "كوب", "سكر", "حليب"]},
            "بن": {"vector": self._generate_vector(4), "category": "food", "related": ["قهوة", "هيل", "دلة", "فنجال", "محمصة", "كافيين"]},
            "محمصة": {"vector": self._generate_vector(5), "category": "food", "related": ["قهوة", "بن", "كافيين"]},
            "كوب": {"vector": self._generate_vector(6), "category": "food", "related": ["قهوة", "شاي", "فنجال", "ماء", "عصير"]},
            "سكر": {"vector": self._generate_vector(7), "category": "food", "related": ["قهوة", "شاي", "حلوى"]},
            "حليب": {"vector": self._generate_vector(8), "category": "food", "related": ["قهوة", "شاي", "لبن", "جبن"]},
            "شاي": {"vector": self._generate_vector(9), "category": "food", "related": ["قهوة", "هيل", "كوب", "سكر", "حليب"]},
            "كافيين": {"vector": self._generate_vector(10), "category": "food", "related": ["قهوة", "بن", "منبه", "طاقة"]},
            "مزاج": {"vector": self._generate_vector(11), "category": "food", "related": ["قهوة", "هيل", "راحة"]},
            "مقهى": {"vector": self._generate_vector(12), "category": "food", "related": ["قهوة", "هيل", "دلة", "كافي"]},
            "شمس": {"vector": self._generate_vector(20), "category": "nature", "related": ["نهار", "ضوء", "حرارة", "صيف", "سماء"]},
            "قمر": {"vector": self._generate_vector(21), "category": "nature", "related": ["ليل", "نجم", "سماء", "هلال"]},
            "نجم": {"vector": self._generate_vector(22), "category": "nature", "related": ["قمر", "سماء", "ليل", "فضاء"]},
            "سماء": {"vector": self._generate_vector(23), "category": "nature", "related": ["شمس", "قمر", "نجم", "غيم", "مطر"]},
            "بحر": {"vector": self._generate_vector(24), "category": "nature", "related": ["ماء", "موج", "شاطئ", "سمك", "سفينة"]},
            "جبل": {"vector": self._generate_vector(25), "category": "nature", "related": ["تل", "صخور", "ثلج", "قمم"]},
            "شجر": {"vector": self._generate_vector(26), "category": "nature", "related": ["ورق", "غابة", "نخيل", "زيتون"]},
            "زهر": {"vector": self._generate_vector(27), "category": "nature", "related": ["ورد", "نبات", "ربيع", "عطر"]},
            "مطر": {"vector": self._generate_vector(28), "category": "nature", "related": ["غيم", "رعد", "برق", "شتاء", "ماء"]},
            "ريح": {"vector": self._generate_vector(29), "category": "nature", "related": ["عاصفة", "هواء", "غبار", "برد"]},
            "بيت": {"vector": self._generate_vector(40), "category": "home", "related": ["منزل", "سكن", "عائلة", "غرفة", "باب"]},
            "غرفة": {"vector": self._generate_vector(41), "category": "home", "related": ["بيت", "سرير", "نافذة", "باب"]},
            "باب": {"vector": self._generate_vector(42), "category": "home", "related": ["بيت", "غرفة", "مفتاح", "دخول"]},
            "نافذة": {"vector": self._generate_vector(43), "category": "home", "related": ["غرفة", "بيت", "ضوء", "هواء"]},
            "سقف": {"vector": self._generate_vector(44), "category": "home", "related": ["بيت", "جدار", "أرض"]},
            "جدار": {"vector": self._generate_vector(45), "category": "home", "related": ["بيت", "سقف", "دهان", "طوب"]},
            "مطبخ": {"vector": self._generate_vector(46), "category": "home", "related": ["بيت", "طعام", "طبخ", "ثلاجة"]},
            "حمام": {"vector": self._generate_vector(47), "category": "home", "related": ["بيت", "ماء", "استحمام"]},
            "سيارة": {"vector": self._generate_vector(60), "category": "transport", "related": ["موتر", "قيادة", "طريق", "بنزين"]},
            "حافلة": {"vector": self._generate_vector(61), "category": "transport", "related": ["مواصلات", "ركاب", "طريق", "محطة"]},
            "قطار": {"vector": self._generate_vector(62), "category": "transport", "related": ["سكة", "محطة", "ركاب", "سفر"]},
            "طائرة": {"vector": self._generate_vector(63), "category": "transport", "related": ["سماء", "مطار", "سفر", "طيران"]},
            "سفينة": {"vector": self._generate_vector(64), "category": "transport", "related": ["بحر", "موانئ", "سفر", "ركاب"]},
            "دراجة": {"vector": self._generate_vector(65), "category": "transport", "related": ["عجلة", "رياضة", "طريق"]},
            "مدرسة": {"vector": self._generate_vector(80), "category": "education", "related": ["تعليم", "طالب", "أستاذ", "درس", "كتاب"]},
            "جامعة": {"vector": self._generate_vector(81), "category": "education", "related": ["تعليم", "طالب", "دكتور", "كلية"]},
            "كتاب": {"vector": self._generate_vector(82), "category": "education", "related": ["قراءة", "مكتبة", "مؤلف", "صفحات"]},
            "قلم": {"vector": self._generate_vector(83), "category": "education", "related": ["كتابة", "ورق", "مدرسة", "حبر"]},
            "طالب": {"vector": self._generate_vector(84), "category": "education", "related": ["مدرسة", "جامعة", "تعليم", "درس"]},
            "أستاذ": {"vector": self._generate_vector(85), "category": "education", "related": ["مدرسة", "جامعة", "تعليم", "درس", "طالب"]},
            "حاسوب": {"vector": self._generate_vector(100), "category": "tech", "related": ["كمبيوتر", "شاشة", "فأرة", "انترنت"]},
            "هاتف": {"vector": self._generate_vector(101), "category": "tech", "related": ["موبايل", "اتصال", "شاشة", "تطبيق"]},
            "انترنت": {"vector": self._generate_vector(102), "category": "tech", "related": ["شبكة", "موقع", "تواصل", "رقمي"]},
            "موقع": {"vector": self._generate_vector(103), "category": "tech", "related": ["انترنت", "صفحة", "ويب", "رابط"]},
            "تطبيق": {"vector": self._generate_vector(104), "category": "tech", "related": ["برنامج", "هاتف", "ذكي", "موبايل"]},
            "كرة": {"vector": self._generate_vector(120), "category": "sports", "related": ["رياضة", "لعب", "ملعب", "هدف", "فريق"]},
            "ملعب": {"vector": self._generate_vector(121), "category": "sports", "related": ["رياضة", "كرة", "لعب", "مباراة"]},
            "فريق": {"vector": self._generate_vector(122), "category": "sports", "related": ["رياضة", "لاعبين", "كرة", "مباراة"]},
            "رياضة": {"vector": self._generate_vector(123), "category": "sports", "related": ["لعب", "حركة", "صحة", "تدريب"]},
            "هدف": {"vector": self._generate_vector(124), "category": "sports", "related": ["كرة", "مباراة", "فوز", "تسجيل"]},
            "أب": {"vector": self._generate_vector(140), "category": "family", "related": ["والد", "عائلة", "بيت", "أولاد"]},
            "أم": {"vector": self._generate_vector(141), "category": "family", "related": ["والدة", "عائلة", "بيت", "أولاد"]},
            "ابن": {"vector": self._generate_vector(142), "category": "family", "related": ["طفل", "عائلة", "والد", "أخ"]},
            "ابنة": {"vector": self._generate_vector(143), "category": "family", "related": ["طفلة", "عائلة", "والد", "أخت"]},
            "أخ": {"vector": self._generate_vector(144), "category": "family", "related": ["شقيق", "عائلة", "أخوة", "ولد"]},
            "أخت": {"vector": self._generate_vector(145), "category": "family", "related": ["شقيقة", "عائلة", "أخوات", "بنت"]},
            "عائلة": {"vector": self._generate_vector(146), "category": "family", "related": ["بيت", "أب", "أم", "أولاد"]},
            "حب": {"vector": self._generate_vector(160), "category": "emotion", "related": ["مشاعر", "قلب", "عاطفة", "زواج"]},
            "فرح": {"vector": self._generate_vector(161), "category": "emotion", "related": ["سعادة", "بهجة", "ضحك", "احتفال"]},
            "حزن": {"vector": self._generate_vector(162), "category": "emotion", "related": ["بكاء", "دموع", "ألم", "خسارة"]},
            "غضب": {"vector": self._generate_vector(163), "category": "emotion", "related": ["عصبية", "صراخ", "مشكلة"]},
            "خوف": {"vector": self._generate_vector(164), "category": "emotion", "related": ["فزع", "رعب", "قلق", "توتر"]},
            "أحمر": {"vector": self._generate_vector(180), "category": "color", "related": ["لون", "دم", "تفاح", "نار"]},
            "أزرق": {"vector": self._generate_vector(181), "category": "color", "related": ["لون", "سماء", "بحر", "ثلج"]},
            "أخضر": {"vector": self._generate_vector(182), "category": "color", "related": ["لون", "شجر", "عشب", "طبيعة"]},
            "أصفر": {"vector": self._generate_vector(183), "category": "color", "related": ["لون", "شمس", "موز", "ذهب"]},
            "أسود": {"vector": self._generate_vector(184), "category": "color", "related": ["لون", "ليل", "ظلام", "فحم"]},
            "أبيض": {"vector": self._generate_vector(185), "category": "color", "related": ["لون", "ثلج", "نور", "نقاء"]},
        }
        self.vocabulary = set(self.word_database.keys())
    
    def calculate_similarity(self, word1, word2):
        clean1 = self.normalize_arabic(word1)
        clean2 = self.normalize_arabic(word2)
        if clean1 == clean2:
            return 1.0
        return self._fallback_similarity(clean1, clean2)
    
    def _fallback_similarity(self, word1, word2):
        data1 = self.word_database.get(word1)
        data2 = self.word_database.get(word2)
        if not data1 or not data2:
            return self._string_similarity(word1, word2)
        score = 0.0
        if data1["category"] == data2["category"]:
            score += 0.4
        if word2 in data1.get("related", []):
            score += 0.5
        if word1 in data2.get("related", []):
            score += 0.5
        related1 = set(data1.get("related", []))
        related2 = set(data2.get("related", []))
        common = related1 & related2
        if common:
            score += len(common) * 0.1
        vec1 = data1["vector"]
        vec2 = data2["vector"]
        cosine_sim = cosine_similarity(vec1, vec2)
        score += max(0, cosine_sim) * 0.3
        return min(1.0, score)
    
    def _string_similarity(self, s1, s2):
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        if union == 0:
            return 0.0
        jaccard = intersection / union
        prefix_match = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                prefix_match += 1
            else:
                break
        prefix_bonus = prefix_match / max(len(s1), len(s2)) * 0.2
        return min(1.0, jaccard * 0.5 + prefix_bonus)
    
    def get_word_rank(self, guess_word, secret_word):
        similarity = self.calculate_similarity(guess_word, secret_word)
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
        today = date.today()
        if self.last_word_date != today or not self.daily_word:
            random.seed(today.toordinal())
            words = list(self.vocabulary)
            self.daily_word = random.choice(words)
            self.last_word_date = today
        return self.daily_word
    
    def get_hint(self, secret_word):
        data = self.word_database.get(secret_word, {})
        related = data.get("related", [])
        if related:
            return random.choice(related)
        category = data.get("category", "general")
        same_category = [w for w, d in self.word_database.items() if d.get("category") == category and w != secret_word]
        if same_category:
            return random.choice(same_category)
        return None
    
    def is_valid_word(self, word):
        clean = self.normalize_arabic(word)
        return len(clean) >= 2 and all('\u0600' <= c <= '\u06FF' or c.isspace() for c in clean)

nlp = ArabicWordEmbedding()

# ============================================================================
# Game State
# ============================================================================

class GameState:
    def __init__(self):
        self.sessions = {}
    
    def get_or_create_session(self, session_id):
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
    return render_template('index.html')

@app.route('/api/daily-word', methods=['GET'])
def get_daily_word_api():
    return jsonify({
        'success': True,
        'message': 'Game initialized',
        'date': date.today().isoformat()
    })

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    word = data.get('word', '').strip()
    session_id = data.get('session_id', 'default')
    if not word:
        return jsonify({'success': False, 'error': 'No word provided'}), 400
    if not nlp.is_valid_word(word):
        return jsonify({'success': False, 'error': 'Please enter Arabic words only'}), 400
    session = game_state.get_or_create_session(session_id)
    secret_word = session['secret_word']
    normalized_guess = nlp.normalize_arabic(word)
    existing_guesses = [nlp.normalize_arabic(g['word']) for g in session['guesses']]
    if normalized_guess in existing_guesses:
        return jsonify({'success': True, 'duplicate': True, 'message': 'Word already guessed'})
    rank = nlp.get_word_rank(word, secret_word)
    guess_data = {'word': word, 'rank': rank, 'is_hint': False}
    session['guesses'].append(guess_data)
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
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    session = game_state.get_or_create_session(session_id)
    if session['game_over']:
        return jsonify({'success': False, 'error': 'Game is over'}), 400
    secret_word = session['secret_word']
    hint_word = nlp.get_hint(secret_word)
    if not hint_word:
        return jsonify({'success': False, 'error': 'No hint available'}), 500
    normalized_hint = nlp.normalize_arabic(hint_word)
    existing_guesses = [nlp.normalize_arabic(g['word']) for g in session['guesses']]
    if normalized_hint in existing_guesses:
        attempts = 0
        while normalized_hint in existing_guesses and attempts < 10:
            hint_word = nlp.get_hint(secret_word)
            normalized_hint = nlp.normalize_arabic(hint_word)
            attempts += 1
        if normalized_hint in existing_guesses:
            return jsonify({'success': False, 'error': 'No new hint available'}), 400
    rank = nlp.get_word_rank(hint_word, secret_word)
    hint_data = {'word': hint_word, 'rank': rank, 'is_hint': True}
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
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    session = game_state.reset_session(session_id)
    return jsonify({'success': True, 'message': 'Game reset successfully'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'vocabulary_size': len(nlp.vocabulary),
        'daily_word_date': date.today().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

"""
ﺳﯿﺎق - Siyaq Backend
Flask API for Arabic Word Similarity Game using NLP
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
#
===============================================================
=============
# Pure Python Vector Operations (No NumPy)
#
===============================================================
=============
def vector_dot(v1, v2):
"""ﺣﺴﺎب اﻟﻀﺮب اﻟﻨﻘﻄﻲ"""
return sum(a * b for a, b in zip(v1, v2))
def vector_norm(v):
"""ﺣﺴﺎب اﻟﻤﻌﯿﺎر"""
return math.sqrt(sum(x * x for x in v))
def cosine_similarity(v1, v2):
"""ﺣﺴﺎب ﺗﺸﺎﺑﮫ ﺟﯿﺐ اﻟﺘﻤﺎم"""
dot = vector_dot(v1, v2)
norm1 = vector_norm(v1)
norm2 = vector_norm(v2)
if norm1 == 0 or norm2 == 0:
return 0.0
return dot / (norm1 * norm2)
app = Flask(__name__)
CORS(app)
#
===============================================================
=============
# Arabic NLP - Word Embeddings System
#
===============================================================
=============
class ArabicWordEmbedding:
"""
ﻧﻈﺎم ﺗﻀﻤﯿﻦ اﻟﻜﻠﻤﺎت اﻟﻌﺮﺑﯿﺔ
ﯾﺴﺘﺨﺪم Word2Vec أو ﻧﻈﺎم ﺑﺪﯾﻞ ﻟﻠﻜﻠﻤﺎت ﻏﯿﺮ اﻟﻤﻮﺟﻮدة ﻓﻲ اﻟﻤﻮدﯾﻞ
"""
def __init__(self):
self.model = None
self.word_vectors = {}
self.vocabulary = set()
self.daily_word = None
self.last_word_date = None
self.load_or_create_model()
def normalize_arabic(self, text):
"""ﺗﻄﺒﯿﻊ اﻟﻨﺺ اﻟﻌﺮﺑﻲ"""
if not text:
return ""
text = text.lower().strip()
replacements = {
'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
'ة': 'ه',
'ى': 'ي',
'ئ': 'ي',
'
'ؤ': 'و
}
for old, new in replacements.items():
text = text.replace(old, new)
return text
def load_or_create_model(self):
"""ﺗﺤﻤﯿﻞ أو إﻧﺸﺎء ﻧﻤﻮذج Word2Vec"""
# اﺳﺘﺨﺪام اﻟﻨﻈﺎم اﻟﺒﺪﯾﻞ )أﺳﺮع وأﺧﻒ(
print("⚡ Using lightweight similarity system")
self._create_fallback_model()
def _create_fallback_model(self):
"""إﻧﺸﺎء ﻧﻈﺎم ﺑﺪﯾﻞ ﻟﻠﺘﺸﺎﺑﮫ ﻋﻨﺪ ﻋﺪم ﺗﻮﻓﺮ Word2Vec"""
# ﻗﺎﻋﺪة ﺑﯿﺎﻧﺎت اﻟﻜﻠﻤﺎت ﻣﻊ ﻣﺘﺠﮭﺎت ﯾﺪوﯾﺔ
self.word_database = {
# اﻟﻄﻌﺎم واﻟﺸﺮاب
"ﻗﮭﻮة": }",)0(vector": self._generate_vector
category": "food", "related"": ]"ھﯿﻞ", "دﻟﺔ", "ﻓﻨﺠﺎل", "ﺑﻦ",
"ﻣﺤﻤﺼﺔ", "ﻛﻮب", "ﺳﻜﺮ", "ﺣﻠﯿﺐ", "ﺷﺎي", "ﻛﺎﻓﯿﯿﻦ", "ﻣﺰاج",
"ﻣﻘﮭﻰ"[{,
"ھﯿﻞ": }",)1(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "دﻟﺔ", "ﻓﻨﺠﺎل", "ﺑﻦ",
"ﺳﻜﺮ", "ﻣﺰاج", "ﻣﻘﮭﻰ"[{,
"دﻟﺔ": }",)2(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "ﻓﻨﺠﺎل", "ﺑﻦ",
"ﻛﻮب", "ﻣﻘﮭﻰ"[{,
"ﻓﻨﺠﺎل": }",)3(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "دﻟﺔ", "ﺑﻦ",
"ﻛﻮب", "ﺳﻜﺮ", "ﺣﻠﯿﺐ"[{,
"ﺑﻦ": }",)4(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "دﻟﺔ", "ﻓﻨﺠﺎل",
"ﻣﺤﻤﺼﺔ", "ﻛﺎﻓﯿﯿﻦ"[{,
"ﻣﺤﻤﺼﺔ": }",)5(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺑﻦ", "ﻛﺎﻓﯿﯿﻦ",
"ﺗﺤﻤﯿﺺ"[{,
"ﻛﻮب": }",)6(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺷﺎي", "ﻓﻨﺠﺎل", "ﻣﺎء",
ﻋﺼﯿﺮ"[{,
"
"ﺳﻜﺮ": }",)7(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺷﺎي", "ﺣﻠﻮى",
"ﺗﺤﻠﯿﺔ"[{,
"ﺣﻠﯿﺐ": }",)8(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺷﺎي", "ﻟﺒﻦ", "ﺟﺒﻦ",
"زﺑﺪة"[{,
"ﺷﺎي": }",)9(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "ﻛﻮب", "ﺳﻜﺮ",
"ﺣﻠﯿﺐ", "إﻓﻄﺎر"[{,
"ﻛﺎﻓﯿﯿﻦ": }",)10(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺑﻦ", "ﻣﻨﺒﮫ", "ﻃﺎﻗﺔ"[{,
"ﻣﺰاج": }",)11(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "راﺣﺔ",
"اﺳﺘﺮﺧﺎء"[{,
"ﻣﻘﮭﻰ": }",)12(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ھﯿﻞ", "دﻟﺔ", "ﻛﺎﻓﻲ",
"ﻣﻄﻌﻢ"[{,
# اﻟﻄﺒﯿﻌﺔ
"ﺷﻤﺲ": }",)20(vector": self._generate_vector
category": "nature", "related"": ]"ﻧﮭﺎر", "ﺿﻮء", "ﺣﺮارة",
"ﺻﯿﻒ", "ﺳﻤﺎء"[{,
"ﻗﻤﺮ": }",)21(vector": self._generate_vector
category": "nature", "related"": ]"ﻟﯿﻞ", "ﻧﺠﻢ", "ﺳﻤﺎء", "ھﻼل",
"ﻓﻀﺎء"[{,
"ﻧﺠﻢ": }",)22(vector": self._generate_vector
category": "nature", "related"": ]"ﻗﻤﺮ", "ﺳﻤﺎء", "ﻟﯿﻞ", "ﻓﻀﺎء",
"ﻧﺠﻮم"[{,
"ﺳﻤﺎء": }",)23(vector": self._generate_vector
category": "nature", "related"": ]"ﺷﻤﺲ", "ﻗﻤﺮ", "ﻧﺠﻢ", "ﻏﯿﻢ",
"ﻣﻄﺮ", "ﻃﯿﺮان"[{,
"ﺑﺤﺮ": }",)24(vector": self._generate_vector
category": "nature", "related"": ]"ﻣﺎء", "ﻣﻮج", "ﺷﺎﻃﺊ", "ﺳﻤﻚ",
"ﻏﻮص", "ﺳﻔﯿﻨﺔ"[{,
"ﺟﺒﻞ": }",)25(vector": self._generate_vector
category": "nature", "related"": ]"ﺗﻞ", "ﺻﺨﻮر", "ﺛﻠﺞ", "ﻗﻤﻢ",
"ﻃﺒﯿﻌﺔ"[{,
"ﺷﺠﺮ": }",)26(vector": self._generate_vector
category": "nature", "related"": ]"ورق", "ﻏﺎﺑﺔ", "ﻧﺨﯿﻞ",
"زﯾﺘﻮن", "ﻓﺎﻛﮭﺔ"[{,
"زھﺮ": }",)27(vector": self._generate_vector
category": "nature", "related"": ]"ورد", "ﻧﺒﺎت", "رﺑﯿﻊ", "ﻋﻄﺮ",
"ﺣﺪﯾﻘﺔ"[{,
"ﻣﻄﺮ": }",)28(vector": self._generate_vector
category": "nature", "related"": ]"ﻏﯿﻢ", "رﻋﺪ", "ﺑﺮق", "ﺷﺘﺎء",
"ﻣﺎء"[{,
"رﯾﺢ": }",)29(vector": self._generate_vector
category": "nature", "related"": ]"ﻋﺎﺻﻔﺔ", "ھﻮاء", "ﻏﺒﺎر",
"ﺑﺮد", "ﺻﯿﻒ"[{,
# اﻟﻤﻨﺰل
"ﺑﯿﺖ": }",)40(vector": self._generate_vector
category": "home", "related"": ]"ﻣﻨﺰل", "ﺳﻜﻦ", "ﻋﺎﺋﻠﺔ", "ﻏﺮﻓﺔ",
"ﺑﺎب"[{,
"ﻏﺮﻓﺔ": }",)41(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﺳﺮﯾﺮ", "ﻧﺎﻓﺬة", "ﺑﺎب",
"أﺛﺎث"[{,
"ﺑﺎب": }",)42(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﻏﺮﻓﺔ", "ﻣﻔﺘﺎح", "دﺧﻮل",
"ﺧﺮوج"[{,
"ﻧﺎﻓﺬة": }",)43(vector": self._generate_vector
category": "home", "related"": ]"ﻏﺮﻓﺔ", "ﺑﯿﺖ", "ﺿﻮء", "ھﻮاء",
"ﻣﻨﻈﺮ"[{,
"ﺳﻘﻒ": }",)44(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﺟﺪار", "أرض",
"ﺳﻤﺎوي"[{,
"ﺟﺪار": }",)45(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﺳﻘﻒ", "دھﺎن", "ﻃﻮب",
"أﺳﻤﻨﺖ"[{,
"ﻣﻄﺒﺦ": }",)46(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﻃﻌﺎم", "ﻃﺒﺦ", "ﺛﻼﺟﺔ",
"ﻣﻮﻗﺪ"[{,
"ﺣﻤﺎم": }",)47(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﻣﺎء", "اﺳﺘﺤﻤﺎم",
"ﻣﺮﺣﺎض", "ﻏﺴﻞ"[{,
# اﻟﻨﻘﻞ
"ﺳﯿﺎرة": }",)60(vector": self._generate_vector
category": "transport", "related"": ]"ﻣﻮﺗﺮ", "ﻗﯿﺎدة", "ﻃﺮﯾﻖ",
"ﺑﻨﺰﯾﻦ", "ﻣﻮﻗﻒ"[{,
"ﺣﺎﻓﻠﺔ": }",)61(vector": self._generate_vector
category": "transport", "related"": ]"ﻣﻮاﺻﻼت", "رﻛﺎب", "ﻃﺮﯾﻖ",
"ﻣﺤﻄﺔ", "ﺳﺎﺋﻖ"[{,
"ﻗﻄﺎر": }",)62(vector": self._generate_vector
category": "transport", "related"": ]"ﺳﻜﺔ", "ﻣﺤﻄﺔ", "رﻛﺎب",
"ﺳﻔﺮ", "ﺳﺮﻋﺔ"[{,
"ﻃﺎﺋﺮة": }",)63(vector": self._generate_vector
category": "transport", "related"": ]"ﺳﻤﺎء", "ﻣﻄﺎر", "ﺳﻔﺮ",
"ﻃﯿﺮان", "رﺣﻠﺔ"[{,
"ﺳﻔﯿﻨﺔ": }",)64(vector": self._generate_vector
category": "transport", "related"": ]"ﺑﺤﺮ", "ﻣﻮاﻧﺊ", "ﺳﻔﺮ",
"رﻛﺎب", "ﺑﺎﺧﺮة"[{,
"دراﺟﺔ": }",)65(vector": self._generate_vector
category": "transport", "related"": ]"ﻋﺠﻠﺔ", "رﯾﺎﺿﺔ", "ﻃﺮﯾﻖ",
"ﻣﺸﻲ", "ﺻﺤﺔ"[{,
# اﻟﺘﻌﻠﯿﻢ
"ﻣﺪرﺳﺔ": }",)80(vector": self._generate_vector
category": "education", "related"": ]"ﺗﻌﻠﯿﻢ", "ﻃﺎﻟﺐ", "أﺳﺘﺎذ",
"درس", "ﻛﺘﺎب"[{,
"ﺟﺎﻣﻌﺔ": }",)81(vector": self._generate_vector
category": "education", "related"": ]"ﺗﻌﻠﯿﻢ", "ﻃﺎﻟﺐ", "دﻛﺘﻮر",
"ﻛﻠﯿﺔ", "ﺑﺤﺚ"[{,
"ﻛﺘﺎب": }",)82(vector": self._generate_vector
category": "education", "related"": ]"ﻗﺮاءة", "ﻣﻜﺘﺒﺔ", "ﻣﺆﻟﻒ",
"ﺻﻔﺤﺎت", "ﻋﻠﻢ"[{,
"ﻗﻠﻢ": }",)83(vector": self._generate_vector
category": "education", "related"": ]"ﻛﺘﺎﺑﺔ", "ورق", "ﻣﺪرﺳﺔ",
ﺣﺒﺮ", "رﺻﺎص"[{,
"
"ﻃﺎﻟﺐ": }",)84(vector": self._generate_vector
category": "education", "related"": ]"ﻣﺪرﺳﺔ", "ﺟﺎﻣﻌﺔ", "ﺗﻌﻠﯿﻢ",
"درس", "اﻣﺘﺤﺎن"[{,
"أﺳﺘﺎذ": }",)85(vector": self._generate_vector
category": "education", "related"": ]"ﻣﺪرﺳﺔ", "ﺟﺎﻣﻌﺔ", "ﺗﻌﻠﯿﻢ",
"درس", "ﻃﺎﻟﺐ"[{,
# اﻟﺘﻜﻨﻮﻟﻮﺟﯿﺎ
"ﺣﺎﺳﻮب": }",)100(vector": self._generate_vector
category": "tech", "related"": ]"ﻛﻤﺒﯿﻮﺗﺮ", "ﺷﺎﺷﺔ", "ﻓﺄرة",
"ﻟﻮﺣﺔ", "اﻧﺘﺮﻧﺖ"[{,
"ھﺎﺗﻒ": }",)101(vector": self._generate_vector
category": "tech", "related"": ]"ﻣﻮﺑﺎﯾﻞ", "اﺗﺼﺎل", "ﺷﺎﺷﺔ",
"ﺗﻄﺒﯿﻖ", "ذﻛﻲ"[{,
"اﻧﺘﺮﻧﺖ": }",)102(vector": self._generate_vector
category": "tech", "related"": ]"ﺷﺒﻜﺔ", "ﻣﻮﻗﻊ", "ﺗﻮاﺻﻞ",
"اﺗﺼﺎل", "رﻗﻤﻲ"[{,
"ﻣﻮﻗﻊ": }",)103(vector": self._generate_vector
category": "tech", "related"": ]"اﻧﺘﺮﻧﺖ", "ﺻﻔﺤﺔ", "وﯾﺐ",
"راﺑﻂ", "ﻣﺘﺼﻔﺢ"[{,
"ﺗﻄﺒﯿﻖ": }",)104(vector": self._generate_vector
category": "tech", "related"": ]"ﺑﺮﻧﺎﻣﺞ", "ھﺎﺗﻒ", "ذﻛﻲ",
"اﺳﺘﺨﺪام", "ﻣﻮﺑﺎﯾﻞ"[{,
# اﻟﺮﯾﺎﺿﺔ
"ﻛﺮة": }",)120(vector": self._generate_vector
category": "sports", "related"": ]"رﯾﺎﺿﺔ", "ﻟﻌﺐ", "ﻣﻠﻌﺐ",
"ھﺪف", "ﻓﺮﯾﻖ"[{,
"ﻣﻠﻌﺐ": }",)121(vector": self._generate_vector
category": "sports", "related"": ]"رﯾﺎﺿﺔ", "ﻛﺮة", "ﻟﻌﺐ",
"ﻣﺒﺎراة", "ﺟﻤﮭﻮر"[{,
"ﻓﺮﯾﻖ": }",)122(vector": self._generate_vector
category": "sports", "related"": ]"رﯾﺎﺿﺔ", "ﻻﻋﺒﯿﻦ", "ﻛﺮة",
"ﻣﺒﺎراة", "ﻓﻮز"[{,
"رﯾﺎﺿﺔ": }",)123(vector": self._generate_vector
category": "sports", "related"": ]"ﻟﻌﺐ", "ﺣﺮﻛﺔ", "ﺻﺤﺔ",
"ﺗﺪرﯾﺐ", "ﺑﻄﻮﻟﺔ"[{,
"ھﺪف": }",)124(vector": self._generate_vector
category": "sports", "related"": ]"ﻛﺮة", "ﻣﺒﺎراة", "ﻓﻮز",
"ﺗﺴﺠﯿﻞ", "ﺷﺒﻜﺔ"[{,
# اﻟﻌﺎﺋﻠﺔ
"أب": }",)140(vector": self._generate_vector
category": "family", "related"": ]"واﻟﺪ", "ﻋﺎﺋﻠﺔ", "ﺑﯿﺖ",
"أوﻻد", "زوج"[{,
"أم": }",)141(vector": self._generate_vector
category": "family", "related"": ]"واﻟﺪة", "ﻋﺎﺋﻠﺔ", "ﺑﯿﺖ",
"أوﻻد", "زوﺟﺔ"[{,
"اﺑﻦ": }",)142(vector": self._generate_vector
category": "family", "related"": ]"ﻃﻔﻞ", "ﻋﺎﺋﻠﺔ", "واﻟﺪ", "أخ",
"وﻟﺪ"[{,
"اﺑﻨﺔ": }",)143(vector": self._generate_vector
category": "family", "related"": ]"ﻃﻔﻠﺔ", "ﻋﺎﺋﻠﺔ", "واﻟﺪ",
"أﺧﺖ", "ﺑﻨﺖ"[{,
"أخ": }",)144(vector": self._generate_vector
category": "family", "related"": ]"ﺷﻘﯿﻖ", "ﻋﺎﺋﻠﺔ", "أﺧﻮة",
"وﻟﺪ", "ﺻﺎﺣﺐ"[{,
"أﺧﺖ": }",)145(vector": self._generate_vector
category": "family", "related"": ]"ﺷﻘﯿﻘﺔ", "ﻋﺎﺋﻠﺔ", "أﺧﻮات",
"ﺑﻨﺖ", "ﺻﺎﺣﺒﺔ"[{,
"ﻋﺎﺋﻠﺔ": }",)146(vector": self._generate_vector
category": "family", "related"": ]"ﺑﯿﺖ", "أب", "أم", "أوﻻد",
"ﻗﺮاﺑﺔ"[{,
# اﻟﻤﺸﺎﻋﺮ
"ﺣﺐ": }",)160(vector": self._generate_vector
category": "emotion", "related"": ]"ﻣﺸﺎﻋﺮ", "ﻗﻠﺐ", "ﻋﺎﻃﻔﺔ",
"روﻣﺎﻧﺴﯿﺔ", "زواج"[{,
"ﻓﺮح": }",)161(vector": self._generate_vector
category": "emotion", "related"": ]"ﺳﻌﺎدة", "ﺑﮭﺠﺔ", "ﺿﺤﻚ",
"اﺣﺘﻔﺎل", "ﺧﺒﺮ"[{,
"ﺣﺰن": }",)162(vector": self._generate_vector
category": "emotion", "related"": ]"ﺑﻜﺎء", "دﻣﻮع", "أﻟﻢ",
"ﺧﺴﺎرة", "ﻣﻮت"[{,
"ﻏﻀﺐ": }",)163(vector": self._generate_vector
category": "emotion", "related"": ]"ﻋﺼﺒﯿﺔ", "ﺻﺮاخ", "ﻣﺸﻜﻠﺔ",
"ﺧﻼف", "ﻋﺪاوة"[{,
"ﺧﻮف": }",)164(vector": self._generate_vector
category": "emotion", "related"": ]"ﻓﺰع", "رﻋﺐ", "ﻗﻠﻖ", "ﺗﻮﺗﺮ",
"ﺧﻄﺮ"[{,
# اﻷﻟﻮان
"أﺣﻤﺮ": }",)180(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "دم", "ﺗﻔﺎح", "ﻧﺎر",
ﺣﺐ"[{,
"
"أزرق": }",)181(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﺳﻤﺎء", "ﺑﺤﺮ", "ﺛﻠﺞ",
"ﺑﺎرد"[{,
"أﺧﻀﺮ": }",)182(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﺷﺠﺮ", "ﻋﺸﺐ", "ﻃﺒﯿﻌﺔ",
رﺑﯿﻊ"[{,
"
"أﺻﻔﺮ": }",)183(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﺷﻤﺲ", "ﻣﻮز", "ذھﺐ",
"ﺻﺤﺮاء"[{,
"أﺳﻮد": }",)184(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﻟﯿﻞ", "ﻇﻼم", "ﻓﺤﻢ",
"ﺣﺰن"[{,
"أﺑﯿﺾ": }",)185(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﺛﻠﺞ", "ﻧﻮر", "ﻧﻘﺎء",
"ﺳﻼم"[{,
}
ً
# إﺿﺎﻓﺔ اﻟﻤﺰﯾﺪ ﻣﻦ اﻟﻜﻠﻤﺎت ﺗﻠﻘﺎﺋﯿﺎ
self._expand_vocabulary()
self.vocabulary = set(self.word_database.keys())
def _generate_vector(self, seed, size=100):
"""ﺗﻮﻟﯿﺪ ﻣﺘﺠﮫ ﻋﺸﻮاﺋﻲ ﻣﺒﻨﻲ ﻋﻠﻰ seed )ﺑﺪون numpy("""
random.seed(seed)
# ﺗﻮﻟﯿﺪ أرﻗﺎم ﻋﺸﻮاﺋﯿﺔ ﺑﺎﺳﺘﺨﺪام ﺗﻮزﯾﻊ ﻃﺒﯿﻌﻲ ﺗﻘﺮﯾﺒﻲ
return [random.gauss(0, 1) for _ in range(size)]
def _expand_vocabulary(self):
"""ﺗﻮﺳﯿﻊ ﻗﺎﻣﻮس اﻟﻜﻠﻤﺎت ﺑﺈﺿﺎﻓﺔ ﻛﻠﻤﺎت ﻣﺸﺘﻘﺔ"""
additional_words = {
# ﻣﺸﺘﻘﺎت اﻟﻄﻌﺎم
"ﻛﺎﻓﻲ": }",)200(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﻣﻘﮭﻰ", "ﻛﺎﻓﯿﯿﻦ"[{,
"ﻓﻄﻮر": }",)201(vector": self._generate_vector
category": "food", "related"": ]"ﻗﮭﻮة", "ﺷﺎي", "ﻃﻌﺎم",
"ﺻﺒﺎح"[{,
"ﻋﺼﯿﺮ": }",)202(vector": self._generate_vector
category": "food", "related"": ]"ﻓﺎﻛﮭﺔ", "ﺑﺮﺗﻘﺎل", "ﺗﻔﺎح",
"ﻣﺸﺮوب"[{,
"ﻓﺎﻛﮭﺔ": }",)203(vector": self._generate_vector
category": "food", "related"": ]"ﺗﻔﺎح", "ﻣﻮز", "ﻋﻨﺐ",
"ﺑﺮﺗﻘﺎل"[{,
"ﺧﻀﺎر": }",)204(vector": self._generate_vector
category": "food", "related"": ]"ﻃﻤﺎﻃﻢ", "ﺧﯿﺎر", "ﺑﺼﻞ",
"ﺳﻠﻄﺔ"[{,
"ﻟﺤﻢ": }",)205(vector": self._generate_vector
category": "food", "related"": ]"دﺟﺎج", "ﺳﻤﻚ", "ﻃﻌﺎم",
"ﺷﻮاء"[{,
"دﺟﺎج": }",)206(vector": self._generate_vector
category": "food", "related"": ]"ﻟﺤﻢ", "ﻃﻌﺎم", "وﺟﺒﺔ",
"ﻣﺸﻮي"[{,
"ﺳﻤﻚ": }",)207(vector": self._generate_vector
category": "food", "related"": ]"ﺑﺤﺮ", "ﻃﻌﺎم", "ﺻﯿﺪ", "ﻣﻄﻌﻢ"[{,
"رز": }",)208(vector": self._generate_vector
category": "food", "related"": ]"ﻃﺒﺦ", "وﺟﺒﺔ", "ﻟﺤﻢ", "دﺟﺎج"[{,
"ﺧﺒﺰ": }",)209(vector": self._generate_vector
category": "food", "related"": ]"ﻃﺤﯿﻦ", "ﻣﺨﺒﺰ", "ﻓﻄﻮر",
"ﺳﺎﻧﺪوﯾﺘﺶ"[{,
# ﻣﺸﺘﻘﺎت اﻟﻄﺒﯿﻌﺔ
"ﻧﮭﺎر": }",)220(vector": self._generate_vector
category": "nature", "related"": ]"ﺷﻤﺲ", "ﺻﺒﺎح", "ﻇﮭﺮ",
"ﻣﺴﺎء"[{,
"ﻟﯿﻞ": }",)221(vector": self._generate_vector
category": "nature", "related"": ]"ﻗﻤﺮ", "ﻧﺠﻢ", "ﻇﻼم", "ﻧﻮم"[{,
"ﺿﻮء": }",)222(vector": self._generate_vector
category": "nature", "related"": ]"ﺷﻤﺲ", "ﻧﮭﺎر", "ﻻﻣﺐ",
"ﻧﻮر"[{,
"ﻇﻼم": }",)223(vector": self._generate_vector
category": "nature", "related"": ]"ﻟﯿﻞ", "أﺳﻮد", "ﺧﻮف",
"ﻧﻮم"[{,
"ھﻮاء": }",)224(vector": self._generate_vector
category": "nature", "related"": ]"رﯾﺢ", "ﺗﻨﻔﺲ", "ﺳﻤﺎء",
"أﻛﺴﺠﯿﻦ"[{,
"ﻧﺎر": }",)225(vector": self._generate_vector
category": "nature", "related"": ]"ﻟﮭﺐ", "ﺣﺮارة", "دفء",
"ﺷﻮاء"[{,
"ﻣﺎء": }",)226(vector": self._generate_vector
category": "nature", "related"": ]"ﺑﺤﺮ", "ﻧﮭﺮ", "ﻋﻄﺶ", "ﺷﺮب",
"ﺣﯿﺎة"[{,
"ﺛﻠﺞ": }",)227(vector": self._generate_vector
category": "nature", "related"": ]"ﺑﺮد", "ﺷﺘﺎء", "أﺑﯿﺾ",
"ﺗﺰﻟﺞ"[{,
"ﺻﺤﺮاء": }",)228(vector": self._generate_vector
category": "nature", "related"": ]"رﻣﻞ", "ﺣﺮ", "ﺟﻤﻞ", "واﺣﺔ"[{,
"ﻏﺎﺑﺔ": }",)229(vector": self._generate_vector
category": "nature", "related"": ]"ﺷﺠﺮ", "ﺣﯿﻮان", "ﻃﺒﯿﻌﺔ",
"أﺧﻀﺮ"[{,
# ﻣﺸﺘﻘﺎت اﻟﻤﻨﺰل
"ﻣﻨﺰل": }",)240(vector": self._generate_vector
category": "home", "related"": ]"ﺑﯿﺖ", "ﺳﻜﻦ", "ﻋﺎﺋﻠﺔ",
"ﻏﺮﻓﺔ"[{,
"ﺳﺮﯾﺮ": }",)241(vector": self._generate_vector
category": "home", "related"": ]"ﻧﻮم", "ﻏﺮﻓﺔ", "ﺑﻄﺎﻧﯿﺔ",
"وﺳﺎدة"[{,
"ﻣﻔﺘﺎح": }",)242(vector": self._generate_vector
category": "home", "related"": ]"ﺑﺎب", "ﻗﻔﻞ", "ﻓﺘﺢ", "دﺧﻮل"[{,
"ﺛﻼﺟﺔ": }",)243(vector": self._generate_vector
category": "home", "related"": ]"ﻣﻄﺒﺦ", "ﻃﻌﺎم", "ﺑﺎرد",
"ﻣﺎء"[{,
"ﺗﻠﻔﺎز": }",)244(vector": self._generate_vector
category": "home", "related"": ]"ﺷﺎﺷﺔ", "ﺑﺮاﻣﺞ", "أﻓﻼم",
"ﺗﺮﻓﯿﮫ"[{,
"أﺛﺎث": }",)245(vector": self._generate_vector
category": "home", "related"": ]"ﻛﺮﺳﻲ", "ﻃﺎوﻟﺔ", "ﺧﺰاﻧﺔ",
"ﺑﯿﺖ"[{,
"ﻛﺮﺳﻲ": }",)246(vector": self._generate_vector
category": "home", "related"": ]"ﺟﻠﻮس", "ﻃﺎوﻟﺔ", "أﺛﺎث",
"ﻣﻜﺘﺐ"[{,
"ﻃﺎوﻟﺔ": }",)247(vector": self._generate_vector
category": "home", "related"": ]"ﻛﺮﺳﻲ", "أﺛﺎث", "ﻃﻌﺎم",
"ﻋﻤﻞ"[{,
# ﻣﺸﺘﻘﺎت اﻟﻨﻘﻞ
"ﻣﻮﺗﺮ": }",)260(vector": self._generate_vector
category": "transport", "related"": ]"ﺳﯿﺎرة", "ﻗﯿﺎدة",
"ﻣﻮاﺻﻼت"[{,
"ﻃﺮﯾﻖ": }",)261(vector": self._generate_vector
category": "transport", "related"": ]"ﺳﯿﺎرة", "ﺳﻔﺮ", "ﺷﺎرع",
"ﺣﺮﻛﺔ"[{,
"ﻣﻄﺎر": }",)262(vector": self._generate_vector
category": "transport", "related"": ]"ﻃﺎﺋﺮة", "ﺳﻔﺮ", "رﺣﻠﺔ",
"ﺟﻮاز"[{,
"ﻣﺤﻄﺔ": }",)263(vector": self._generate_vector
category": "transport", "related"": ]"ﻗﻄﺎر", "ﺣﺎﻓﻠﺔ", "ﻣﻮاﺻﻼت",
"رﻛﺎب"[{,
"ﺳﻔﺮ": }",)264(vector": self._generate_vector
category": "transport", "related"": ]"رﺣﻠﺔ", "ﻃﺎﺋﺮة", "ﺳﯿﺎﺣﺔ",
"ﻓﻨﺪق"[{,
"رﺣﻠﺔ": }",)265(vector": self._generate_vector
category": "transport", "related"": ]"ﺳﻔﺮ", "ﻃﺎﺋﺮة", "ﺳﯿﺎﺣﺔ",
"اﺳﺘﺠﻤﺎم"[{,
# ﻣﺸﺘﻘﺎت اﻟﺘﻌﻠﯿﻢ
"ﺗﻌﻠﯿﻢ": }",)280(vector": self._generate_vector
category": "education", "related"": ]"ﻣﺪرﺳﺔ", "ﺟﺎﻣﻌﺔ", "ﻋﻠﻢ",
"ﻣﻌﺮﻓﺔ"[{,
"ﻋﻠﻢ": }",)281(vector": self._generate_vector
category": "education", "related"": ]"ﻣﻌﺮﻓﺔ", "ﺗﻌﻠﯿﻢ", "ﺑﺤﺚ",
"دراﺳﺔ"[{,
"ﻣﻌﺮﻓﺔ": }",)282(vector": self._generate_vector
category": "education", "related"": ]"ﻋﻠﻢ", "ﺗﻌﻠﯿﻢ", "ﺛﻘﺎﻓﺔ",
"ﻓﮭﻢ"[{,
"دراﺳﺔ": }",)283(vector": self._generate_vector
category": "education", "related"": ]"ﺗﻌﻠﯿﻢ", "ﻛﺘﺎب", "اﻣﺘﺤﺎن",
"ﻧﺠﺎح"[{,
"اﻣﺘﺤﺎن": }",)284(vector": self._generate_vector
category": "education", "related"": ]"دراﺳﺔ", "درﺟﺔ", "ﻧﺠﺎح",
رﺳﻮب"[{,
"
"ﻣﻜﺘﺒﺔ": }",)285(vector": self._generate_vector
category": "education", "related"": ]"ﻛﺘﺎب", "ﻗﺮاءة", "ﻋﻠﻢ",
"دراﺳﺔ"[{,
# ﻣﺸﺘﻘﺎت اﻟﺘﻜﻨﻮﻟﻮﺟﯿﺎ
"ﻛﻤﺒﯿﻮﺗﺮ": }",)300(vector": self._generate_vector
category": "tech", "related"": ]"ﺣﺎﺳﻮب", "ﺷﺎﺷﺔ", "اﻧﺘﺮﻧﺖ",
"ﺑﺮﻧﺎﻣﺞ"[{,
"ﻣﻮﺑﺎﯾﻞ": }",)301(vector": self._generate_vector
category": "tech", "related"": ]"ھﺎﺗﻒ", "ذﻛﻲ", "ﺷﺎﺷﺔ",
"اﺗﺼﺎل"[{,
"ﺷﺒﻜﺔ": }",)302(vector": self._generate_vector
category": "tech", "related"": ]"اﻧﺘﺮﻧﺖ", "اﺗﺼﺎل", "واي ﻓﺎي",
"ﺗﻮاﺻﻞ"[{,
"ﺑﺮﻧﺎﻣﺞ": }",)303(vector": self._generate_vector
category": "tech", "related"": ]"ﺗﻄﺒﯿﻖ", "ﺣﺎﺳﻮب", "ﻛﻤﺒﯿﻮﺗﺮ",
"ﻧﻈﺎم"[{,
"ذﻛﻲ": }",)304(vector": self._generate_vector
category": "tech", "related"": ]"ھﺎﺗﻒ", "ﺗﻄﺒﯿﻖ", "ﺗﻘﻨﯿﺔ",
"ذﻛﺎء"[{,
"ذﻛﺎء": }",)305(vector": self._generate_vector
category": "tech", "related"": ]"اﺻﻄﻨﺎﻋﻲ", "ﺗﻌﻠﻢ", "آﻟﺔ",
"ﺗﻘﻨﯿﺔ"[{,
# ﻣﺸﺘﻘﺎت اﻟﺮﯾﺎﺿﺔ
"ﻟﻌﺐ": }",)320(vector": self._generate_vector
category": "sports", "related"": ]"رﯾﺎﺿﺔ", "ﻛﺮة", "ﻣﺘﻌﺔ",
"أﻃﻔﺎل"[{,
"ﻣﺒﺎراة": }",)321(vector": self._generate_vector
category": "sports", "related"": ]"ﻛﺮة", "ﻓﺮﯾﻖ", "ﻓﻮز",
"ﺧﺴﺎرة"[{,
"ﻓﻮز": }",)322(vector": self._generate_vector
category": "sports", "related"": ]"ﻣﺒﺎراة", "ﺑﻄﻮﻟﺔ", "ﻛﺄس",
"اﺣﺘﻔﺎل"[{,
"ﺧﺴﺎرة": }",)323(vector": self._generate_vector
category": "sports", "related"": ]"ﻣﺒﺎراة", "ﺣﺰن", "ﻓﺸﻞ",
"ﺗﺪرﯾﺐ"[{,
"ﺗﺪرﯾﺐ": }",)324(vector": self._generate_vector
category": "sports", "related"": ]"رﯾﺎﺿﺔ", "ﻟﯿﺎﻗﺔ", "ﻣﺪرب",
"ﺗﻤﺎرﯾﻦ"[{,
"ﺑﻄﻮﻟﺔ": }",)325(vector": self._generate_vector
category": "sports", "related"": ]"ﻣﺒﺎراة", "ﻓﻮز", "ﻛﺄس",
"ﻣﻨﺘﺨﺐ"[{,
# ﻣﺸﺘﻘﺎت اﻟﻌﺎﺋﻠﺔ
"واﻟﺪ": }",)340(vector": self._generate_vector
category": "family", "related"": ]"أب", "أم", "ﻋﺎﺋﻠﺔ",
"أوﻻد"[{,
"واﻟﺪة": }",)341(vector": self._generate_vector
category": "family", "related"": ]"أم", "ﻋﺎﺋﻠﺔ", "أوﻻد",
"ﺣﻨﺎن"[{,
"ﻃﻔﻞ": }",)342(vector": self._generate_vector
category": "family", "related"": ]"اﺑﻦ", "اﺑﻨﺔ", "ﺻﻐﯿﺮ",
"ﻟﻌﺐ"[{,
"زوج": }",)343(vector": self._generate_vector
category": "family", "related"": ]"زوﺟﺔ", "زواج", "ﻋﺎﺋﻠﺔ",
ﺣﺐ"[{,
"
"زوﺟﺔ": }",)344(vector": self._generate_vector
category": "family", "related"": ]"زوج", "زواج", "ﻋﺎﺋﻠﺔ",
ﺣﺐ"[{,
"
"زواج": }",)345(vector": self._generate_vector
category": "family", "related"": ]"زوج", "زوﺟﺔ", "ﻋﺎﺋﻠﺔ", "ﺣﺐ",
"ﻓﺮح"[{,
"أوﻻد": }",)346(vector": self._generate_vector
category": "family", "related"": ]"أب", "أم", "ﻋﺎﺋﻠﺔ",
"أﻃﻔﺎل"[{,
# ﻣﺸﺘﻘﺎت اﻟﻤﺸﺎﻋﺮ
"ﻣﺸﺎﻋﺮ": }",)360(vector": self._generate_vector
category": "emotion", "related"": ]"ﺣﺐ", "ﻓﺮح", "ﺣﺰن", "ﻗﻠﺐ"[{,
"ﻋﺎﻃﻔﺔ": }",)361(vector": self._generate_vector
category": "emotion", "related"": ]"ﺣﺐ", "ﻣﺸﺎﻋﺮ", "ﻗﻠﺐ",
"روﻣﺎﻧﺴﯿﺔ"[{,
"ﻗﻠﺐ": }",)362(vector": self._generate_vector
category": "emotion", "related"": ]"ﺣﺐ", "ﻣﺸﺎﻋﺮ", "ﻧﺒﺾ",
"ﻋﺎﻃﻔﺔ"[{,
"ﺳﻌﺎدة": }",)363(vector": self._generate_vector
category": "emotion", "related"": ]"ﻓﺮح", "ﺑﮭﺠﺔ", "ﺳﺮور",
"رﺿﺎ"[{,
"ﺑﮭﺠﺔ": }",)364(vector": self._generate_vector
category": "emotion", "related"": ]"ﻓﺮح", "ﺳﻌﺎدة", "ﺳﺮور",
"اﺣﺘﻔﺎل"[{,
"ﺿﺤﻚ": }",)365(vector": self._generate_vector
category": "emotion", "related"": ]"ﻓﺮح", "ﺑﮭﺠﺔ", "ﻓﻜﺎھﺔ",
ﻣﺮح"[{,
"
"ﺑﻜﺎء": }",)366(vector": self._generate_vector
category": "emotion", "related"": ]"ﺣﺰن", "دﻣﻮع", "أﻟﻢ",
"ﺧﺴﺎرة"[{,
"دﻣﻮع": }",)367(vector": self._generate_vector
category": "emotion", "related"": ]"ﺑﻜﺎء", "ﺣﺰن", "أﻟﻢ",
"ﻋﯿﻦ"[{,
"أﻟﻢ": }",)368(vector": self._generate_vector
category": "emotion", "related"": ]"ﺣﺰن", "ﺑﻜﺎء", "ﻣﻌﺎﻧﺎة",
"ﻣﺮض"[{,
# ﻣﺸﺘﻘﺎت اﻷﻟﻮان
"ﻟﻮن": }",)380(vector": self._generate_vector
category": "color", "related"": ]"أﺣﻤﺮ", "أزرق", "أﺧﻀﺮ",
"أﺻﻔﺮ"[{,
"أﺑﯿﺾ": }",)381(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﺛﻠﺞ", "ﻧﻮر", "ﻧﻘﺎء"[{,
"أﺳﻮد": }",)382(vector": self._generate_vector
category": "color", "related"": ]"ﻟﻮن", "ﻟﯿﻞ", "ﻇﻼم", "ﻓﺤﻢ"[{,
# إﺿﺎﻓﺎت ﻣﺘﻨﻮﻋﺔ
"وﻗﺖ": }",)400(vector": self._generate_vector
category": "time", "related"": ]"ﺳﺎﻋﺔ", "دﻗﯿﻘﺔ", "ﯾﻮم", "ﺷﮭﺮ",
"ﺳﻨﺔ"[{,
"ﺳﺎﻋﺔ": }",)401(vector": self._generate_vector
category": "time", "related"": ]"وﻗﺖ", "دﻗﯿﻘﺔ", "ﺛﺎﻧﯿﺔ",
ﯾﻮم"[{,
"
"ﯾﻮم": }",)402(vector": self._generate_vector
category": "time", "related"": ]"وﻗﺖ", "ﻟﯿﻞ", "ﻧﮭﺎر",
"أﺳﺒﻮع"[{,
"ﻟﯿﻠﺔ": }",)403(vector": self._generate_vector
category": "time", "related"": ]"ﻟﯿﻞ", "ﯾﻮم", "ﻧﻮم", "أﺣﻼم"[{,
"ﺻﺒﺎح": }",)404(vector": self._generate_vector
category": "time", "related"": ]"ﻧﮭﺎر", "ﯾﻮم", "ﻓﻄﻮر", "ﺷﻤﺲ"[{,
"ﻣﺴﺎء": }",)405(vector": self._generate_vector
category": "time", "related"": ]"ﻟﯿﻞ", "ﯾﻮم", "ﻋﺸﺎء", "ﻏﺮوب"[{,
"ﻣﺎل": }",)420(vector": self._generate_vector
category": "money", "related"": ]"ﻓﻠﻮس", "ﺛﺮوة", "دﺧﻞ",
"ﻣﺼﺎرﯾﻒ"[{,
"ﻓﻠﻮس": }",)421(vector": self._generate_vector
category": "money", "related"": ]"ﻣﺎل", "ﻧﻘﺪ", "دﻓﻊ", "ﺷﺮاء"[{,
"ﻋﻤﻞ": }",)422(vector": self._generate_vector
category": "work", "related"": ]"وﻇﯿﻔﺔ", "ﻣﮭﻨﺔ", "ﻣﻜﺘﺐ",
"دﺧﻞ"[{,
"وﻇﯿﻔﺔ": }",)423(vector": self._generate_vector
category": "work", "related"": ]"ﻋﻤﻞ", "ﻣﮭﻨﺔ", "راﺗﺐ",
"ﻣﻜﺘﺐ"[{,
"ﻣﺪرس": }",)424(vector": self._generate_vector
category": "work", "related"": ]"ﺗﻌﻠﯿﻢ", "ﻣﺪرﺳﺔ", "ﻃﺎﻟﺐ",
"درس"[{,
"دﻛﺘﻮر": }",)425(vector": self._generate_vector
category": "work", "related"": ]"ﻃﺒﯿﺐ", "ﺻﺤﺔ", "ﻣﺴﺘﺸﻔﻰ",
"ﻋﻼج"[{,
"ﻣﮭﻨﺪس": }",)426(vector": self._generate_vector
category": "work", "related"": ]"ﺑﻨﺎء", "ﺗﺼﻤﯿﻢ", "ﻋﻤﻞ",
"ﻣﻜﺘﺐ"[{,
"ﻣﺪﯾﻨﺔ": }",)440(vector": self._generate_vector
category": "city", "related"": ]"ﺑﻠﺪ", "ﺷﺎرع", "ﻣﺒﻨﻰ",
"ﺳﻜﺎن"[{,
"ﺑﻠﺪ": }",)441(vector": self._generate_vector
category": "city", "related"": ]"ﻣﺪﯾﻨﺔ", "ﻗﺮﯾﺔ", "دوﻟﺔ",
"وﻃﻦ"[{,
"ﺷﺎرع": }",)442(vector": self._generate_vector
category": "city", "related"": ]"ﻣﺪﯾﻨﺔ", "ﻃﺮﯾﻖ", "ﺳﯿﺎرة",
"ﻣﺤﻞ"[{,
"ﻣﺒﻨﻰ": }",)443(vector": self._generate_vector
category": "city", "related"": ]"ﻣﺪﯾﻨﺔ", "ﺑﺮج", "ﺑﯿﺖ",
"ﻣﻜﺘﺐ"[{,
"ﺣﺪﯾﻘﺔ": }",)444(vector": self._generate_vector
category": "city", "related"": ]"ﻣﺪﯾﻨﺔ", "زھﺮ", "ﺷﺠﺮ",
"ﻃﺒﯿﻌﺔ"[{,
"ﻣﻮﺳﯿﻘﻰ": }",)460(vector": self._generate_vector
category": "art", "related"": ]"ﻏﻨﺎء", "آﻟﺔ", "ﻋﺰف", "أﻏﻨﯿﺔ"[{,
"ﻏﻨﺎء": }",)461(vector": self._generate_vector
category": "art", "related"": ]"ﻣﻮﺳﯿﻘﻰ", "ﺻﻮت", "أﻏﻨﯿﺔ",
"ﻓﻦ"[{,
"رﻗﺺ": }",)462(vector": self._generate_vector
category": "art", "related"": ]"ﻣﻮﺳﯿﻘﻰ", "ﺣﺮﻛﺔ", "ﻓﻦ",
"اﺣﺘﻔﺎل"[{,
"ﻓﻦ": }",)463(vector": self._generate_vector
category": "art", "related"": ]"إﺑﺪاع", "ﺟﻤﺎل", "ﻟﻮﺣﺔ",
"ﻣﻮﺳﯿﻘﻰ"[{,
"ﻟﻮﺣﺔ": }",)464(vector": self._generate_vector
category": "art", "related"": ]"ﻓﻦ", "رﺳﻢ", "أﻟﻮان", "ﻓﻨﺎن"[{,
"ﻣﺴﺮح": }",)465(vector": self._generate_vector
category": "art", "related"": ]"ﻓﻦ", "ﺗﻤﺜﯿﻞ", "ﻣﻤﺜﻞ",
"ﻣﺴﺮﺣﯿﺔ"[{,
"ﺳﯿﻨﻤﺎ": }",)466(vector": self._generate_vector
category": "art", "related"": ]"ﻓﯿﻠﻢ", "ﻣﺸﺎھﺪة", "ﺗﺮﻓﯿﮫ",
"أﻓﻼم"[{,
"ﻓﯿﻠﻢ": }",)467(vector": self._generate_vector
category": "art", "related"": ]"ﺳﯿﻨﻤﺎ", "ﻣﺸﺎھﺪة", "ﻗﺼﺔ",
"ﺗﻤﺜﯿﻞ"[{,
"أﻏﻨﯿﺔ": }",)468(vector": self._generate_vector
category": "art", "related"": ]"ﻣﻮﺳﯿﻘﻰ", "ﻏﻨﺎء", "ﺻﻮت",
"ﻛﻠﻤﺎت"[{,
"ﺻﺤﺔ": }",)480(vector": self._generate_vector
category": "health", "related"": ]"ﺟﺴﻢ", "رﯾﺎﺿﺔ", "ﻃﻌﺎم",
"ﻧﻮم"[{,
"ﺟﺴﻢ": }",)481(vector": self._generate_vector
category": "health", "related"": ]"ﺻﺤﺔ", "ﻋﻀﻼت", "رﯾﺎﺿﺔ",
"ﻟﯿﺎﻗﺔ"[{,
"رﯾﺎﺿﺔ": }",)482(vector": self._generate_vector
category": "health", "related"": ]"ﺻﺤﺔ", "ﺟﺴﻢ", "ﻟﯿﺎﻗﺔ",
"ﺗﻤﺎرﯾﻦ"[{,
"ﻧﻮم": }",)483(vector": self._generate_vector
category": "health", "related"": ]"ﺻﺤﺔ", "راﺣﺔ", "ﻟﯿﻞ",
ﺳﺮﯾﺮ"[{,
"
"ﻃﻌﺎم": }",)484(vector": self._generate_vector
category": "health", "related"": ]"ﺻﺤﺔ", "أﻛﻞ", "وﺟﺒﺔ",
"ﻏﺬاء"[{,
}
self.word_database.update(additional_words)
def calculate_similarity(self, word1, word2):
"""ﺣﺴﺎب اﻟﺘﺸﺎﺑﮫ ﺑﯿﻦ ﻛﻠﻤﺘﯿﻦ"""
clean1 = self.normalize_arabic(word1)
clean2 = self.normalize_arabic(word2)
# اﻟﺘﺤﻘﻖ ﻣﻦ اﻟﺘﻄﺎﺑﻖ اﻟﺘﺎم
if clean1 == clean2:
return 1.0
# اﺳﺘﺨﺪام اﻟﻨﻈﺎم اﻟﺒﺪﯾﻞ )ﺳﺮﯾﻊ وﻓﻌﺎل(
return self._fallback_similarity(clean1, clean2)
def _fallback_similarity(self, word1, word2):
"""ﻧﻈﺎم ﺑﺪﯾﻞ ﻟﺤﺴﺎب اﻟﺘﺸﺎﺑﮫ"""
# اﻟﺒﺤﺚ ﻓﻲ ﻗﺎﻋﺪة اﻟﺒﯿﺎﻧﺎت
data1 = self.word_database.get(word1)
data2 = self.word_database.get(word2)
if not data1 or not data2:
# إذا إﺣﺪى اﻟﻜﻠﻤﺎت ﻏﯿﺮ ﻣﻮﺟﻮدة، اﺳﺘﺨﺪم اﻟﺘﺸﺎﺑﮫ اﻟﺤﺮﻓﻲ
return self._string_similarity(word1, word2)
ً ﻋﻠﻰ اﻟﻔﺌﺔ واﻟﻜﻠﻤﺎت اﻟﻤﺮﺗﺒﻄﺔ
# ﺣﺴﺎب اﻟﺘﺸﺎﺑﮫ ﺑﻨﺎء
score = 0.0
# ﻧﻔﺲ اﻟﻔﺌﺔ = ﺗﺸﺎﺑﮫ ﻋﺎل
ٍ
if data1["category"] == data2["category"]:
score += 0.4
# ﻛﻠﻤﺎت ﻣﺮﺗﺒﻄﺔ ﻣﺒﺎﺷﺮة
if word2 in data1.get("related", []):
score += 0.5
if word1 in data2.get("related", []):
score += 0.5
# ﻛﻠﻤﺎت ﻣﺮﺗﺒﻄﺔ ﺑﺸﻜﻞ ﻏﯿﺮ ﻣﺒﺎﺷﺮ
related1 = set(data1.get("related", []))
related2 = set(data2.get("related", []))
common = related1 & related2
if common:
score += len(common) * 0.1
# ﺗﺸﺎﺑﮫ اﻟﻤﺘﺠﮭﺎت )ﺑﺪون numpy(
vec1 = data1["vector"]
vec2 = data2["vector"]
cosine_sim = cosine_similarity(vec1, vec2)
score += max(0, cosine_sim) * 0.3
return min(1.0, score)
def _string_similarity(self, s1, s2):
"""ﺗﺸﺎﺑﮫ ﻧﺼﻲ ﺑﺴﯿﻂ"""
# ﺣﺴﺎب اﻟﺤﺮوف اﻟﻤﺸﺘﺮﻛﺔ
set1 = set(s1)
set2 = set(s2)
intersection = len(set1 & set2)
union = len(set1 | set2)
if union == 0:
return 0.0
jaccard = intersection / union
# ﺗﺸﺎﺑﮫ اﻟﺒﺎدﺋﺔ
prefix_match = 0
for i in range(min(len(s1), len(s2))):
if s1[i] == s2[i]:
prefix_match += 1
else:
break
prefix_bonus = prefix_match / max(len(s1), len(s2)) *
0.2
return min(1.0, jaccard * 0.5 + prefix_bonus)
def get_word_rank(self, guess_word, secret_word):
"""ﺣﺴﺎب ﺗﺮﺗﯿﺐ اﻟﺘﺨﻤﯿﻦ )1 = اﻷﻗﺮب("""
similarity = self.calculate_similarity(guess_word,
secret_word)
# ﺗﺤﻮﯾﻞ اﻟﺘﺸﺎﺑﮫ )0-1( إﻟﻰ ﺗﺮﺗﯿﺐ )1-10000(
# ﻛﻠﻤﺎ زاد اﻟﺘﺸﺎﺑﮫ، ﻗﻞ اﻟﺘﺮﺗﯿﺐ
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
"""اﻟﺤﺼﻮل ﻋﻠﻰ ﻛﻠﻤﺔ اﻟﯿﻮم"""
today = date.today()
# اﻟﺘﺤﻘﻖ ﻣﻤﺎ إذا ﻛﺎﻧﺖ اﻟﻜﻠﻤﺔ ﻗﺪ ﺗﻐﯿﺮت
if self.last_word_date != today or not self.daily_word:
ً ﻋﻠﻰ اﻟﺘﺎرﯾﺦ
# ﺗﻮﻟﯿﺪ ﻛﻠﻤﺔ ﻋﺸﻮاﺋﯿﺔ ﺑﻨﺎء
random.seed(today.toordinal())
words = list(self.vocabulary)
self.daily_word = random.choice(words)
self.last_word_date = today
print(f"! Daily word for {today}:
{self.daily_word}")
return self.daily_word
def get_hint(self, secret_word):
"""اﻟﺤﺼﻮل ﻋﻠﻰ ﺗﻠﻤﯿﺢ )ﻛﻠﻤﺔ ﻗﺮﯾﺒﺔ("""
data = self.word_database.get(secret_word, {})
related = data.get("related", [])
if related:
return random.choice(related)
# إذا ﻟﻢ ﺗﻮﺟﺪ ﻛﻠﻤﺎت ﻣﺮﺗﺒﻄﺔ، اﺧﺘﺮ ﻛﻠﻤﺔ ﻋﺸﻮاﺋﯿﺔ ﻣﻦ ﻧﻔﺲ
category = data.get("category", "general")
same_category = [w for w, d in
self.word_database.items()
if d.get("category") == category and
w != secret_word]
if same_category:
return random.choice(same_category)
return None
def is_valid_word(self, word):
"""اﻟﺘﺤﻘﻖ ﻣﻦ ﺻﺤﺔ اﻟﻜﻠﻤﺔ"""
clean = self.normalize_arabic(word)
return len(clean) >= 2 and all('\u0600' <= c <=
'\u06FF' or c.isspace() for c in clean)
اﻟﻔﺌﺔ
#
===============================================================
=============
# Initialize NLP System
#
===============================================================
=============
nlp = ArabicWordEmbedding()
#
===============================================================
=============
# Game State Management
#
===============================================================
=============
class GameState:
"""إدارة ﺣﺎﻟﺔ اﻟﻠﻌﺒﺔ ﻟﻜﻞ ﺟﻠﺴﺔ"""
def __init__(self):
self.sessions = {}
def get_or_create_session(self, session_id):
"""اﻟﺤﺼﻮل ﻋﻠﻰ ﺟﻠﺴﺔ أو إﻧﺸﺎؤھﺎ"""
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
"""إﻋﺎدة ﺗﻌﯿﯿﻦ اﻟﺠﻠﺴﺔ"""
self.sessions[session_id] = {
'guesses': [],
'hints_used': 0,
'game_over': False,
'won': False,
'secret_word': nlp.get_daily_word()
}
return self.sessions[session_id]
game_state = GameState()
#
===============================================================
=============
# API Routes
#
===============================================================
=============
@app.route('/')
def index():
"""اﻟﺼﻔﺤﺔ اﻟﺮﺋﯿﺴﯿﺔ"""
return render_template('index.html')
@app.route('/api/daily-word', methods=['GET'])
def get_daily_word_api():
"""اﻟﺤﺼﻮل ﻋﻠﻰ ﻛﻠﻤﺔ اﻟﯿﻮم )ﻣﺨﻔﯿﺔ("""
return jsonify({
'success': True,
'message': 'Game initialized',
'date': date.today().isoformat()
)}
@app.route('/api/guess', methods=['POST'])
def make_guess():
"""ﺗﻘﺪﯾﻢ ﺗﺨﻤﯿﻦ"""
data = request.get_json()
word = data.get('word', '').strip()
session_id = data.get('session_id', 'default')
if not word:
provided'}), 400
return jsonify({'success': False, 'error': 'No word
# اﻟﺘﺤﻘﻖ ﻣﻦ أن اﻟﻜﻠﻤﺔ ﻋﺮﺑﯿﺔ
if not nlp.is_valid_word(word):
return jsonify({'success': False, 'error': 'Please
enter Arabic words only'}), 400
session = game_state.get_or_create_session(session_id)
secret_word = session['secret_word']
# اﻟﺘﺤﻘﻖ ﻣﻦ اﻟﺘﻜﺮار
normalized_guess = nlp.normalize_arabic(word)
existing_guesses = [nlp.normalize_arabic(g['word']) for g
in session['guesses']]
if normalized_guess in existing_guesses:
return jsonify({
'success': True,
'duplicate': True,
'message': 'Word already guessed'
)}
# ﺣﺴﺎب اﻟﺘﺮﺗﯿﺐ
rank = nlp.get_word_rank(word, secret_word)
# إﺿﺎﻓﺔ اﻟﺘﺨﻤﯿﻦ
guess_data = {
'word': word,
'rank': rank,
'is_hint': False
}
session['guesses'].append(guess_data)
# اﻟﺘﺤﻘﻖ ﻣﻦ اﻟﻔﻮز
is_correct = normalized_guess ==
nlp.normalize_arabic(secret_word)
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
)}
@app.route('/api/hint', methods=['POST'])
def get_hint_api():
"""اﻟﺤﺼﻮل ﻋﻠﻰ ﺗﻠﻤﯿﺢ"""
data = request.get_json()
session_id = data.get('session_id', 'default')
session = game_state.get_or_create_session(session_id)
if session['game_over']:
return jsonify({'success': False, 'error': 'Game is
over'}), 400
secret_word = session['secret_word']
hint_word = nlp.get_hint(secret_word)
if not hint_word:
available'}), 500
return jsonify({'success': False, 'error': 'No hint
# اﻟﺘﺤﻘﻖ ﻣﻦ ﻋﺪم ﺗﻜﺮار اﻟﺘﻠﻤﯿﺢ
normalized_hint = nlp.normalize_arabic(hint_word)
existing_guesses = [nlp.normalize_arabic(g['word']) for g
in session['guesses']]
if normalized_hint in existing_guesses:
# اﺧﺘﯿﺎر ﺗﻠﻤﯿﺢ آﺧﺮ
attempts = 0
while normalized_hint in existing_guesses and attempts
:10 <
hint_word = nlp.get_hint(secret_word)
normalized_hint = nlp.normalize_arabic(hint_word)
attempts += 1
if normalized_hint in existing_guesses:
return jsonify({'success': False, 'error': 'No new
hint available'}), 400
rank = nlp.get_word_rank(hint_word, secret_word)
# ﺣﺴﺎب ﺗﺮﺗﯿﺐ اﻟﺘﻠﻤﯿﺢ
# إﺿﺎﻓﺔ اﻟﺘﻠﻤﯿﺢ
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
)}
@app.route('/api/give-up', methods=['POST'])
def give_up():
"""اﻻﺳﺘﺴﻼم"""
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
)}
@app.route('/api/reset', methods=['POST'])
def reset_game():
"""إﻋﺎدة ﺗﻌﯿﯿﻦ اﻟﻠﻌﺒﺔ"""
data = request.get_json()
session_id = data.get('session_id', 'default')
session = game_state.reset_session(session_id)
return jsonify({
'success': True,
'message': 'Game reset successfully'
)}
@app.route('/api/stats', methods=['GET'])
def get_stats():
"""اﻟﺤﺼﻮل ﻋﻠﻰ إﺣﺼﺎﺋﯿﺎت اﻟﻠﻌﺒﺔ"""
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
)}
@app.route('/api/test-similarity', methods=['POST'])
def test_similarity():
"""اﺧﺘﺒﺎر ﺗﺸﺎﺑﮫ ﻛﻠﻤﺘﯿﻦ )ﻟﻠﺘﺠﺮﺑﺔ("""
data = request.get_json()
word1 = data.get('word1', '')
word2 = data.get('word2', '')
if not word1 or not word2:
return jsonify({'success': False, 'error': 'Two words
required'}), 400
similarity = nlp.calculate_similarity(word1, word2)
rank = nlp.get_word_rank(word1, word2)
return jsonify({
'success': True,
'word1': word1,
'word2': word2,
'similarity': round(similarity, 4),
'rank': rank
)}
@app.route('/api/health', methods=['GET'])
def health_check():
"""ﻓﺤﺺ ﺻﺤﺔ اﻟﺴﯿﺮﻓﺮ"""
return jsonify({
'success': True,
'status': 'healthy',
'vocabulary_size': len(nlp.vocabulary),
'daily_word_date': date.today().isoformat()
)}
#
===============================================================
=============
# Main Entry Point
#
===============================================================
=============
if __name__ == '__main__':
port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port, debug=True)

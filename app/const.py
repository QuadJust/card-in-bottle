#!/usr/bin/env python
#coding:utf-8

__author__ = "Shinri Ishikawa <justlikebussiness@google.com>"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "20 June 2019"

import logging

# Logging level
LOG_LEVEL = logging.DEBUG
# For CentOS
MECAB_IPADIC_PATH = '/usr/lib64/mecab/dic/mecab-ipadic-neologd'
# For Ubuntu
#MECAB_IPADIC_PATH = '/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd'

# Hiragana tupple
HIRA_TUPPLE = ('あ','い','う','え','お','か','き','く','け','こ','さ','し','す','せ','そ','た','ち','つ','て','と','な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ','ま','み','む','め','も','や','ゆ','よ','ら','り','る','れ','ろ','わ','を','ん','っ','ゃ','ゅ','ょ','ー','が','ぎ','ぐ','げ','ご','ざ','じ','ず','ぜ','ぞ','だ','ぢ','づ','で','ど','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ')
# Katakana tupple
KATA_TUPPLE = ('ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','サ','シ','ス','セ','ソ','タ','チ','ツ','テ','ト','ナ','ニ','ヌ','ネ','ノ','ハ','ヒ','フ','ヘ','ホ','マ','ミ','ム','メ','モ','ヤ','ユ','ヨ','ラ','リ','ル','レ','ロ','ワ','ヲ','ン','ッ','ャ','ュ','ョ','ー','ガ','ギ','グ','ゲ','ゴ','ザ','ジ','ズ','ゼ','ゾ','ダ','ヂ','ヅ','デ','ド','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ')
#
COGNITIVE_API_URL = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/ocr'
#
COGNITIVE_API_KEY = '7f659cdd87214fef9d0b5398060f71bf'
# Tupple of company form
JP_COMPANY_FORM_TUPPLE = ('株式会社','合同会社', '合資会社', '合名会社', '有限会社')
# 
JP_PREF_TUPPLE = (
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', 
    '山形県', '福島県', '茨城県', '栃木県', '群馬県', 
    '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', 
    '富山県', '石川県', '福井県', '山梨県', '長野県', 
    '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', 
    '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', 
    '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', 
    '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', 
    '鹿児島県', '沖縄県'
)

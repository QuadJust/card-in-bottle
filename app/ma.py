import sys
import datetime
import logging
from logging import getLogger, StreamHandler, Formatter
import MeCab
from const import *

# Morphological analysis class 
class Ma(object):
    # Construct
    def __init__(self):
        # Initialize logger
        logger = getLogger('MA')
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(filename='cib_' + datetime.datetime.today().strftime('%Y%m%d') + '.log')
        handler.setLevel(LOG_LEVEL)
        handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(handler_format)
        logger.addHandler(handler)
        self.logger = logger
    
    # Analyze Morpheme
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def analyze(self, text):
        tagger = MeCab.Tagger('-d ' + MECAB_IPADIC_PATH)
        r = []

        for chunk in tagger.parse(text).splitlines()[:-1]:
            surface, feature = chunk.split('\t')
            # 翻訳に失敗した場合、テキストをそのまま使用する
            if len(feature.split(",")) <= 7:
                r.append(text)
            else:
                r.append(feature.split(",")[7])
        
        result = ("".join(r)).strip()
        return result
    
    # Convert Katakana to Hiragana
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def convert_kata_to_hira(self, katakana):
        k_to_h_dict = dict()

        for i in range(len(HIRA_TUPPLE)):
            k_to_h_dict[KATA_TUPPLE[i]] = HIRA_TUPPLE[i]

        hiragana = ''

        for i in range(len(katakana)):
            hiragana += k_to_h_dict[katakana[i]]

        return hiragana


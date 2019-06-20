#!/usr/bin/env python
#coding:utf-8

import sys
import datetime
import logging
from logging import getLogger, StreamHandler, Formatter
import MeCab
from const import *

__author__ = "Shinri Ishikawa<justlikebussiness@google.com>"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "20 June 2019"

class Ma(object):
    """
    Morphological analysis class 
    """
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

        return tagger.parse(text)
    
    # Analyze Morpheme
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def analyze_wakati(self, text):
        tagger = MeCab.Tagger('-Owakati')

        return tagger.parse(text)
    
    # Analyze Morpheme
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def analyze_list(self, text):
        result = []

        wakati_text = self.analyze_wakati(text)
        tagger = MeCab.Tagger('-d' + MECAB_IPADIC_PATH)

        for c1 in wakati_text.split(' '):
            for c2 in tagger.parse(c1).splitlines()[:-1]:
                line = {}
                surface, feature = c2.split('\t')
                features = feature.split(",")

                line['surface'] = surface
                if len(features) > 7:
                    line['pos'] = features[0]
                    line['pos_type1'] = features[1]
                    line['pos_type2'] = features[2]
                    line['pos_type3'] = features[3]
                    line['kata'] = features[7]
                else:
                    line['pos'] = ''
                    line['pos_type1'] = ''
                    line['pos_type2'] = ''
                    line['pos_type3'] = ''
                    line['kata'] = ''

                result.append(line)

        return result
    
    # Analyze Morpheme
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def analyze_kana(self, text):
        tagger = MeCab.Tagger('-d ' + MECAB_IPADIC_PATH)
        r = []

        for chunk in tagger.parse(text).splitlines()[:-1]:
            surface, feature = chunk.split('\t')
            # 翻訳に失敗した場合、テキストをそのまま使用する
            if len(feature.split(",")) > 7:
                r.append(feature.split(",")[7])
            else:
                r.append(surface)
        
        result = ("".join(r)).strip()
        return result
    
    # Analyze Morpheme
    # @see https://qiita.com/Hirai0827/items/917d324f3f4d2b7d3134
    def analyze_name(self, text):
        tagger = MeCab.Tagger('-d ' + MECAB_IPADIC_PATH)
        r = []

        for chunk in tagger.parse(text).splitlines()[:-1]:
            surface, feature = chunk.split('\t')
            # 翻訳に失敗した場合、テキストをそのまま使用する
            if len(feature.split(",")) > 7:
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


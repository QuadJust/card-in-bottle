#!/usr/bin/env python
#coding:utf-8

import sys
import json
import datetime
import re
import uuid
import cv2
import requests
import threading
import numpy
from logging import getLogger, StreamHandler, FileHandler, Formatter
import pandas as pd
import xml.etree.ElementTree as ET
from cerberus import Validator

from ocr import Ocr
from ma import Ma
from const import *

# Bzcard class
class Bzcard(Ocr, Ma):
    # Validator schema
    schema = {
        'ip': {
            'type': 'string',
            'empty': False
        },
        'corp': {
            'type': 'string',
            'empty': False
        },
        'user': {
            'type': 'string',
            'empty': False
        },
        'RequestURL': {
            'type': 'string',
            'empty': True,
            'nullable': True
        },
        'lang': {
            'type': 'integer',
            'empty': True,
            'nullable': True,
            # FIXME Take any of the values
            'min': 1,
            'max': 4
        },
        'langchar': {
            'type': 'integer',
            'empty': True,
            'nullable': True,
        },
        'cnt': {
            'type': 'integer',
            'empty': False
        },
        'imgno': {
            'type': 'integer',
            'empty': False
        },
        'cardtype': {
            'type': 'integer',
            'empty': True,
            'nullable': True,
            # FIXME Take any of the values
            'min': 0,
            'max': 1
        },
        'cardou': {
            'type': 'integer',
            'empty': True,
            'nullable': True,
            # FIXME Take any of the values
            'min': 0,
            'max': 2
        },
        'pflg': {
            'type': 'integer',
            'empty': False,
            # FIXME Take any of the values
            'min': 0,
            'max': 1
        },
        'company': {
            'type': 'string',
            'empty': False
        }
    }
    
    # Construct
    def __init__(self) :
        logger = getLogger('Bzcard OCR')
        logger.setLevel(LOG_LEVEL)
        handler = FileHandler(filename='cib_' + datetime.datetime.today().strftime('%Y%m%d') + '.log')
        handler.setLevel(LOG_LEVEL)
        handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(handler_format)
        logger.addHandler(handler)
        self.logger = logger
    
    def in_bottle(self, forms, files):
        self.logger.debug(sys._getframe().f_code.co_name + ' called') 
        self.result = 1
        # Post data
        try:
            ip = forms.get('ip') # ipaddress
            corp = forms.get('corp') # corp id
            user = forms.get('user') # user id
            RequestURL = forms.get('RequestURL') # request url
            lang = int(forms.get('lang')) # language
            langchar = int(forms.get('langchar')) # language character?
            cnt = int(forms.get('cnt')) # card count(fixed 1)
            imgno = int(forms.get('imgno')) # image number
            cardtype = int(forms.get('cardtype')) # card type(single or compress)
            cardou = int(forms.get('cardou')) # omote ura
            pflg = int(forms.get('pflg')) # personal flg
            company = forms.get('company') # company id

            img1 = files.get('img1', '') # omote image
        except ValueError as e:
            return e.message
        
        if img1 is None:
            return {'img1': ['null value not allowed']}
             

        # Post data
        data = {
            'ip': ip,
            'corp': corp,
            'user': user,
            'RequestURL': RequestURL,
            'lang': lang,
            'langchar': langchar,
            'cnt': cnt,
            'imgno': imgno,
            'cardtype': cardtype,
            'cardou': cardou,
            'pflg': pflg,
            'company': company,
        }

        v = Validator(self.schema)

        #if (v.validate(data)):
        msg = 'IP:%s\t' \
        'Pflg:%s\t' \
        'Corp:%s\t' \
        'User:%s\t' \
        'ImgNo:%s\t' \
        'Cnt:%s\t' \
        'Lang:%s\t' \
        'LangChar:%s\t' \
        'cardtype:%s\t' \
        'cardou:%s\t' \
        'ImgQuality:%s\t' \
        % (ip, pflg, corp, user, imgno, cnt, lang, langchar, cardtype, cardou, '0')
        
        thread = threading.Thread(target=self.write_reply, args=(forms, files))
        thread.start()

        self.result = 0
        #else:
        #    msg = v.errors
        self.logger.debug(sys._getframe().f_code.co_name + ' end')
        return msg
    
    def write_reply(self, forms, files):
        self.logger.debug(sys._getframe().f_code.co_name + ' start')
        
        # Post Data
        ip = forms.get('ip') # ipaddress
        corp = forms.get('corp') # corp id
        user = forms.get('user') # user id
        RequestURL = forms.get('RequestURL') # request url
        lang = int(forms.get('lang')) # language
        langchar = int(forms.get('langchar')) # language character?
        cnt = int(forms.get('cnt')) # card count(fixed 1)
        imgno = int(forms.get('imgno')) # image number
        cardtype = int(forms.get('cardtype')) # card type(single or compress)
        cardou = int(forms.get('cardou')) # omote ura
        pflg = int(forms.get('pflg')) # personal flg
        company = forms.get('company') # company id

        img1 = files.get('img1', '') # omote image
        img2 = files.get('img2', '') # ura image

        try:
            # TODO Generate csv
            file_name = self.__get_file_name(imgno, 0, 0)
            img1.save(file_name)
            shape = self.__wide_or_high(file_name)

            # Determin langage
            if lang == 1:
                lang_code = 'ja'
                #if shape == 'w':
                #    lang = 'jpn'
                #else:
                #    lang = 'jpn_vert'
            elif lang == 2:
                lang_code = 'en'
            elif lang == 3:
                lang_code = 'zh-Hans'
                #if shape == 'w':
                #    lang = 'chi'
                #else:
                #    lang = 'chi_vert'
            elif lang == 4:
                lang_code = 'ko'
                #if shape == 'w':
                #    lang = 'kor'
                #else:
                #    lang = 'kor_vert'
            else:
                raise ValueError('Invalid lang code!')

            csv = self.__ms_cognitive_service(file_name, lang_code)

            # Create http client
            # Header settings
            #headers = {
            #    'Content-Type': 'multipart/form-data'
            #}
            # Parameters
            params = {
                'ret': 0,
                'id': corp,
                'impid': imgno,
                'userid': user,
                'cnt': 1
            }
            files = {
                'img1': img1.file,
                'csv': csv
            }

            # リクエストの生成
            #req = urllib.request.Request(RequestURL, params, files=files, headers=headers)
            # リクエストの送信
            res = requests.post(RequestURL, params, files=files)
            # レスポンスの取得
            #r = res.read()
            
            print(res)
        except Exception as e:
            print(e)
            self.logger.exception(e)
        
        self.logger.debug(sys._getframe().f_code.co_name + ' finished')

        return 

    # Generate mock csv file
    def __generate_mock_csv(self):
        # Generate random uuid
        tmp_csv = str(uuid.uuid4()) + '.csv'
        # Create DataFrame
        df = pd.DataFrame([["","","マーケティング事業部","","佐藤","サトウ","美咲","ミサキ","","","","","03-0000-0000","","","","","","","","","","e-iuailxxx@xxx.co.p","","www.a-one.oo.jpl","",0,0,0,0,0,"w_18523_0_0_190327124016253.jpg",0]])
        df.to_csv(tmp_csv, index=False, header=False)
        return tmp_csv

    # Generate csv file
    def __generate_csv(self):

        return
    
    # Determine and return filename
    def __get_file_name(self, imgno, index, a_index):
        my_time = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
        return '_'.join([str(imgno), str(index), str(a_index), my_time]) + '.jpg'

    # Determine whether image is High or Wide 
    def __wide_or_high(self, img_name):
        quad = cv2.imread(img_name, 0)
        height, width = quad.shape[:2]

        if height > width:
            return 'h'
        else:
            return 'w'
    
    # OCR by Tesseract
    def __tesseract(self, img, lang):

        hocr = self.to_hocr(img, lang)
        elem = ET.fromstring(hocr)

        # 要素のタグを取得
        for e in elem.getiterator("body"):
            if e.items()[0] == 'class' and e.items()[1] == 'ocr_line':
                for e2 in elem.getiterator():
                    if e.items()[0] == 'class' and e.items()[1] == 'ocrx_word':
                        print('')

        return 

     # OCR by MicroSoft Cognitive Service
    # @see https://docs.microsoft.com/ja-jp/azure/cognitive-services/computer-vision/quickstarts/python-disk
    # @see https://azure-recipe.kc-cloud.jp/2017/07/cognitive-services-computer-vision-3/
    def __ms_cognitive_service(self, img, lang):
        # Read the image into a byte array
        image_data = open(img, "rb").read()

        # Request headers
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': COGNITIVE_API_KEY
        }
        params = {
            'language': lang,
            'detectOrientation ': 'true'
        }
        res = requests.post(COGNITIVE_API_URL, headers=headers, params= params, data=image_data)
        res_data = res.json()

        data = self.__parse_wide_card(res_data)

        ### csvデータ出力 ###
        # CSVヘッダ情報
        #output = [["name" + str(j) for j in range(height_top)] + search_words.keys()]
        #output = {}
        # 行の追加
        #rows = [data[head] if data.get(head) != None else "" for head in output[0]]
        #output.append(rows)
        # CSV文字列化
        #csv = "\n".join(['"' + '","'.join(row) + '"' for row in data])
        csv = '"' + '","'.join(data)
        
        return csv

    def __parse_wide_card(self, res_data):
        # 対象と検索値の設定
        search_words = {
            'company': ['会社'],
            'mail': ['@', '＠'],
            'tel': ['tel', 'phone', '電話', '直通'],
            'fax': ['fax'],
            'zip': ['〒'],
            'address': PREF_TUPPLE,
            'office': ['事業所'],
            'building': ['ビル'],
            'url': ['http', 'www']
        }

        # 各行のテキスト、高さ抽出
        lines = [
            {
                'left': max([int(word['boundingBox'].split(',')[0]) for word in line['words']]), 
                'top': max([int(word['boundingBox'].split(',')[1]) for word in line['words']]), 
                'width': max([int(word['boundingBox'].split(',')[2]) for word in line['words']]),
                'height': max([int(word['boundingBox'].split(',')[3]) for word in line['words']]), 
                'text': ''.join([word['text'] for word in line['words']])
            } 
            for reg_i, region in enumerate(res_data['regions']) 
            for line_i, line in enumerate(region['lines'])
        ]

        print("lines : ")
        print(lines)

        ### 名刺画像内のデータ抽出 ###
        data = {
            'company': '', # 会社名
            'company_k': '', # カイシャカナ
            'affiliation': '', # 部署名
            'exetive': '', # 役職名
            'fname': '',
            'fname_k': '',
            'lname': '',
            'lname_k': '',
            'office': '',
            'zip': '',
            'address': '',
            'building': '',
            'tel': '',
            'fax': '',
            'zip2': '',
            'address2': '',
            'building2': '',
            'tel2': '',
            'fax2': '',
            'mobile': '',
            'mobile2': '',
            'mail': '',
            'mail2': '',
            'url': '',
            'url2': '',
            'x': '0',
            'y': '0',
            'wide': '0',
            'height': '0',
            'rotate': '0',
            'file': '',
            'ou': '0'
        }

        # Make sys.maxsize the biggest int
        min_top = sys.maxsize
        max_top = 0

        for i, line in enumerate(lines):
            # 設定検索条件に基づいてデータを検索、抽出
            for key, words in search_words.items():
                if data.get(key) == None:
                    data.update({key: ''})

                word_match = re.search('|'.join(words), line['text'].lower())
                if word_match and data[key] == '':
                    data[key] = line['text']

                if min_top > line['top']:
                    min_top = line['top']

                if max_top < line['top']:
                    max_top = line['top']
            
            #data.update({'metadata' + str(i): line['text']})

        # TelとFaxが1行になっているものを分割して格納
        if data['tel'].lower().find('fax') >= 0:
            tel_arr = data['tel'].lower().split('fax')
            data['tel'] = tel_arr[0]
            data['fax'] = tel_arr[1]
        
        ### 氏名の抽出 ###
        # 行高の上位数の設定
        height_top = 3
        # 行高の上位抽出
        name_list = sorted(lines, key=lambda x: x['height'], reverse=True)[:height_top]
        # 明確に氏名でない項目の削除
        avg_top = (max_top + max_top) / 2

        idx = numpy.abs(numpy.asarray(list(map(lambda x: x['top'], lines))) - avg_top).argmin()
        name = lines[idx]
        #not_name = [val for key, val in data.items() if key.find('metadata') < 0] # 住所等すでに氏名でないと判明している項目
        #name_list = [name['text'] for name in name_list if name['text'] not in not_name]
        #name_list += [''] * (height_top - len(name_list))
        #data.update({'name' + str(name_i): name for name_i, name in enumerate(name_list)})

        return data.values()

   

#!/usr/bin/env python
#coding:utf-8

import sys
import json
import csv
import datetime
import re
import uuid
import cv2
import requests
import threading
import numpy
from PIL import Image
import io
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
    
    def bottle_in(self, forms, files):
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
        # thread start
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
            # Save file
            img1.save(file_name)
            shape = self.__get_shape(open(file_name, 'rb'))
            c = self.__tesseract(file_name, lang, shape)

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
                'img1': (shape['code'] + '_' + file_name, open(file_name, 'rb')),
                'csv': c
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
    
    # Determine and return filename
    def __get_file_name(self, imgno, index, a_index):
        my_time = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
        return '_'.join([str(imgno), str(index), str(a_index), my_time]) + '.jpg'

    # Determine whether image is High or Wide 
    def __get_shape(self, img):
        img_numpy = numpy.asarray(bytearray(img.read()), dtype=numpy.uint8)
        quad = cv2.imdecode(img_numpy, -1)
        height, width = quad.shape[:2]

        if height > width:
            return {'code': 'h', 'height': height, 'width': width}
        else:
            return {'code': 'w', 'height': height, 'width': width}
    
    # OCR by Tesseract
    def __tesseract(self, file_name, lang, shape):
        # Determin langage
        if lang == 1:
            if shape['code'] == 'w':
                lang_code = 'jpn'
            else:
                lang_code = 'jpn_vert'
        elif lang == 2:
            lang_code = 'eng'
        elif lang == 3:
            if shape['code'] == 'w':
                lang_code = 'chi_sim'
            else:
                lang_code = 'chi_sim_vert'
        elif lang == 4:
            if shape['code'] == 'w':
                lang_code = 'kor'
            else:
                lang_code = 'kor_vert'
        else:
            raise ValueError('Invalid lang code!')

        data = self.to_tsv(file_name, lang_code)
        # 各行のテキスト、高さ抽出
        lines = []
        par_num = 999
        row_text = ''
        row_left = 0
        row_top = 0
        row_width = 0
        row_height = 0
        print(data)
        for i, tsv in enumerate(csv.DictReader(data.splitlines(), delimiter='\t')):
            if i == 0:
                par_num = int(tsv['par_num'])
                row_left = int(tsv['left'])
                row_top = int(tsv['top'])
                row_width = int(tsv['width'])
                row_height = int(tsv['height'])
            if par_num == int(tsv['par_num']):
                row_text = row_text + tsv['text']
                row_left = int(tsv['left']) if int(tsv['left']) < row_left else row_left
                row_top = int(tsv['top']) if int(tsv['top']) < row_left else row_top
                row_width = int(tsv['width']) if int(tsv['width']) > row_width else row_width
                row_height = int(tsv['height']) if int(tsv['height']) > row_height else row_height
            else:
                lines.append({
                    'left': row_left,
                    'top': row_top,
                    'width': row_width,
                    'height': row_height,
                    'text': row_text
                })
                row_text = tsv['text']
                par_num = tsv['par_num']
            

        lines = [
            {
                'left': int(tsv['left']), 
                'top': int(tsv['top']),
                'width': int(tsv['width']),
                'height': int(tsv['height']),
                'text': tsv['text'],
                'line_num': tsv['line_num'] 
            } 
            for i, tsv in enumerate(csv.DictReader(data.splitlines(), delimiter='\t'))
        ]
        
        data = self.__parse_card(lines, shape['code'] + '_' + file_name, shape)
        c = '"' + '","'.join(data.values())
        return c

     # OCR by MicroSoft Cognitive Service
    # @see https://docs.microsoft.com/ja-jp/azure/cognitive-services/computer-vision/quickstarts/python-disk
    # @see https://azure-recipe.kc-cloud.jp/2017/07/cognitive-services-computer-vision-3/
    def __ms_cognitive_service(self, file_name, lang, shape):
        # Determin langage
        if lang == 1:
            lang_code = 'ja'
        elif lang == 2:
            lang_code = 'en'
        elif lang == 3:
            lang_code = 'zh-Hans'
        elif lang == 4:
            lang_code = 'ko'
        else:
            raise ValueError('Invalid lang code!')
        
        # Read the image into a byte array
        #image_data = open(img, "rb").read()

        # Request headers
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': COGNITIVE_API_KEY
        }
        params = {
            'language': lang_code,
            'detectOrientation ': 'true'
        }
        res = requests.post(COGNITIVE_API_URL, headers=headers, params= params, data=open(file_name, 'rb'))
        res_data = res.json()

        # TODO 画像の回転

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
        
        data = self.__parse_card(lines, shape['code'] + '_' + file_name, shape)
        c = '"' + '","'.join(data.values())
        return c

    def __parse_card(self, lines, filename, shape):
        # 対象と検索値の設定
        search_words = {
            # 比較時にはlowercaseを使うものとする
            'company': ['会社', '公司', 'co.', 'ltd.', 'inc.', 'corp.'],
            'mail': ['@', '＠'],
            'tel': ['tel', 'phone', '電話', '直通'],
            'fax': ['fax'],
            'zip': ['〒'],
            'address': JP_PREF_TUPPLE,
            'office': ['事業所'],
            'building': ['ビル'],
            'url': ['http', 'www']
        }

        ### 名刺画像内のデータ抽出 ###
        data = {
            'company': '', # 会社名
            'company_k': '', # カイシャカナ
            'affiliation': '', # 部署名
            'exetive': '', # 役職名
            'fname': '', # 姓
            'fname_k': '', #　セイカナ
            'lname': '', # 名
            'lname_k': '', # メイカナ
            'office': '', 
            'zip': '',
            'address': '',
            'building': '',
            'tel': '',
            'fax': '',
            'office2': '',
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
            'file': filename,
            'ou': '0',
            'dummy': '' # FIXME
        }

        if shape['code'] == 'w':
            direction = 'height'
            measure = 'top'
            center = shape[direction] / 2
        else:
            direction = 'width'
            measure = 'left'
            center = shape[direction] / 2

        # Make sys.maxsize the biggest int
        #min_top = sys.maxsize
        #max_top = 0

        for i, line in enumerate(lines):
            # 設定検索条件に基づいてデータを検索、抽出
            for key, words in search_words.items():
                if data.get(key) == None:
                    data.update({key: ''})

                word_match = re.search('|'.join(words), line['text'].lower())
                if word_match:
                    if data[key] == '':
                        data[key] = line['text']
                        if key + '_k' in data:
                            data[key + '_k'] = self.analyze_kana(line['text'])
                    elif (key + '2') in data and data[key + '2'] == '':
                        data[key + '2'] = line['text']

                #if min_top > line['top']:
                #    min_top = line['top']

                #if max_top < line['top']:
                #    max_top = line['top']
            
            #data.update({'metadata' + str(i): line['text']})

        # TelとFaxが1行になっているものを分割して格納
        if data['tel'].lower().find('fax') >= 0:
            tel_arr = data['tel'].lower().split('fax')
            data['tel'] = tel_arr[0]
            data['fax'] = tel_arr[1]
        
        ### 氏名の抽出 ###
        top = 3
        name_list = sorted(lines, key=lambda x: x[direction], reverse=True)[:top]
        if len(name_list) > 1:
            if name_list[0][direction] - name_list[1][direction] >= 10:
                idx = 0
            else:
                idx = numpy.abs(numpy.asarray([row[measure] for row in name_list]) - center).argmin()
        else:
            idx = 0

        # リストの解析
        data['fname'], data['fname_k'], data['lname'], data['lname_k'], idx = self.__find_name(name_list, idx)
        del name_list[idx]

        # 名前候補で別の重要項目を埋める
        for line in name_list:
            if data['company'] == '':
                data['company'] = line['text']
                data['company_k'] = self.analyze_kana(self.__delete_company_form(line['text']))

            # TODO

        return data

    def __find_name(self, name_list, idx):
        name = name_list[idx]['text']
        self.logger.debug(name_list)
        # リストの解析
        fname, fname_k, lname, lname_k = '','', '', ''
        parts = self.analyze_list(name)
        for i, part in enumerate( parts):
            
            if part['pos_type2'] == '人名' and part['pos_type3'] == '姓':
                if fname == '' and fname_k == '':
                    fname = part['surface']
                    fname_k = part['kata']
                    if i == 0:
                        fname = ''.join(part[1:]['surface'])
                        fname_k = ''.join(part[1:]['kata'])
                        break
                else:
                    lname = part['surface']
                    lname_k = part['kata']
            elif part['pos_type2'] == '人名' and part['pos_type3'] == '名':
                if lname == '' and lname_k == '':
                    lname = part['surface']
                    lname_k = part['kata']
                else:
                    fname = part['surface']
                    fname_k = part['kata']
            elif part['pos_type2'] == '人名' and part['pos_type3'] == '一般':
                f_l_name = self.analyze_wakati(part['surface']).split(' ')
                f_l_name_k = self.analyze_wakati(part['kata']).split(' ')
                if len(f_l_name) >= 2 and f_l_name_k >= 2:
                    fname = f_l_name[0]
                    fname_k = f_l_name_k[0]
                    lname = f_l_name[1]
                    lname_k = f_l_name_k[1]
        
        if fname == '' and fname_k == '' and lname == '' and lname_k == '' and len(name_list) > (idx + 1):
            fname, fname_k, lname, lname_k, idx = self.__find_name(name_list, (idx + 1))

        return fname, fname_k, lname, lname_k, idx

    def __delete_company_form(self, company_name):
        for company_form in JP_COMPANY_FORM_TUPPLE:
            company_name.strip(company_form)
        return company_name
    

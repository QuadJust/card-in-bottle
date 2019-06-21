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
import os
import io
import mimetypes
import zipfile
from logging import getLogger, StreamHandler, FileHandler, Formatter
import pandas as pd
import xml.etree.ElementTree as ET
from cerberus import Validator

from ocr import Ocr
from ma import Ma
from const import *
from keystone import Keystone

__author__ = "Shinri Ishikawa <justlikebussiness@google.com>"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "20 June 2019"

class Bzcard(Ocr, Ma):
    """
    Bzcard class
    """

    file_format = 'jpg'

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
        imgno = forms.get('imgno') # image number
        cardtype = int(forms.get('cardtype')) # card type(single or compress)
        cardou = int(forms.get('cardou')) # omote ura
        pflg = int(forms.get('pflg')) # personal flg
        company = forms.get('company') # company id

        img1 = files.get('img1', '') # omote image
        img2 = files.get('img2', '') # ura image

        try:
            files = {}
            c = []
            index = 0
            a_index = 0
            current_time = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
            file_type = os.path.splitext(img1.raw_filename)[1]

            dir_name = os.path.join(corp, imgno)
            os.makedirs(dir_name)
            errmsg = ''

            # When the upload file is zip 
            if file_type == '.zip' or file_type == '.lzh':
                # Decompression files
                img1.save(img1.raw_filename)
                zipfile.ZipFile(img1.raw_filename).extractall(dir_name)
                # Remove original file
                os.remove(img1.raw_filename)
                # Walk files
                for x in os.listdir(dir_name):
                    try:
                        decfile_path = os.path.join(dir_name, x)
                        if os.path.isfile(decfile_path):
                            # Define file name
                            file_name = '_'.join([imgno, str(index), str(a_index), current_time]) + '.' + self.file_format
                            # Save file as jpeg file
                            im = Image.open(decfile_path)
                            rgb_im = im.convert('RGB') 
                            rgb_im.save(file_name)
                            size = self.__get_size(open(file_name, 'rb'))
                            # OCR
                            c.append(self.__tesseract(file_name, lang, size, a_index))
                            files.update({'img' + str(index):  (size['code'] + '_' + file_name, open(file_name, 'rb'))})
                            index += 1
                            # For japanese mojibake-taisaku
                            errmsg += 'OK : 1 : ' + x.encode('cp437').decode('cp932') + os.linesep
                    except Exception as e:
                        print(e)
                        self.logger.exception(e)
                        errmsg += 'NG : 1 : ' + x + os.linesep
                    finally:
                        os.remove(x)

                files.update({'csv': os.linesep.join(c)})
            elif file_type == '.jpg' or file_type == '.jpeg' or file_type == '.gif' or file_type == '.png' or file_type == '.bmp' or file_type == '.tif' or file_type == '.tiff':
                images = [img1, img2]
                for image in images:
                    if image == '':
                        break
                    try:
                        # Define file name
                        file_name = '_'.join([imgno, str(index), str(a_index), current_time]) + '.' + self.file_format
                        # Save file as jpeg file
                        im = Image.open(image.file)
                        rgb_im = im.convert('RGB') 
                        rgb_im.save(file_name)
                        size = self.__get_size(open(file_name, 'rb'))
                        # OCR
                        c.append(self.__tesseract(file_name, lang, size, a_index))
                        files.update({'img' + str(a_index): (size['code'] + '_' + file_name, open(file_name, 'rb'))})
                        a_index+=1
                    except Exception as e:
                        print(e)
                        self.logger.exception(e)
                        break
                    finally:
                        os.remove(image.raw_filename )

                files.update({'csv': os.linesep.join(c)})
            else:
                return

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
                'cnt': 1,
                'errmsg': errmsg
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
        return '_'.join([str(imgno), str(index), str(a_index), my_time]) + '.' + self.file_format

    # Determine whether image is High or Wide 
    def __get_size(self, img):
        #img_numpy = numpy.asarray(bytearray(img.read()), dtype=numpy.uint8)
        #quad = cv2.imdecode(img_numpy, -1)
        im = Image.open(img.name)
        width, height = im.size

        if height > width:
            return {'code': 'h', 'height': height, 'width': width}
        else:
            return {'code': 'w', 'height': height, 'width': width}
    
    # OCR by Tesseract
    def __tesseract(self, file_name, lang, size, ou=0):
        # Determin langage
        if lang == 1:
            lang_code = 'jpn'
        elif lang == 2:
            lang_code = 'eng'
        elif lang == 3:
            lang_code = 'chi_sim'
        elif lang == 4:
            lang_code = 'kor'
        else:
            raise ValueError('Invalid lang code!')

        data = self.to_tsv(file_name, lang_code)
        # FIXME
        print(data)

        # 各行のテキスト、高さ抽出
        lines = []
        par_num = 999
        line_num = 999
        row_text = ''
        row_left = 0
        row_top = 0
        row_width = 0
        row_height = 0
        
        for i, tsv in enumerate(csv.DictReader(data.splitlines(), delimiter='\t')):
            if i == 0:
                par_num = int(tsv['par_num'])
                line_num = int(tsv['line_num'])
                row_left = int(tsv['left'])
                row_top = int(tsv['top'])
                row_width = int(tsv['width'])
                row_height = int(tsv['height'])
            if par_num == int(tsv['par_num']) and line_num == int(tsv['line_num']):
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
                par_num = int(tsv['par_num'])
                line_num = int(tsv['line_num'])
                row_left = int(tsv['left'])
                row_top = int(tsv['top'])
                row_width = int(tsv['width'])
                row_height = int(tsv['height'])
        
        # Append last row
        lines.append({
            'left': row_left,
            'top': row_top,
            'width': row_width,
            'height': row_height,
            'text': row_text
        })
        row_text = tsv['text']
        par_num = tsv['par_num']
        
        data = self.__parse_card(lines, size['code'] + '_' + file_name, size, ou)
        c =  ','.join(map(lambda x: '"' + x + '"' if type(x) is str else str(x), data.values()))
        return c

    # OCR by MicroSoft Cognitive Service
    # @see https://docs.microsoft.com/ja-jp/azure/cognitive-services/computer-vision/quickstarts/python-disk
    # @see https://azure-recipe.kc-cloud.jp/2017/07/cognitive-services-computer-vision-3/
    def __ms_cognitive_service(self, file_name, lang, size, ou=0):
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
        
        data = self.__parse_card(lines, size['code'] + '_' + file_name, size, ou)
        c =  ','.join(map(lambda x: '"' + x + '"' if type(x) is str else str(x), data.values()))
        return c

    def __parse_card(self, lines, filename, size, ou=0):
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
            'office': '', # 事業所
            'zip': '', # 郵便番号
            'address': '', # 住所
            'building': '', # 建物  
            'tel': '', # 電話番号
            'fax': '', # FAX
            'office2': '', # 事業所2
            'zip2': '', # 郵便番号2
            'address2': '', # 住所2
            'building2': '', # 建物2
            'tel2': '', # 電話番号2
            'fax2': '', # FAX2
            'mobile': '', # 携帯電話
            'mobile2': '', # 携帯電話2
            'mail': '', # メールアドレス
            'mail2': '', # メールアドレス2
            'url': '', # URL
            'url2': '', # URL2
            'x': 0, # 固定値
            'y': 0, # 固定値
            'wide': 0, # 固定値
            'height': 0, # 固定値
            'rotate': 0, # 固定値
            'file': filename,  # ファイル名
            'ou': ou # 表裏
        }

        if size['code'] == 'w':
            direction = 'height'
            measure = 'top'
            center = size[direction] / 2
        else:
            direction = 'width'
            measure = 'left'
            center = size[direction] / 2

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
                        # 該当文字列の除去
                        match_string = line['text'].strip(word_match.group(0))
                        data[key] = match_string
                        if key + '_k' in data:
                            if key == 'company':
                                match_string = self.__trim_company_form(match_string)
                            data[key + '_k'] = self.analyze_kana(match_string)
                    elif (key + '2') in data and data[key + '2'] == '':
                        data[key + '2'] = line['text'].strip(word_match.group())

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
        # TODO text=''のものは排除
        name_list = sorted(filter(lambda x: x['text'] != '', lines), key=lambda x: x[direction], reverse=True)[:top]
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
        for line in reversed(name_list):
            if data['company'] == '':
                data['company'] = line['text']
                data['company_k'] = self.analyze_kana(self.__trim_company_form(line['text']))

            # TODO

        return data

    def __find_name(self, name_list, idx):
        name = name_list[idx]['text']
        self.logger.debug(name_list)
        # リストの解析
        fname, fname_k, lname, lname_k = '','', '', ''
        parts = self.analyze_list(name)
        for i, part in enumerate(parts):
            
            if part['pos_type2'] == '人名' and part['pos_type3'] == '姓':
                if fname == '' and fname_k == '':
                    fname = part['surface']
                    fname_k = part['kata']
                    if i == 0 and len(parts) > 1:
                        lname = ''.join(x['surface'] for x in parts[1:])
                        lname_k = ''.join(x['kata'] for x in parts[1:])
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
                if len(f_l_name) >= 2 and len(f_l_name_k) >= 2:
                    fname = f_l_name[0]
                    fname_k = f_l_name_k[0]
                    lname = f_l_name[1]
                    lname_k = f_l_name_k[1]
        
        if fname == '' and fname_k == '' and lname == '' and lname_k == '' and len(name_list) > (idx + 1):
            fname, fname_k, lname, lname_k, idx = self.__find_name(name_list, (idx + 1))

        return fname, fname_k, lname, lname_k, idx

    def __trim_company_form(self, company_name):
        for company_form in JP_COMPANY_FORM_TUPPLE:
           company_name = company_name.strip(company_form)
        return company_name
    
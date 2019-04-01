import sys
import json
import datetime
import pandas as pd
import uuid
from logging import getLogger, StreamHandler, FileHandler, Formatter
from cerberus import Validator
import threading
import requests
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
            tmp_csv = self.__generate_mock_csv()

            # Create http client
            # Header settings
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            # Parameters
            params = {
                'ret': 0,
                'id': corp,
                'impid': imgno,
                'userid': user,
                'cnt': 1,
                'img1': img1
            }
            files = {
                'csv': open(tmp_csv, "r+b").read()
            }

            # リクエストの生成
            #req = urllib.request.Request(RequestURL, params, files=files, headers=headers)
            # リクエストの送信
            res = requests.post(RequestURL, params, files=files, headers=headers)
            # レスポンスの取得
            #r = res.read()
            
            print(res)
        except Exception as e:
            print(e)
            self.logger.exception(e)
        
        self.logger.debug(sys._getframe().f_code.co_name + ' finished')

        return 


    def __generate_mock_csv(self):
        # Generate random uuid
        tmp_csv = str(uuid.uuid4()) + '.csv'
        # Create DataFrame
        df = pd.DataFrame([["","","マーケティング事業部","","佐藤","サトウ","美咲","ミサキ","","","","","03-0000-0000","","","","","","","","","","e-iuailxxx@xxx.co.p","","www.a-one.oo.jpl","",0,0,0,0,0,"w_18523_0_0_190327124016253.jpg",0]])
        df.to_csv(tmp_csv)
        return tmp_csv

    def __generate_csv(self):

        return

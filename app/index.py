#!/usr/bin/env python
#coding:utf-8

import sys
import datetime
from logging import getLogger, StreamHandler, FileHandler, Formatter
from bottle import Bottle, redirect, request, response, run, static_file, debug
from bzcard import Bzcard
from ocr import Ocr
from ma import Ma
from pyfiglet import Figlet
from const import *

#import io
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Bottle()
debug(True)

# Logging API call
@app.hook('before_request')
def logging_api():
    logger = getLogger('API call')
    logger.setLevel(LOG_LEVEL)
    handler = FileHandler(filename='cib_' + datetime.datetime.today().strftime('%Y%m%d') + '.log')
    handler.setLevel(LOG_LEVEL)
    handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(handler_format)
    logger.addHandler(handler)

# Get static file.
@app.get('/static/<filePath:path>')
def static(filePath):
    return static_file(filePath, root='./static')

# Access root dir.
@app.route('/')
def index():
    redirect('/cib')

# Card in bottle.
@app.get('/cib')
def greeting():
    return '<b>Welcome Card in Bottle</b>!'

# Post BzCard API.
@app.post('/CS000/CS001P.aspx')
def bzcard_interface():
    forms = request.forms
    files = request.files

    bzcard = Bzcard()
    msg = bzcard.bottle_in(forms=forms, files=files)

    response.headers['result'] = bzcard.result
    response.headers['errmsg'] = msg

    if bzcard.result == 0:
        return """
        <h1>Just a moment, please!!</h1>
        """
    else:
        return """
        <h1>Sorry, I'm bussy!!</h1>
        """

# POST sample image.
@app.post('/sample/upload')
def sample():
    files = request.files
    print(files)
    files.get('file').save('file.png', overwrite=True)
    ocr = Ocr()
    return ocr.to_hocr(imgPath='file.png', lang='jpn')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/text')
def sample_string():
    ocr = Ocr()
    return ocr.to_string(imgPath='sample.png', lang='jpn')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/hocr')
def sample_hocr():
    ocr = Ocr()
    return ocr.to_hocr(imgPath='sample.png', lang='jpn')

# Get sample image throw boxes.
@app.get('/sample-image/ocr/boxes')
def sample_boxes():
    ocr = Ocr()
    return ocr.to_boxes(imgPath='sample.png', lang='jpn')

# Get sample image throw tsv.
@app.get('/sample-image/ocr/tsv')
def sample_tsv():
    ocr = Ocr()
    return ocr.to_tsv(imgPath='sample.png', lang='jpn')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/pdf')
def sample_pdf():
    ocr = Ocr()
    return ocr.to_pdf(imgPath='sample.png', lang='jpn')

# Get sample image throw OCR.
@app.get('/sample/analyze')
def sample_pdf():
    text = request.query.getunicode("text")

    if text is None:
        text = ''

    ma = Ma()
    return ma.analyze(text=text)

# Enable cors
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

if (len(sys.argv) > 1) and (sys.argv[1] == "debug"):
    import ptvsd
    print("waiting...")
    ptvsd.enable_attach(address=('0.0.0.0', 5678))
    ptvsd.wait_for_attach()

if __name__ == '__main__':
    # this setting is running for development.
    f = Figlet(font='slant')
    msg = f.renderText('Card in Bottle')
    print(msg)
    run(
        app = app, 
        host = '0.0.0.0', 
        port = 80, 
        debug = True)

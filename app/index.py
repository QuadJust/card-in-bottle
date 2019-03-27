import sys
import datetime
import logging
from logging import getLogger, StreamHandler, Formatter
from bottle import Bottle, redirect, request, response, run, static_file
from bzcard import Bzcard
from ocr import Ocr
from ma import Ma
from pyfiglet import Figlet
from const import *

app = Bottle()

# Logging API call
@app.hook('before_request')
def logging_api():
    logger = getLogger('API call')
    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(filename='cib_' + datetime.datetime.today().strftime('%Y%m%d') + '.log')
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
def bzcard():
    forms = request.forms
    files = request.files

    ocr = Bzcard()
    msg = ocr.in_bottle(forms=forms, files=files)

    response.headers['result'] = ocr.result
    response.headers['errmsg'] = msg

    if ocr.result == 0:
        return """
        <h1>Just a moment, please!!</h1>
        """
    else:
        return """
        <h1>Sorry, I'm bussy!!</h1>
        """

# Get sample image.
@app.get('/cib/sample-image')
def sample():
    return static_file('sample.png', root='./static')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/text')
def sample_string():
    ocr = Ocr()
    return ocr.to_string(imgPath='sample.png', lang='eng')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/hocr')
def sample_hocr():
    ocr = Ocr()
    return ocr.to_hocr(imgPath='sample.png', lang='eng')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/pdf')
def sample_pdf():
    ocr = Ocr()
    return ocr.to_pdf(imgPath='sample.png', lang='eng')

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

if __name__ == '__main__':
    # this setting is running for development.
    f = Figlet(font='slant')
    msg = f.renderText('Card in Bottle')
    print(msg)
    run(
        app = app, 
        host = '0.0.0.0', 
        port = 8080, 
        debug = True)

if (len(sys.argv) > 1) and (sys.argv[1] == "debug"):
    import ptvsd
    print("waiting...")
    ptvsd.enable_attach("my_secret", address=('0.0.0.0', 8080))
    ptvsd.wait_for_attach()

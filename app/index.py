from bottle import Bottle, redirect, request, response, run, static_file
from pyfiglet import Figlet
from ocr import Ocr
from logging import getLogger, StreamHandler, Formatter
import threading
import pytesseract

app = Bottle()

# Loggin API call
@app.hook('before_request')
def logging_call():
    logger = getLogger("API call")
    logger.setLevel(logging.DEBUG)
    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(handler_format)
    logger.debug(equest.environ['PATH_INFO'])

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
@app.post('/OCR/CS000.aspx')
def bzcard():
    ip = request.forms.get('ip')
    corp = request.forms.get('corp')
    user = request.forms.get('user')
    RequestURL = request.forms.get('RequestURL')
    lang = request.forms.get('lang')
    langchar = request.forms.get('langchar')
    cnt = request.forms.get('cnt')
    imgno = request.forms.get('imgno')
    cardtype = request.forms.get('cardtype')
    cardou = request.forms.get('cardou')
    pflg = request.forms.get('pflg')
    company = request.forms.get('company')

    img1 = request.files.get('img1', '')
    img2 = request.files.get('img2', '')

    response.headers['result'] = 0
    response.headers['errmsg'] = """
    IP:%s\t
    Pflg:%d\t
    Corp:%s\t
    User:%s\t
    ImgNo:%d\t
    Cnt:%d\t
    Lang:%d\t
    LangChar:%d\t
    cardtype:%d\t
    cardou:%d\t
    ImgQuality:%d\t
    """ % (ip, pflg, corp, user, imgno, cnt, lang, langchar, cardtype, cardou)

    return """
    <h1>Just a moment, please!!</h1>
    """

# Get sample image.
@app.get('/cib/sample-image')
def sample():
    return static_file('sample.png', root='./static')

# Get sample image throw OCR.
@app.get('/sample-image/ocr/string')
def sample_string():
    imgPath = 'sample.png'
    ocr = Ocr()
    return ocr.to_string(imgPath)

# Get sample image throw OCR.
@app.get('/sample-image/ocr/hocr')
def sample_hocr():
    imgPath = 'sample.png'
    ocr = Ocr()
    return ocr.to_hocr(imgPath)

# Get sample image throw OCR.
@app.get('/sample-image/ocr/pdf')
def sample_pdf():
    imgPath = 'sample.png'
    ocr = Ocr()
    return ocr.to_pdf(imgPath)

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

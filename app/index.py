from bottle import Bottle, redirect, run, static_file
#from util.Ocr import Ocr
from ocr import ocr
import pytesseract

app = Bottle()

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
    return '<b>Hello</b>!'

# Post BzCard API.
@app.post('/OCR/CS000.aspx')
def bzcard():

    return '<b>Hello BzCard</b>!'

# Get sample image.
@app.get('/cib/sample-image')
def sample():
    return static_file('sample.png', root='./static')

# Get sample image throw OCR.
@app.get('/cib/sample-image/ocr')
def sampleOcr():
    return ocr()

if __name__ == '__main__':
    # this setting is running for development.
    run(app=app, host='0.0.0.0',port=8080, reloader=True, debug=True)
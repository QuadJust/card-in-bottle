#from util.Ocr import Ocr
import pytesseract

def ocr():
    return pytesseract.image_to_string('sample.png')
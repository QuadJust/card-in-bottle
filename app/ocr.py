import logging
from logging import getLogger, StreamHandler, Formatter
import pytesseract
import MeCab

# OCR class
class Ocr(object):
    def __init__(self) :
        logger = getLogger("API call")
        logger.setLevel(logging.DEBUG)
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(handler_format)
        logger.addHandler(stream_handler)
        logger.debug(request.environ['PATH_INFO'])

    def to_string(self, imgPath):
        return pytesseract.image_to_string(imgPath)

    def to_hocr(self, imgPath):
        return pytesseract.image_to_pdf_or_hocr(imgPath, extension='hocr')

    def to_pdf(self, imgPath):
        return pytesseract.image_to_pdf_or_hocr(imgPath, extension='pdf')

class BzcardOcr(Ocr):


    def generate_csv(self):
        return
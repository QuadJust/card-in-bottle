import sys
import datetime
import logging
from logging import getLogger, StreamHandler, Formatter
import pytesseract
from const import *

# Optical character recognition/Reader class
class Ocr(object):
    # Construct
    def __init__(self):
        # Initialize logger
        logger = getLogger('OCR')
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(filename='cib_' + datetime.datetime.today().strftime('%Y%m%d') + '.log')
        handler.setLevel(LOG_LEVEL)
        handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(handler_format)
        logger.addHandler(handler)
        self.logger = logger

    # Image > String
    def to_string(self, imgPath, lang):
        self.logger.debug(sys._getframe().f_code.co_name + ' start')
        ret = pytesseract.image_to_string(imgPath, lang=lang)
        self.logger.debug(sys._getframe().f_code.co_name + ' end')
        return ret

    # Image > hOCR
    def to_hocr(self, imgPath, lang):
        self.logger.debug(sys._getframe().f_code.co_name + ' start')
        ret = pytesseract.image_to_pdf_or_hocr(imgPath, lang=lang,extension='hocr')
        self.logger.debug(sys._getframe().f_code.co_name + ' end')
        return ret

    # Image > PDF
    def to_pdf(self, imgPath, lang):
        self.logger.debug(sys._getframe().f_code.co_name + ' start')
        ret = pytesseract.image_to_pdf_or_hocr(imgPath, lang=lang, extension='pdf')
        self.logger.debug(sys._getframe().f_code.co_name + ' end')
        return ret

from logging import getLogger, StreamHandler, Formatter
import pytesseract
import MeCab

class Ocr(object):
    def to_string(imgPath):
        return pytesseract.image_to_string(imgPath)

    def to_hocr(imgPath):
        return pytesseract.image_to_pdf_or_hocr(imgPath, extension='hocr')

    def to_pdf(imgPath):
        return pytesseract.image_to_pdf_or_hocr(imgPath, extension='pdf')


class BzcardOcr(Ocr):
    def generate_csv():
        return
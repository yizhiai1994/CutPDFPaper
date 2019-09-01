from urllib.request import urlopen
#from pdfminer.pdfinterp import PDFResourceManager,process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open
import io
import os
import sys
from PyPDF2 import PdfFileReader,PdfFileWriter

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator,TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.pdfdevice import PDFDevice

from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar,LTLine,LTAnno,LTText,LTCurve,LTItem,LTRect,LTTextLineHorizontal

class CutPDF_new(object):
    isAbstract = 0
    isKeywords = 0
    isIntroduction = 0
    isResume= 0
    str_LTChar = ''
    def Main(self,src_add,dsc_add,password=''):
        title_list = []
        file = open(src_add, 'rb')
        parser = PDFParser(file)
        document = PDFDocument(parser)

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        page_num = 0
        stpage = 0
        endpage = 0
        new_pdf_name = ''
        new_pdf_name_num = 0
        for page in PDFPage.get_pages(file):
            self.isAbstract = 0
            self.isIntroduction = 0
            self.isKeywords = 0
            self.isResume = 0
            self.str_LTChar = ''
            interpreter.process_page(page)

            layout = device.get_result()

            self.judge(layout)
            # result = sum([self.isAbstract, self.isIntroduction, self.isKeywords, self.isResume])
            # if result > 1:
            #     title_list.append(page_num)
            if self.isIntroduction == 1 and (self.isAbstract == 1 or self.isResume == 1 or self.isKeywords == 1):
                title_list.append(page_num)
            page_num = page_num + 1
        page_cnt = page_num
        for page_num in title_list:
            endpage = page_num
            new_pdf_name = str(new_pdf_name_num)+'.pdf'
            self.cutPDF(src_add,stpage,endpage,new_pdf_name,dsc_add)
            stpage = page_num
            new_pdf_name_num = new_pdf_name_num + 1
        # the last sub-file
        self.cutPDF(src_add, stpage, page_cnt, new_pdf_name, dsc_add)
        print(title_list)


    def cutPDF(self,pdf_file, stPage, endPage,filename,output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        input_stream = open(pdf_file, 'rb')

        #pdf_page = PDFPage.get_pages(input_stream,stPage)

        pdf_input = PdfFileReader(input_stream)
        pdf_output = PdfFileWriter()

        i = stPage

        while i < endPage:
            page = pdf_input.getPage(i)  # 选取需要页面，需要注意的是第一页的编号是0
            #print(page.getDocumentInfo())
            pdf_output.addPage(page)  # 将选好的页面加入到新的pdf中
            i += 1

        #filename = str(stPage) + filename  # 给新的pdf文件命名，这个可以保证不重复覆盖
        filename = str(stPage+1)+'_'+str(i)+'.pdf'
        outputfilename = output_dir + '/' + filename
        output_stream = open(outputfilename, 'wb')
        pdf_output.write(output_stream)
        output_stream.close()
        input_stream.close()
        return True

    def judge(self,layout):
        for lay in layout:
            if isinstance(lay, LTTextBox) or isinstance(lay, LTTextLine):
                #print(1)
                #print(str)
                isAbstract = self.is_Abstract(lay.get_text())
                isKeywords = self.is_Keywords(lay.get_text())
                isIntroduction = self.is_Introduction(lay.get_text())
                isRésumé = self.is_Résumé(lay.get_text())
                if isAbstract == 1:
                    self.isAbstract = 1
                if isKeywords == 1:
                    self.isKeywords = 1
                if isIntroduction == 1:
                    self.isIntroduction = 1
                if isRésumé == 1:
                    self.isResume = 1
                self.judge(lay)
                self.judgeLTChar(self.str_LTChar)
                #print(lay.get_text())
            elif isinstance(lay, LTFigure):
                # LTFigure 对象是其他LT* objects对象的容器，所以我们通过其子对象来递归
                self.judge(lay)
                self.judgeLTChar(self.str_LTChar)
            elif isinstance(lay, LTChar):
                self.str_LTChar = self.str_LTChar + lay.get_text()
                self.judgeLTChar(self.str_LTChar)
            elif isinstance(lay,LTTextLineHorizontal):
                self.judge(lay)
                self.judgeLTChar(self.str_LTChar)
            # elif isinstance(lay,LTRect):
            #     print(lay.get_pts())
                #self.judge(lay)
            else:
                #print(lay)
                self.judgeLTChar(self.str_LTChar)
    def judgeLTChar(self,str):
        isAbstract = self.is_Abstract(str)
        isKeywords = self.is_Keywords(str)
        isIntroduction = self.is_Introduction(str)
        isRésumé = self.is_Résumé(str)
        if isAbstract == 1:
            self.isAbstract = 1
        if isKeywords == 1:
            self.isKeywords = 1
        if isIntroduction == 1:
            self.isIntroduction = 1
        if isRésumé == 1:
            self.isRésumé = 1
    # 把统一编码转换为二进制流
    def to_bytestring(self, s, enc='utf-8'):
        if s:
            # print s
            if isinstance(s, str):
                return s
            else:
                return s.encode(enc)

    def is_Abstract(self,str):
        if "Abstract" in str:
            return 1

    def is_Keywords(self,str):
        if "Keywords" in str:
            return 1

    def is_Introduction(self,str):
        if "Introduction" in str:
            return 1

    def is_Résumé(self,str):
        if "Résumé" in str:
            return 1
#CutPDF_new().Main('/home/py35/Desktop/CAiSE2015.pdf','/home/py35/Desktop/s2')

if __name__ == '__main__':
    CutPDF_new().Main(sys.argv[1],sys.argv[2])
#CutPDF_new().Main('./src/Part-I.pdf','./dst')
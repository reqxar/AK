import threading
import xml.etree.cElementTree as ET
from multiprocessing import Process
from archivekit import Kit, Document, Requisite
from datetime import datetime
from dataset import *
from runames import get_random_name

# Настройки
docStartDateBegin = '11.06.2021' # Дата начала периода
docStartDateEnd = '11.06.2021' # Дата окончания периода

file_quantity = 3000 # Количество файлов
doc_quantity = 15000 # Количество документов в файле

thread_count = 6

savePath = 'D:/out/'

AK = Requisite()

def main():
    for operation_day in Requisite.get_date_range(docStartDateBegin, docStartDateEnd):
        for i in range(round(file_quantity / thread_count)):
            root = Kit.add_baseline()
            for n in range(doc_quantity):

                AK.random_string('formCode', ['407'])
                AK.random_string('codeABS', ['500'])
                AK.random_string('docName', ['Лицевой счет 407'])
                AK.random_string('depName', ['Центральный Аппарат'])
                AK.add('docStartDate', operation_day)
                AK.add('docEndDate', operation_day)
                AK.add('creationDateTime', operation_day)
                AK.add('employee', get_random_name())
                AK.add('isCorrect', '0')
                AK.firstOrder('accountNumber', account_deb_correspondence, 20, False)
                AK.random_string('depNumber', ['3'])
                AK.add('fileName', '')
                AK.add('vspNumber', '00000')               
                AK.addPrimary()

                archive = Kit.make(AK.attributes, root)

            Document.save(archive, savePath, operation_day)


if __name__ == '__main__':
    processes = []

    for i in range(thread_count):
        new_process = Process(target=main)
        new_process.daemon = True
        processes.append(new_process)
        new_process.start()
    
    for process in processes:
        process.join()

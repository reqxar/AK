import threading
import xml.etree.cElementTree as ET
from multiprocessing import Process
from archivekit import Kit, Document, Requisite
from datetime import datetime
from dataset import *
from runames import get_random_name

# Настройки
docStartDateBegin = '11.10.2021' # Дата начала периода
docStartDateEnd = '11.10.2021' # Дата окончания периода

file_quantity = 20 # Количество файлов
doc_quantity = 100 # Количество документов в файле

thread_count = 6

savePath = 'D:/out/'

AK = Requisite()

def main():
    for operation_day in Requisite.get_date_range(docStartDateBegin, docStartDateEnd):
        for i in range(round(file_quantity / thread_count)):
            root = Kit.add_baseline()
            for n in range(doc_quantity):

                AK.random_string('formCode', ['NDOPKO'])
                AK.random_string('codeABS', ['2000'])
                AK.add('employeeFIO', get_random_name())
                AK.random_string('depNumber', ['02'])
                AK.add('docStartDate', operation_day)
                #AK.add('vspNumber', 'BRC')
                AK.add('sumInWords', 'Некоторая сумма прописью')
                AK.add('docQuantity', '1')
                AK.add('pageQuantity', '1')
                AK.random_number('sum', 5, True)
                AK.random_number('debitSum', 5, True)
                AK.random_number('creditSum', 5, True)
                AK.random_number('docNumber', 11)
                AK.random_number('requestId', 6)
                AK.random_number('requestId', 6)
                AK.firstOrder('accountNumber', account_deb_correspondence, 20, False)
                AK.firstOrder('accountKrNumber', account_kr_correspondence, 20, False)
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

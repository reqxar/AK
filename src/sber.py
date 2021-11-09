import threading
import xml.etree.cElementTree as ET
from multiprocessing import Process
from archivekit import Kit, Document, Requisite
from datetime import datetime
from dataset import *
from runames import get_random_name

# Настройки
docStartDateBegin = '20.09.2021' # Дата начала периода
docStartDateEnd = '20.09.2021' # Дата окончания периода

file_quantity = 100 # Количество файлов
doc_quantity = 100 # Количество документов в файле

thread_count = 6

savePath = 'D:/out/'

AK = Requisite()

def main():
    for operation_day in Requisite.get_date_range(docStartDateBegin, docStartDateEnd):
        for i in range(round(file_quantity / thread_count)):
            root = Kit.add_baseline()
            for n in range(doc_quantity):

                AK.random_string('formCode', ['0401108'])
                AK.random_string('codeABS', ['2200'])
                AK.add('employeeFIO', get_random_name())
                AK.add('controlFIO', get_random_name())
                AK.add('signFIO1', get_random_name())
                AK.add('signFIO2', get_random_name())
                AK.add('signStatus1', 'OK')
                AK.add('signStatus2', 'OK')
                AK.random_string('bankSender', bank_list)
                AK.random_string('bankReceiver', bank_list)
                AK.random_string('operationContent', payment_purpose)
                AK.random_string('depNumber', ['3'])
                AK.random_string('depName', ['Московский Банк Сбербанка Российской Федерации'])
                AK.add('docStartDate', operation_day)
                AK.add('signDate1', operation_day)
                AK.add('signDate2', operation_day)
                AK.add('signResult1', 'Подписано ЭП DataMart')
                AK.add('signResult2', 'Подписано ЭП DataMart')
                AK.add('vspNumber', '00000')
                AK.add('sumInWords', 'Некоторая сумма российских рублей прописью')
                AK.add('docQuantity', '1')
                AK.add('pageQuantity', '1')
                AK.add('storeTerm', '5')
                AK.add('accDebNumberName', 'Наименование счета по дебету')
                AK.add('accKrNumberName', 'Наименование счета по кредиту')
                AK.random_number('sum', 5, True)
                AK.random_number('debitSum', 5, True)
                AK.random_number('creditSum', 5, True)
                AK.random_number('docNumber', 50)
                AK.random_number('docCode', 2)
                AK.random_number('docId', 11)
                AK.random_number('bik1', 9)
                AK.random_number('bik2', 9)
                AK.firstOrder('accountNumber', account_deb_correspondence, 25, False)
                AK.firstOrder('accountKrNumber', account_kr_correspondence, 25, False)
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

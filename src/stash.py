import sys
import logging
from dataset import *
from random import choice
from runames import get_random_name
from pylogbeat import PyLogBeatClient
from multiprocessing import Process, Pool, Value
from logging.handlers import RotatingFileHandler
from archivekit import Kit, Document, Requisite

# Настройки подключения к ELK
elk_host = 'depot-elk.labma.ru'
elk_port = 5044
elk_ssl = False

# Количество параллельных процессов
process_number = 10

docStartDateBegin = '01.01.2020' # Дата начала периода
docStartDateEnd = '31.12.2020' # Дата окончания периода

# Инициализация логирования
logging.basicConfig(format='%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
                    handlers=[RotatingFileHandler(filename = 'akmaker.log', mode = 'a', maxBytes=5*1024*1024, backupCount=5, encoding=None, delay=0)])

akmaker_logger = logging.getLogger('root')
akmaker_logger.setLevel(logging.INFO)

date_range = Requisite.get_date_range(docStartDateBegin, docStartDateEnd)

client = PyLogBeatClient(elk_host, elk_port, ssl_enable=elk_ssl)
AK = Requisite()

def main():
    akmaker_logger.info('Connecting to %s:%s', elk_host, elk_port)
    client.connect()
    
    while True:
        akmaker_logger.debug('Generating document...')
        root = Kit.add_baseline('depot')

        AK.random_string('formCode', form_code_list)
        AK.random_string('codeABS', code_abs)
        AK.add('sender', get_random_name())
        AK.add('receiver', get_random_name())
        AK.random_string('bankSender', bank_list)
        AK.random_string('bankReceiver', bank_list)
        AK.random_string('paymentPurpose', payment_purpose)
        AK.random_string('depNumber', dep_number)
        AK.random_string('docStartDate', date_range)
        AK.add('vspNumber', '00000')
        AK.random_number('sum', 5, True)
        AK.random_number('docNumber', 11)
        AK.random_number('bik1', 9)
        AK.random_number('bik2', 9)
        AK.firstOrder('accountNumber', account_correspondence, 20, False)
        AK.firstOrder('accountKrNumber', account_correspondence, 20, False)
        AK.addPrimary()

        edocument = Kit.makeDepotObject(AK.attributes, root)
        akmaker_logger.debug('Document generation finished.')

        akmaker_logger.debug('Sending document.')

        client.send([edocument])
        
        akmaker_logger.debug('Document sent. Document Number: %s', AK.attributes['docNumber'])
    
    client.close()
    akmaker_logger.info('Connection closed.')

if __name__ == '__main__':
    processes = []

    for i in range(process_number):
        new_process = Process(target=main)
        new_process.daemon = True
        processes.append(new_process)
        new_process.start()
    
    for process in processes:
        process.join()
        akmaker_logger.info('%s', process)

        akmaker_logger.info('Transfer completed.')
        akmaker_logger.info('Master process and its daemons has been terminated.')

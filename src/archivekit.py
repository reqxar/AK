import os
import string
import base64
import logging
import time
import xml.etree.cElementTree as ET
from string import Formatter
from random import choice, uniform, randint, randrange
from datetime import datetime, date, timedelta
from logging.handlers import RotatingFileHandler


class UnseenFormatter(Formatter):
    """ Позволяет форматировать строки, если указано неполное количество
    аргументов для string.format() """
    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            try:
                return kwds[key]
            except KeyError:
                return key
        else:
            return Formatter.get_value(key, args, kwds, kwds)

class Requisite:
    attributes = {}

    def add(self, requisite_name, requisite_value):
        """ Добавляет реквизит "Как есть". """
        self.attributes[requisite_name] = requisite_value
        return self.attributes

    def random_number(self, requisite_name, length, isDouble=False):
        """ Добавляет реквизит, значением которого является
        случайное число установленного размера. """
        range_start = 10**(length-1)
        range_end = (10**length)-1
        if isDouble is True:
            result = str(round(uniform(range_start, range_end), 2))
        else:
            result = str(randint(range_start, range_end))
        self.attributes[requisite_name] = result
        return self.attributes

    def random_string(self, requisite_name, values):
        """ Добавляет реквизит, значением которого является
        случайное строковое значение переданное в аргументах функции. """
        self.attributes[requisite_name] = choice(values)
        
    def randomEscapedString(self, requisite_name, *values):
        """ Добавляет реквизит, значением которого является
        случайное строковое значение переданное в аргументах функции.
        Значение будет преобразовано в безопасное для использование в xml """
        self.attributes[requisite_name] = choice(values).encode('ascii', 'xmlcharrefreplace').decode('utf-8')        

    def firstOrder(self, requisite_name, values, max_length=20, isMulti=False):
        """ Используется для создания аналога счёта по первому порядку
        Напр. когда есть необходимость иметь статичные первые пять знаков 
        номера счёта. """
        self.attributes[requisite_name] = pickLength(max_length, choice(values))

        if isMulti:
            for each in values:
                self.attributes[requisite_name] = self.attributes[requisite_name] + ';' + pickLength(max_length, each)

    def addPrimary(self, requisite_name='document', edType='default', encoding='utf-8'):
        """ Включает в АК первичный файл документа в формате base64. """
        absolutePath = os.path.dirname(os.path.abspath(__file__))
        filePath = absolutePath + '/primary/' + edType + '.txt'
        
        fmt = UnseenFormatter()
        try:
            primaryFile = open(filePath, encoding=encoding)
            data = primaryFile.read()
            data = fmt.format(data, **self.attributes)
        except:
            primaryFile = open(absolutePath + '/primary/default.txt', encoding=encoding)
            data = primaryFile.read()
            data = fmt.format(data, **self.attributes)
                
        encodedBytes = base64.b64encode(data.encode(encoding))
        encodedStr = str(encodedBytes, encoding)
        
        primaryFile.close()

        self.attributes[requisite_name] = encodedStr
    
    @staticmethod
    def get_date_range(startDate, endDate):
        """ Получает список дат в указанном промежутке. """
        startDate = datetime.strptime(startDate, '%d.%m.%Y')
        endDate = datetime.strptime(endDate, '%d.%m.%Y')
        step = timedelta(days=1)

        dateRange = []

        while startDate <= endDate:
            dateRange.append(startDate.strftime('%d.%m.%Y'))
            startDate += step

        return dateRange

class Kit:
    root = ET.Element('akt:archiveKit')
    root.set('xmlns:akt', 'http://ru.sbrf.carch')

    @staticmethod
    def add_baseline(kind='archiveKit'):
        if kind == 'archiveKit':
            root = ET.Element('akt:archiveKit')
            root.set('xmlns:akt', 'http://ru.sbrf.carch')
        elif kind == 'depot':
            root = ET.Element('document', documentFormatName = 'LE', documentFormatVersion = '1.2', documentID = getID())
        return root

    @staticmethod
    def make(requisites, parent=root):
        archiveKitDoc = ET.SubElement(parent, 'archiveKitDoc')

        for key, value in requisites.items():
            if key in ['codeABS', 'creationDateTime', 'depNumber', 'vspNumber', 'formCode', 'document']:
                ET.SubElement(archiveKitDoc, key).text = value
            else:
                appliedAttributs = ET.SubElement(archiveKitDoc, 'appliedAttributs')
                ET.SubElement(appliedAttributs, 'attributeName').text = key
                ET.SubElement(appliedAttributs, 'value').text = value

        return parent
   
    @staticmethod
    def makeDepotObject(requisites, parent=root):
        depotObject = {}

        contents = ET.SubElement(parent, 'contents', contentsID = getID())
        contentsRequisites = ET.SubElement(contents, 'contentsRequisites', contentsRequisitesID = getID())

        for key, value in requisites.items():
            if key == 'formCode':
                ET.SubElement(contentsRequisites, key).text = value
                ET.SubElement(contentsRequisites, 'eDocTypeID').text = value
            elif key == 'document':
                contentsBody = ET.SubElement(contents, 'contentsBody', contentsBodyID = getID(), contentsBodyType = 'simple')

                ET.SubElement(contentsBody, 'contentsBodyName').text = getID('') + '.txt'
                ET.SubElement(contentsBody, 'contentsBodyData', encoding='base64').text = value
                
            else:
                ET.SubElement(contentsRequisites, key).text = value
        
        depotObject['message'] = ET.tostring(parent).decode('UTF-8')
        
        return depotObject

class Document(object):

    @staticmethod
    def save(root, path, operationDay, encoding='UTF-8', fileType='AK'):
        tree = ET.ElementTree(root)
        fileName = fileType + '_' + operationDay.replace('.', '') + '_' + str(datetime.now().time()).replace(':', '') + str(randrange(0, 100))
        filePath = os.path.join(path, operationDay.replace('.', ''), fileName)
        try:
            tree.write(filePath, encoding = encoding, xml_declaration = True)
        except FileNotFoundError:
            os.mkdir(path + operationDay.replace('.', ''))
            tree.write(filePath, encoding = encoding, xml_declaration = True)
        os.rename(filePath, filePath + '.xml')

    @staticmethod
    def saveDepotObject(root, path, operationDay, currentSid, encoding='UTF-8', fileType='AK'):
        fileName = getFileName(currentSid)
        filePath = os.path.join(path, fileName[0], fileName[1])

        tree = ET.tostring(root)
        tree = '<?xml version="1.0" encoding="utf-8" ?>' + tree.decode('utf-8') + '\n'
        
        try:
            depotFile = open(filePath, 'w+')
            depotFile.write(tree)
        except FileNotFoundError:
            os.makedirs(os.path.join(path, fileName[0]))
            depotFile = open(filePath, 'w+')
            depotFile.write(tree)
        depotFile.close()

def pickLength(max_length, value):
    """ Функция для генерации случайного числа определённой длины.
    С возможностью указания статического значения первых цифр"""
    numberLength = max_length - len(value)
    range_start = 10**(numberLength-1)
    range_end = (10**numberLength)-1

    return value + str(randint(range_start, range_end))

def getID(prefix='ACCED'):
    return prefix + ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(32))

def getLead(sid):
    return "{:03d}".format(sid)

def getFileName(sid):
    #if (sid > 1000):
    #    return None
    #else:
    return os.path.split(getLead((sid >> 24) & 0xFF) + '/' + getLead((sid >> 16) & 0xFF) + '/' + getLead((sid >> 8) & 0xFF) + '/' + getLead(sid & 0xFF) + '.0')

def getExecutionTime(func):
    def wrap(*args, **kwargs):
        startTime = time.time()
        ret = func(*args, **kwargs)
        finishTime = time.time()
        executionTime = ((finishTime - startTime) * 1000.0)

        logging.debug('Process %s took %s ms', func.__name__, executionTime)

        return ret
    return wrap
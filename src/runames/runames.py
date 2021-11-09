import random
from os.path import abspath, join, dirname

full_path = lambda filename: abspath(join(dirname(__file__), filename))

DICTIONARIES = {
    'first.male': full_path('dict.name.male.first'),
    'last.male': full_path('dict.name.male.last'),
    'mid.male': full_path('dict.name.male.mid'),
    'first.female': full_path('dict.name.female.first'),
    'last.female': full_path('dict.name.female.last'),
    'mid.female': full_path('dict.name.female.mid')
}

def fetch_line(filename):
    with open(filename, 'r', encoding='utf-8') as dict_file:
        lines = dict_file.read().splitlines()
        dict_file.close()
    return random.choice(lines)
    
def get_firstname(gender):
    return fetch_line(DICTIONARIES['first.%s' % gender])

def get_middlename(gender):
    return fetch_line(DICTIONARIES['mid.%s' % gender])

def get_lastname(gender):
    return fetch_line(DICTIONARIES['last.%s' % gender])

def get_random_name(gender=None):
    if gender is None:
        gender = random.choice(('male', 'female'))
    
    return "{0} {1} {2}".format(get_lastname(gender), get_firstname(gender), get_middlename(gender))
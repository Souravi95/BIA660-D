from __future__ import print_function
import re
import en_core_web_sm


#from pyclausie import ClausIE
from itertools import ifilter


nlp = en_core_web_sm.load()
#cl = ClausIE.get_instance()

re_spaces = re.compile(r'\s+')


class Person(object):
    def __init__(self, name, likes=list(), has=list(), travels=list()):
        """
        :param name: the person's name
        :type name: basestring
        :param likes: (Optional) an initial list of likes
        :type likes: list
        :param dislikes: (Optional) an initial list of likes
        :type dislikes: list
        :param has: (Optional) an initial list of things the person has
        :type has: list
        :param travels: (Optional) an initial list of the person's travels
        :type travels: list
        """
        self.name = name
        self.likes = likes
        self.has = has
        self.travels = travels

    @property
    def like_display(self):
        return self.name + ' likes ' + ' '.join(self.likes)

    def __repr__(self):
        return self.name


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self):
        self.departs_on = None
        self.departs_to = None


def get_data_from_file(file_path='./assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '===')) and line.strip() != '']

    return cleaned_lines


def preprocess_question(question='Who has a dog?'):
    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass

    return re.sub(re_spaces, ' ', ' '.join(q_words))


def has_question_word(string):
    # use to figure if a question is answerable or not
    # note: there are other question words
    for qword in ('who', 'what'):
        if qword in string.lower():
            return True

    return False


def get_tagged_data(sentence):
    doc = nlp(u'{0}'.format(sentence))

    ret_val = list()
    for token in doc:
        if not token.is_punct:
            ret_val.append((token.text, token.pos_))

    return ret_val


def train_bot(tagged_data, pets, people):

    _person = {}
    _pets = {}

    propn = [i for i in ifilter(lambda x: x[-1] == 'PROPN', tagged_data)]

    for index, td in enumerate(tagged_data):

        if td[-1] == 'PROPN' and td[0] not in pets:
            if td[-1] not in _person and td[0] != u'Mr.':
                _person[td[0]] = {'likes': [], 'dislikes': []}
        if td[-1] == 'NOUN' and td[0] in ['dog', 'cat'] and propn[-1][0] not in people:
            _pets[propn[-1][0]] = {'type': td[0], 'owner': propn[0][0]}
        if td[-1] == 'VERB' and td[0] in ['likes', 'like']:
            pass

    return _person, _pets


PEOPLE = dict()
PETS = dict()

for gd in get_data_from_file():
    a, b = train_bot(get_tagged_data(gd), PETS, PEOPLE)
    PEOPLE.update(a)
    PETS.update(b)

for k in PETS:
    PEOPLE.pop(k)

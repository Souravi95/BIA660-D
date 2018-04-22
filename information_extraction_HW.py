from __future__ import print_function
import re
import en_core_web_sm

from pyclausie import ClausIE

nlp = en_core_web_sm.load()
CL_OBJ = ClausIE.get_instance()

re_spaces = re.compile(r'\s+')


class Person(object):
    def __init__(self, name, likes=None, has=None, travels=None):
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
        self.likes = [] if likes is None else likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels

    def __repr__(self):
        return self.name


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self, date, place=None):
        self.date = date
        self.place = place


persons = []
pets = []
trips = []
root = None


def get_data_from_file(file_path='C:\\Users\\soura\\Desktop\\assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '==='))]

    return cleaned_lines


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


def add_person(name):
    person = select_person(name)

    if person is None:
        new_person = Person(name)
        persons.append(new_person)

        return new_person

    return person


def select_pet(name):
    for person in persons:
        if person.name == name:
            return person


def add_pet(type, name=None):
    pet = None

    if name:
        pet = select_pet(name)

    if pet is None:
        pet = Pet(type, name)
        pets.append(pet)

    return pet


def get_persons_pet(person_name):
    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing


def process_relation_triplet(triplet):
    """
    Process a relation triplet found by ClausIE and store the data
    find relations of types:
    (PERSON, likes, PERSON)
    (PERSON, has, PET)
    (PET, has_name, NAME)
    (PERSON, travels, TRIP)
    (TRIP, departs_on, DATE)
    (TRIP, departs_to, PLACE)
    :param triplet: The relation triplet from ClausIE
    :type triplet: tuple
    :return: a triplet in the formats specified above
    :rtype: tuple
    """

    sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object

    doc = nlp(unicode(sentence))
    global root
    for t in doc:
        if t.pos_ == 'VERB' and t.head == t:
            root = t
        # return root
        # elif t.pos_ == 'NOUN'

    # also, if only one sentence
    # root = doc[:].root

    """
    CURRENT ASSUMPTIONS:
    - People's names are unique (i.e. there only exists one person with a certain name).
    - Pet's names are unique
    - The only pets are dogs and cats
    - Only one person can own a specific pet
    - A person can own only one pet
    """

    # Process (PET, has, NAME)
    if 'dog' in triplet.subject or 'cat' in triplet.subject:
        if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
            # below is the original syntax for span
            # obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
            # using chunks to get compound names

            obj_span = nlp(list(doc.noun_chunks)[-1].root.text).char_span(0, len(list(doc.noun_chunks)[-1].root.text))

            # handle single names, but what about compound names? Noun chunks might help.
            if len(obj_span) == 1 and obj_span[0].pos_ == 'PROPN':
                name = triplet.object
                subj_start = sentence.find(triplet.subject)
                subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

                s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']
                assert len(s_people) == 1
                s_person = select_person(s_people[0])

                s_pet_type = 'dog' if 'dog' in triplet.subject or ('dog' in triplet.object) else 'cat'

                pet = add_pet(s_pet_type, name)

                s_person.has.append(pet)

    if root.lemma_ == 'like' and 'does n' not in triplet.predicate:
        if triplet.subject in [e.text for e in doc.ents if
                               (e.label_ == 'PERSON') or (e.label_ == 'ORG')] and triplet.object in [e.text for e in
                                                                                                     doc.ents if
                                                                                                     e.label_ == 'PERSON']:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            s.likes.append(o)

    if root.lemma_ == 'be' and (triplet.object.endswith('friends')) and len(
            [e.text for e in doc.ents if e.label_ == 'PERSON']) > 1:
        fname = [str(e.text) for e in doc.ents if e.label_ == 'PERSON']
        s = add_person(fname[0])
        o = add_person(fname[1])
        s.likes.append(o)
        o.likes.append(s)

    return False


def preprocess_question(question):
    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass

    return re.sub(re_spaces, ' ', ' '.join(q_words))


def answer_question(question=' '):
    while question[-1] != '?':
        question = raw_input("Please enter your question: ")
        question = question.lower()
        if question[-1] != '?':
            print('This is not a question... please try again')

    q_trip = CL_OBJ.extract_triples([preprocess_question(question)])[0]
    doc = nlp(unicode(question))

    # (WHO, has, PET)
    if q_trip.subject == 'who' and q_trip.object == 'dog':
        answer = '{} has a {} named {}.'
        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and pet.type == 'dog':
                print(answer.format(person.name, 'dog', pet.name))

    elif q_trip.subject == 'who' and q_trip.object == 'cat':
        answer = '{} has a {} named {}.'
        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and pet.type == 'cat':
                print(answer.format(person.name, 'cat', pet.name))

    # What's the name of <person>'s <pet_type>? (e.g. What's the name of Mike's dog?)
    elif q_trip.object.endswith('name'):
        answer = '{}\'s {}\'s name is {}.'
        pet_person = q_trip.subject
        pet_type = 'dog' if q_trip.object.lower() != 'cat' else 'cat'

        petname = ''

        for person in persons:
            pet = get_persons_pet(person.name)
            if person.name == pet_person and pet:
                petname = pet.name
                if pet.type == pet_type:
                    print(answer.format(pet_person, pet_type, petname))
                else:
                    print(person.name + ' ' + 'doesn\'t have a' + ' ' + pet_type + '.')

        if petname == '' or None:
            print('Sorry, I do not know.')

    # Does someone like someone else?
    elif (q_trip.predicate == 'like') and (q_trip.subject.startswith('does')):
        answer = '{}, {} {} {}.'
        doc = nlp(unicode(question))
        people = [entity.text for entity in doc.ents if entity.label_ == 'PERSON']
        p1 = str(people[0])
        p2 = str(people[1])
        pp2 = select_person(p2)
        host_person = [str(person.likes) for person in persons if person.name == p1]

        if host_person and pp2:
            if p2 in host_person[0]:
                print(answer.format('Yes', p1, 'likes', p2))
            else:
                print(answer.format('No', p1, 'does not like', p2))

        else:
            print('Sorry, I do not know.')

    elif (q_trip.subject.lower() == 'who') and (q_trip.predicate == 'likes') and [entity.text for entity in doc.ents if
                                                                                  entity.label_ == 'PERSON']:
        answer = '{} {} {}.'
        doc = nlp(unicode(question))
        personnames = [entity.text for entity in doc.ents if entity.label_ == 'PERSON']
        p1 = str(personnames[0])
        personlikep1 = []
        for person in persons:
            personlike = person.likes
            for p in set(personlike):
                if p1 == p.name:
                    personlikep1.append(person.name)
        ref = []

        if personlikep1 != ref:
            for pp in personlikep1:
                print(answer.format(pp, 'likes', p1))
        else:
            print('Sorry, I do not know.')
        
    # Who does <person> like?
    elif (q_trip.object.lower() == 'who') and (q_trip.predicate.endswith('like')):
        answer = '{} {} {}.'
        personnames = [entity.text for entity in doc.ents if entity.label_ == 'PERSON']
        p1 = str(personnames[0])
        p1likes = []
        for person in persons:
            if person.likes and person.name == p1:
                likes = [person.likes for person in persons if person.name == p1][0]
                p1likes = [p.name for p in set(likes)]

        ref = []

        if p1likes != ref:
            for pl in p1likes:
                print(answer.format(p1, 'likes', pl))
        else:
            print('Sorry, I do not know.')
    else:
        print('Sorry, not smart enough')


def process_data_from_input_file(path='C:\\Users\\soura\\Desktop\\assignment_01.data'):
    sentences = get_data_from_file(path)

    triplets = CL_OBJ.extract_triples(sentences)

    for triplet in triplets:
        r = process_relation_triplet(triplet)


def main():
    process_data_from_input_file()
    answer_question()


if __name__ == '__main__':
    main()

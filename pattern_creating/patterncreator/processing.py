#!/usr/bin/python3
# -*- coding: utf8 -*-

from .tools import is_slice

class Bracket_content_processor:
    """
    Returns word data for questions after testing. Each word of bracket content should be tested one by one.

    Example::
        bracket_content_processor = Bracket_content_processor()
        print(bracket_content_processor.try_word('о'))
        bracket_content_processor.reset()
        print(bracket_content_processor.try_word('чем'))

        print(bracket_content_processor.try_word('о'))
        print(bracket_content_processor.try_word('чем'))
        print(bracket_content_processor.try_word('чем'))

        print(bracket_content_processor.try_word('о'))
        print(bracket_content_processor.try_word('ком'))

        # output is:
        # False
        # {'anim': 'inan', 'case': 'ins'}
        # False
        # {'anim': 'inan', 'case': 'prep'}
        # False
        # {'anim': 'inan', 'case': 'ins'}
        # False
        # {'anim': 'anim', 'case': 'prep'}
    """
    def __init__(self):
        self.case_questions = {
            # 'nom' : {'anim' : ['кто'], 'inan' : ['что']},
            'gen' : {'anim' : ['кого'], 'inan' : ['чего']},
            'dat' : {'anim' : ['кому'], 'inan' : ['чему']},
            'acc' : {'anim' : ['кого'], 'inan' : ['что']},
            'ins' : {'anim' : ['кем'], 'inan' : ['чем']},
            'prep' : {'anim' : ['ком'], 'inan' : ['чем', 'чём']}
        }

        self.case_preps = {
            # 'nom' : [''],
            'gen' : ['', 'относительно', 'от', 'с', 'со', 'для', 'среди', 'у', 'против', 'из'],
            'dat' : ['', 'к', 'по'],
            'acc' : ['', 'в', 'на', 'во'],
            'ins' : ['', 'между', 'перед', 'над', 'за', 'с'],
            'prep' : ['о', 'об', 'при', 'на', 'в'],
        }

        self.last_prep = ''

    def prep_to_cases(self, prep):
        cases = set()
        for case in self.case_preps:
            if prep in self.case_preps[case]:
                cases.add(case)

        return cases

    def question_to_cases_anim(self, question):
        cases = []
        for case in self.case_questions:
            for anim in self.case_questions[case]:
                if question in self.case_questions[case][anim]:
                    cases.append({'case' : case, 'anim' : anim})

        return cases

    def try_word(self, word):
        if self.prep_to_cases(word) != set():
            self.last_prep = word
            return False
        else:
            question_cases_anim = self.question_to_cases_anim(word)
            if question_cases_anim != []:
                prep_cases = self.prep_to_cases(self.last_prep)
                self.last_prep = ''
                result_cases = []
                for cases_anim in question_cases_anim:
                    if cases_anim['case'] in prep_cases:
                        result_cases.append(cases_anim)
                if result_cases != []:
                    if len(result_cases) > 1:
                        return {'case': 'acc', 'anim': 'anim'}
                        # word 'кого' without prep
                        # print(result_cases)
                    return result_cases[0]
                else:
                    return False
            else:
                self.last_prep = ''
                return False

    def reset(self):
        self.last_prep = ''

class Pattern_creator:

    def __init__(self, morph, reductive):
        self.morph = morph
        self.reductive = reductive

        self.bracket_content_processor = Bracket_content_processor()

        self.part_of_speech_type_names = ['W', 'N', 'A', 'V', 'Pa',
                                            'Ap', 'Pn', 'Av', 'Cn',
                                            'Pr', 'Pt', 'Int', 'Num', 'NG', 'VG']

        self.pattern_part_of_speech_list = []

        self.pymorphy_types_translator = {
                                             'INFN': 'V',
                                             'NOUN': 'N',
                                             'PREP': 'Pr',
                                             'ADJF': 'A',
                                             'PRTF': 'Pa',
                                             'ADVB': 'Av',
                                             'PRCL': 'Pt',
                                             'NPRO': 'Pn',
                                             'CONJ': 'Cn'
                                         }

        self.pymorphy_cases_translator = {
                                             'nomn': 'nom',
                                             'gent': 'gen',
                                             'datv': 'dat',
                                             'accs': 'acc',
                                             'ablt': 'ins',
                                             'loct': 'prep',
                                             # below are cases that are translated into best matching lspl cases
                                             'voct': 'nom',
                                             'gen2': 'gen',
                                             'acc2': 'acc',
                                             'loc2': 'prep'
                                         }

        self.pattern_number = 0
        self.part_of_speech_types = dict.fromkeys(self.part_of_speech_type_names, 0)

    def set_verb_header(self, verb_header):
        self.verb_header = verb_header

    def get_pattern_name (self):
        self.pattern_number += 1
        return 'P' + self.number_to_letters(self.pattern_number)

    def number_to_letters (self, number):
        letters = ''
        while number > 0:
            last_digit = number % 26
            letters += chr(65+last_digit)
            number //= 26
        return letters

    def new_part_of_speech_number (self, part_of_speech_type):
        self.part_of_speech_types[part_of_speech_type] += 1

        return self.part_of_speech_types[part_of_speech_type]

    def fetch_matching_str(self):
        matching_types = ('A', 'Pa', 'N')
        result_list = []
        for word in self.pattern_part_of_speech_list:
            if word['type_name'] in matching_types:
                result_list.append(word['type_name'] + str(word['number']))

        self.pattern_part_of_speech_list = []

        if len(result_list) > 1:
            return '<{}>'.format('='.join(result_list))
        else:
            return ''

    def reset_pattern_info(self):
        # print(self.pattern_part_of_speech_list)
        # self.pattern_part_of_speech_list = []
        for part_of_speech_type_name in self.part_of_speech_types:
            self.part_of_speech_types[part_of_speech_type_name] = 0

    def special_form_to_pattern(self, phrase_struct):
        self.reset_pattern_info()
        result_strings = []
        verb_seen, leading_part = self.fetch_leading_verb(phrase_struct[0])
        saved_part_of_speech_types = {**self.part_of_speech_types}

        leading_str = self.fragment_to_pattern(leading_part, verb_seen)
        for semicolon_group in phrase_struct:
            dependent_str = self.fragment_to_pattern(semicolon_group)
            matching_str = self.fetch_matching_str()
            result = '{} = {}{}{}'.format(self.get_pattern_name(), leading_str, dependent_str, matching_str)
            result_strings.append(result)

            self.part_of_speech_types = saved_part_of_speech_types

        return '\n'.join(result_strings)

    def fragment_to_pattern(self, fragment_struct, verb_seen = None):
        if verb_seen is not None:
            if verb_seen in self.verb_header['main_verbs']:
                pattern_verbs = self.verb_header['main_verbs'] + self.verb_header['bracket_verbs']
            elif verb_seen in self.verb_header['bracket_verbs']:
                pattern_verbs = [verb_seen]
            else:
                print('unknown', verb_seen)
                pattern_verbs = [verb_seen] + self.verb_header['main_verbs'] + self.verb_header['bracket_verbs']
                # PKE = {V1<сделать>|V1<делать>}<1,1>N1<работа>

            if len(pattern_verbs) > 1:
                verbs_str = '{' + ' | '.join(list(map(lambda x: 'V1<{0}>'.format(x), pattern_verbs))) + '}<1,1>'
            else:
                verbs_str = 'V{0}<{1}>'.format(self.new_part_of_speech_number('V'), pattern_verbs[0])

            return verbs_str

        result_str = ''
        for element in fragment_struct:
            if 'words' in element:
                element_type = 'words'
            elif 'braces' in element:
                element_type = 'braces'
            elif 'square_brackets' in element:
                element_type = 'square_brackets'
            elif 'round_brackets' in element:
                element_type = 'round_brackets'
            else:
                raise Exception('smth impossible')

            if element_type in ('words', 'braces', 'round_brackets'):
                if element_type == 'round_brackets':
                    word_patterns = list(map(lambda by_comma_list: ' '.join(self.process_round_brackets_words(by_comma_list)), element[element_type]))
                elif element_type == 'braces':
                    word_patterns = list(map(lambda by_comma_list: ' '.join(self.process_adjectives(by_comma_list)), element[element_type]))
                else:
                    word_patterns = list(map(lambda by_comma_list: ' '.join(map(self.word_to_pattern, by_comma_list)), element[element_type]))
                if len(word_patterns) > 1:
                    result_str += '{' + ' | '.join(word_patterns) + '}<1,1>'
                else:
                    result_str += word_patterns[0]

            else:
                word_patterns = list(map(lambda by_comma_list: ' '.join(self.process_adjectives(by_comma_list)), element[element_type]))
                result_str += '[' + ' | '.join(word_patterns) + ']'


            # for by_comma_list in element[element_type]:
            #     result_str += ''

            # result_str += str(element[element_type])

        return result_str

    def process_round_brackets_words(self, words):
        # if words == ['с', 'инф']:
        inf_verb = is_slice(['с', 'инф'], words)
        while inf_verb is not None:
            for i in range(2):
                words.pop(inf_verb)
            words.insert(inf_verb, '{inf}')
            inf_verb = is_slice(['с', 'инф'], words)

        self.bracket_content_processor.reset()
        return map(self.round_brackets_word_to_pattern, words)

    def process_adjectives(self, words):
        return map(lambda word: self.word_to_pattern(word, False), words)

    def round_brackets_word_to_pattern(self, word):
        if word == '{inf}':
            return 'VG{0}'.format(self.new_part_of_speech_number('VG'))
        name_group = self.bracket_content_processor.try_word(word)
        if name_group:
            return 'NG{}<c={}, a={}>'.format(self.new_part_of_speech_number('NG'), name_group['case'], name_group['anim'])
        elif word in ('с', 'со', 'к', 'ко', 'в', 'во'):
            if self.reductive:
                result = '{' + '"{form1}"|"{form2}"'.format(form1=word[0], form2=(word[0] + 'о')) + '}<1,1>'
            else:
                result = '{' + 'Pr{number}<{form1}>|Pr{number}<{form2}>'.format(number=self.new_part_of_speech_number('Pr'),
                                                                            form1=word[0],
                                                                            form2=(word[0] + 'о')) + '}<1,1>'
            return result
        else:
            return self.word_to_pattern(word)

    def word_to_pattern(self, word, noun_desirable = True):
        if 'square_brackets' in word:
            need_brackets = True
            word = word['square_brackets']
        else:
            need_brackets = False

        if self.reductive:
            result = '"{}"'.format(word)
        else:
            word_data = self.get_part_of_speech_data(word, noun_desirable)
            word_data['number'] = self.new_part_of_speech_number(word_data['type_name'])
            if 'c' in word_data:
                pattern_str = '{type_name}{number}<{normal_form}, c={c}>'
            else:
                pattern_str = '{type_name}{number}<{normal_form}>'

            self.pattern_part_of_speech_list.append({'type_name': word_data['type_name'], 'number': word_data['number']})

            result = pattern_str.format(**word_data)

        if need_brackets:
            result = '[' + result + ']'
        return result

    def fetch_leading_verb(self, first_semicolon_group):
        if 'words' in first_semicolon_group[0]:
            first_index = 0
            if first_semicolon_group[0]['words'][0][0] == 'не':
                last_index = 1
                verb = first_semicolon_group[0]['words'][0][1]
                first_semicolon_group[0]['words'][0][1] = '{verb}'
                leading_part = [
                    {'words': [[
                        first_semicolon_group[0]['words'][0].pop(0),
                        first_semicolon_group[0]['words'][0].pop(0)
                    ]]}
                ]
                # return verb
            else:
                last_index = 0
                verb = first_semicolon_group[0]['words'][0][0]
                first_semicolon_group[0]['words'][0][0] = '{verb}'
                leading_part = [
                    {'words': [[
                        first_semicolon_group[0]['words'][0].pop(0)
                    ]]}
                ]
            if first_semicolon_group[0]['words'][0] == []:
                first_semicolon_group[0]['words'].pop()
            if first_semicolon_group[0]['words'] == []:
                first_semicolon_group.pop(0)
                # return verb
        elif 'square_brackets' in first_semicolon_group[0]:
            first_index = 1
            last_index = 0
            verb = first_semicolon_group[1]['words'][0][0]
            first_semicolon_group[1]['words'][0][0] = '{verb}'
            leading_part = [
                first_semicolon_group.pop(0),
                {'words': [[
                    first_semicolon_group[0]['words'][0].pop(0)
                ]]}
            ]
            # return verb
        else:
            raise Exception("Failed to get leading verb")

        # verb = first_semicolon_group[first_index]['words'][0][last_index]
        # first_semicolon_group[first_index]['words'][0][last_index] = '{verb}'
        # leading_part = [first_semicolon_group.pop(0)]
        # if first_index == 1:
        #     leading_part += first_semicolon_group.pop(0)
        return (verb, leading_part)

    def get_part_of_speech_data (self, word, noun_desirable):
        if noun_desirable:
            desirable_types = ['N', 'Pr', 'Pt', 'A', 'Pa', 'Av', 'V', 'W']
        else:
            desirable_types = ['Pr', 'Pt', 'A', 'Pa', 'Av', 'N', 'V', 'W']
        desirable_cases = ['acc']
        types_with_cases = ['N', 'Pn', 'A', 'Pa']
        type_coef  = 0.4
        case_coef  = 0.5
        word_coef = 1 - type_coef - case_coef
        def sorting_key(x):
            if x.normal_form == 'основный':
                return 0

            lspl_type = self.get_lspl_type(x.tag.POS)
            word_score = x.score

            type_score = 1
            for d_type in desirable_types:
                if lspl_type == d_type:
                    break
                else:
                    type_score /= 1.2

            # while self.get_lspl_type(x.tag.POS) not in desirable_types:
            #     type_score /= 2
            if lspl_type in types_with_cases:
                lspl_case = self.get_lspl_case(x.tag.case)
                if lspl_case == 'nom':
                    return 0
                    case_score = 0
                else:
                    case_score = 1
                    for d_case in desirable_cases:
                        if lspl_case == d_case:
                            break
                        # elif self.get_lspl_case(x.tag.case) == 'nom':
                        #     case_score = 0
                        #     break
                        else:
                            case_score /= 1.2

                value = word_coef * word_score + type_coef * type_score + case_coef * case_score
            else:
                value = word_coef * word_score + (type_coef + case_coef) * type_score
            # while self.get_lspl_case(x.tag.case) not in desirable_cases:
            #     case_score /= 2

            return value
        # possible_words = self.morph.parse(word)
        # possible_words = list(filter(lambda x: x.score >= 0.1, self.morph.parse(word)))
        # for x in self.morph.parse(word):
        #     print(x)
        possible_words = [x for x in self.morph.parse(word) if x.score >= 0.1]

        sorted_words = sorted(possible_words, key=sorting_key, reverse=True)
        # print(sorted_words)
        # print(possible_words)
        # for sw in sorted_words:
        #     print(sorting_key(sw), sw)

        # if possible_words[0].score - sorted_words[0].score > 0.000001:
        #     max_score_word = possible_words[0].normal_form
        #     max_metric_word = sorted_words[0].normal_form
        #     if max_score_word != max_metric_word:
        #         print(max_score_word, 'and', max_metric_word)

        word_parsed = sorted_words[0]

        types_need_cases = ['N', 'Pn']

        tag = word_parsed.tag

        normal_form = word_parsed.normal_form

        lspl_type = self.get_lspl_type(tag.POS)

        result = {'type_name': lspl_type, 'normal_form': normal_form}

        # if word_parsed.tag.case: -- adding case to any part of speech having it
        if lspl_type in types_need_cases:
            lspl_case = self.get_lspl_case(tag.case)
            result.update({'c': lspl_case})

        return result

    def get_lspl_type(self, pymorphy_type):
        if pymorphy_type in self.pymorphy_types_translator:
            lspl_type = self.pymorphy_types_translator[pymorphy_type]
        else:
            # Part of speech type was not detected.
            # Consider it to be `word`
            # print(pymorphy_type)
            lspl_type = 'W'

        return lspl_type

    def get_lspl_case(self, pymorphy_case):
        if pymorphy_case in self.pymorphy_cases_translator:
            lspl_case = self.pymorphy_cases_translator[pymorphy_case]
        else:
            lspl_case = ''

        return lspl_case

    # def get_desirable_word(self, possible_words, desirable_types, desirable_cases, single_desired = True):
    #     type_coef  = 0.4
    #     case_coef  = 0.3
    #     word_coef = 1 - type_coef - case_coef
    #     sorted_words = sorted(possible_words, key=sorting_key, reverse=True)
    #
    #     def sorting_key(x):
    #         return x.score


    def get_desirable_type_words(self, possible_words, desirable_types):
        # words_with_desirable_types = dict.fromkeys(desirable_types, [])
        words_with_desirable_types = {x: [] for x in desirable_types}

        for possible_word in possible_words:
            lspl_type = self.get_lspl_type(possible_word.tag.POS)
            if lspl_type in desirable_types:
                words_with_desirable_types[lspl_type].append(possible_word)
                # value = words_with_desirable_types[lspl_type].copy()
                # value.append(possible_word)
                # words_with_desirable_types.update({lspl_type: value})

        for desirable_type in desirable_types:
            if words_with_desirable_types[desirable_type] != []:
                return words_with_desirable_types[desirable_type]
        return []

    def get_desirable_case_words(self, possible_words, desirable_cases, single_desired = True):
        prior_number = 'sing' if single_desired else 'plur'
        not_prior_number = 'plur' if single_desired else 'sing'
        words_with_desirable_cases = {x: {'sing' : [], 'plur' : []} for x in desirable_cases}
        # words_with_desirable_cases = {}
        # for key in desirable_cases:
        #     words_with_desirable_cases[key] = {'sing' : [], 'plur' : []}

        for possible_word in possible_words:
            lspl_case = self.get_lspl_case(possible_word.tag.case)
            if lspl_case in desirable_cases:
                if 'sing' in possible_word.tag:
                    words_with_desirable_cases[lspl_case]['sing'].append(possible_word)
                else:
                    words_with_desirable_cases[lspl_case]['plur'].append(possible_word)

        for desirable_case in desirable_cases:
            if words_with_desirable_cases[desirable_case][prior_number] != []:
                return words_with_desirable_cases[desirable_case][prior_number]
            if words_with_desirable_cases[desirable_case][not_prior_number] != []:
                return words_with_desirable_cases[desirable_case][not_prior_number]

        return []

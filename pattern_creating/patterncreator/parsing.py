#!/usr/bin/python3
# -*- coding: utf8 -*-

import re
from functools import reduce

from .constants import alphabet_ru

class Phrase_content_processor:

    def __init__(self):
        word_pattern_str = '[^; ,\(\)\[\]{}\n]+'
        words_comma_separated_pattern_str = '[^\[\]\(\){}\n]+'
        square_brackets_possible_pattern_str = '[^\(\){}\n]+'
        top_level_pattern_str = '\[' +\
         words_comma_separated_pattern_str +\
         '\]|{' + square_brackets_possible_pattern_str +\
         '}|\(' + words_comma_separated_pattern_str + '\)|' +\
          words_comma_separated_pattern_str

        self.top_level_pattern = re.compile(top_level_pattern_str)

    def get_special_form(self, phrase):
        # special_form consists of semicolon_groups
        special_form = []
        semicolon_splitted = re.split('; ', phrase)

        for semicolon_str in semicolon_splitted:
            semicolon_group = []
            top_level_parts = self.top_level_pattern.findall(semicolon_str)
            for fetched_part in top_level_parts:
                if self.is_words(fetched_part):
                    fetched_part_type = 'words'
                    elem = self.split_flat_line(fetched_part)

                elif self.is_square_brackets_string(fetched_part):
                    fetched_part_type = 'square_brackets'
                    elem = self.split_flat_line(fetched_part[1:-1])

                elif self.is_round_brackets_string(fetched_part):
                    fetched_part_type = 'round_brackets'
                    elem = self.split_hyphen_line(fetched_part[1:-1])

                elif self.is_braces_string(fetched_part):
                    fetched_part_type = 'braces'
                    elem = self.split_formatted_line(fetched_part[1:-1])

                else:
                    raise Exception('not recognized part of phrase: ' + fetched_part)

                semicolon_group.append({fetched_part_type: elem})

            special_form.append(semicolon_group)

        return special_form

    def split_flat_line(self, string):
        result = []
        comma_splitted = re.split(', ', string)
        for splitted in comma_splitted:
            if splitted != '':
                comma_splitted_part = []
                for word in re.findall('[' + alphabet_ru + '-]+', splitted):
                    comma_splitted_part.append(word)

                result.append(comma_splitted_part)

        return result

    def split_formatted_line(self, string):
        result = []
        comma_splitted = re.split(', ', string)
        for splitted in comma_splitted:
            comma_splitted_part = []
            for word in re.findall('[\[\]' + alphabet_ru + '-]+|[' + alphabet_ru + '-]+', splitted):
                if self.is_words(word):
                    comma_splitted_part.append(word)
                elif self.is_square_brackets_string(word):
                    comma_splitted_part.append({'square_brackets': word[1:-1]})
                else:
                    raise Exception("bad structure")

            result.append(comma_splitted_part)

        return result

    def split_hyphen_line(self, string):
        def appender(l1, l2):
            result = []
            for x in l1:
                for y in l2:
                    result.append(x + y)

            return result

        hyphen_splitted = re.split(' - ', string)
        result = []
        for comma_group in hyphen_splitted:
            comma_splitted = re.split(', ', comma_group)
            comma_group_res = []
            for splitted in comma_splitted:
                comma_splitted_part = []
                for word in re.findall('[' + alphabet_ru + '-]+', splitted):
                    comma_splitted_part.append(word)

                comma_group_res.append(comma_splitted_part)
            result.append(comma_group_res)

        return reduce(appender, result)

    def split_words(self, string):
        result = []
        for word in re.findall('[' + alphabet_ru + '-]+', string):
            result.append(word)
        return result

    def is_words (self, string):
        return not (string[0] == '[' or string[0] == '(' or string[0] == '{')

    def is_square_brackets_string(self, string):
        return (string[0] == '[' and string[-1] == ']')

    def is_round_brackets_string(self, string):
        return (string[0] == '(' and string[-1] == ')')

    def is_braces_string(self, string):
        return (string[0] == '{' and string[-1] == '}')


class Letter_blocks:
    """
    Iterates file with letter blocks by filename given

    Example::
        for letter_block in Letter_blocks("input.txt"):
            print('block_text for letter', letter_block['block_letter'], ':')
            print(letter_block['block_text'])
    """
    def __init__(self, input_file_name):
        self.input_file = open(input_file_name, 'r')

        first_line = self.input_file.readline()
        while first_line == '\n':
            first_line = self.input_file.readline()

        if first_line != '':
            self.leading_letter = first_line[:-1]

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns a dictionary with keys 'block_letter' and 'block_text'
        for each letter block
        :returns: dictionary

        """

        result_str = ''

        line = self.input_file.readline()
        if line == '':
            self.input_file.close()
            raise StopIteration

        while line != '':
            if len(line) == 2:
                leading_letter = self.leading_letter
                self.leading_letter = line[:-1]
                return {'block_letter' : leading_letter, 'block_text' : result_str}

            result_str += line
            line = self.input_file.readline()

        return {'block_letter' : self.leading_letter, 'block_text' : result_str}

class Verb_blocks:
    """
    Iterates string of verb blocks structure

    Example::
        for verb_block in Verb_blocks("дать (давать)\nдать [глубокий, исчерпывающий, научный] анализ (чего)\n"):
            print('block_text for verb', verb_block['block_verb_forms'], ':')
            for line in verb_block['block_text']:
                print (line)
    """
    def __init__(self, verb_blocks_str):
        self.lines = verb_blocks_str.splitlines()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns a dictionary with keys 'block_verb_forms' and 'block_text'
        for each verb block
        :returns: dictionary

        """

        if self.lines == []:
            raise StopIteration

        result_list = []
        line = self.lines.pop(0)

        self.verb_forms = self.verb_line_to_verb_forms(line)

        line = self.lines.pop(0)
        while line != '' and self.lines != []:
            result_list.append(line)
            line = self.lines.pop(0)

        if line != '':
            result_list.append(line)

        return {'block_verb_forms' : self.verb_forms, 'block_text' : result_list}

    def verb_line_to_verb_forms(self, verb_line):
        pat_verbtitle = '(?P<main_part>[^\(]+){,}( \((?P<bracket_part>.+)\)){0,1}'
        comp_verbtitle = re.compile(pat_verbtitle)
        match = comp_verbtitle.fullmatch(verb_line)

        if match is not None:
            parts = match.groupdict()

            main_verbs = re.split(', ', parts['main_part'])
            if main_verbs == []:
                raise Exception('no main verbs in title: ' + verb_line)

            redirection_parts = re.split(' см. ', parts['main_part'])
            if len(redirection_parts) > 1:
                return {'redirection': True, 'verb': redirection_parts[0], 'redirect_verb': redirection_parts[1]}

            title_verbs = {'main_verbs': main_verbs, 'bracket_verbs':[]}

            if parts['bracket_part'] is not None:
                bracket_part = []
                ignored = [
                    'т. несов. в.',
                    'об. несов. в.',
                    'об. сов. в.',
                    'сов. и несов. в.'
                ]

                for elem in re.split(', ', parts['bracket_part']):
                    if not (elem in ignored):
                        bracket_part.append(elem)

                title_verbs.update({'bracket_verbs': bracket_part})
            return title_verbs
        else:
            raise Exception('unrecognized title: ' + verb_line)

#!/usr/bin/python3
# -*- coding: utf8 -*-

import re

from .constants import alphabet_ru

def output_fix(input_filename, output_filename):
    f = open(input_filename, 'r')
    txt = ''
    for letter in f.read():
        if letter == 'ё':
            txt += 'е'
        else:
            txt += letter

    f.close()

    f = open(output_filename, 'wb')
    f.write(txt.encode('windows-1251'))
    f.close()

def dict_fix(filename):
    """
    Create a fixed version of `filename` file.
    New file name is 'fixed_' + `filename`

    :param filename: name of a file to read. MUST NOT be absolute
    :returns: void

    Example::
        # generates "fixed_input.txt" file
        dict_fix('input.txt')
    """

    input_file = open(filename, 'r')
    output_file = open("fixed_" + filename, 'w')

    result = re.sub(',', ', ', input_file.read())
    result = re.sub(']', '] ', result)
    result = re.sub('  ', ' ', result)

    output_file.write(result)

    input_file.close()
    output_file.close()

class Bracket_words:
    """
    Gets the word from the string those are in brackets and stores them in set
    The set can be printed

    Example::
        bracket_words = Bracket_words()
        for verb_block in Verb_blocks("дать (давать)\nдать [глубокий, исчерпывающий, научный] анализ (чего)\n"):
            print('block_text for verb', verb_block['block_verb_forms'], ':')
            for line in verb_block['block_text']:
                bracket_words.add_from_string(line)
            bracket_words.print_word_set()
    """
    def __init__(self):
        self.word_set = set()

    def add_from_string(self, string_with_brackets):
        for brackets_group in re.findall('\(.+?\)', line):
            # self.word_set.add(brackets_group)
            for word in re.findall('[' + alphabet_ru + '\.-]+', brackets_group):
                self.word_set.add(word)

    def print_word_set(self):
        for word in self.word_set:
            print(word)

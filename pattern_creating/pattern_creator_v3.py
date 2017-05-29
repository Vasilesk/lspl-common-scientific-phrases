#!/usr/bin/python3
# -*- coding: utf8 -*-

import pymorphy2

from patterncreator.parsing import Phrase_content_processor, Letter_blocks, Verb_blocks
from patterncreator.processing import Pattern_creator
from patterncreator.tools import to_file
from patterncreator.correcting import output_fix

if __name__ == "__main__":
    reductive = False
    # reductive = True
    patterns_utf8_filename = 'patterns_v3.txt'
    patterns_win1251_filename = 'patterns_v3.pat'
    dict_filename = 'data/txt_dict.txt'
    print ("Text to lspl patterns")
    morph = pymorphy2.MorphAnalyzer()

    res_file = open(patterns_utf8_filename, 'w')
    # to_file(res_file, 'NG = {A} N, <A=N>')
    to_file(res_file, 'NG = N')
    # to_file(res_file, 'VG = {Av} V')
    to_file(res_file, 'VG = V')

    pattern_creator = Pattern_creator(morph, reductive)
    parser = Phrase_content_processor()
    count = 0
    for letter_block in Letter_blocks(dict_filename):
        for verb_block in Verb_blocks(letter_block['block_text']):
            pattern_creator.set_verb_header(verb_block['block_verb_forms'])
            for line in verb_block['block_text']:
                count += 1
                special_form = parser.get_special_form(line)
                pattern = pattern_creator.special_form_to_pattern(special_form)
                to_file(res_file, pattern)

    res_file.close()
    print(count)
    output_fix(patterns_utf8_filename, patterns_win1251_filename)

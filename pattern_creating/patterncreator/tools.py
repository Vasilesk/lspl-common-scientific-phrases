#!/usr/bin/python3
# -*- coding: utf8 -*-

def to_file(result_file, *data):
    result_file.write(' '.join([str(x) for x in data]) + '\n')

def is_slice(pattern, main_list):
    p_len = len(pattern)
    for i in range(len(main_list) - p_len + 1):
        main_list_slice = main_list[i:i+p_len]
        if main_list_slice == pattern:
            return i

    return None

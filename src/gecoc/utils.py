# -*- coding: utf-8 -*-

import random
import string

LOWER, UPPER, DIGITS, PUNCT = (string.lowercase,
                    string.uppercase,
                    string.digits,
                    '.:;,!?{}[]<>=-_()+')


def generate(size=11, lower=True, upper=True, digits=True,
        punctuation=False):

    chars = ''
    selection = [lower, upper, digits, punctuation]
    strings =(LOWER, UPPER, DIGITS, PUNCT)   

    for opt, v in zip(selection, strings):
        if opt:
            chars += v

    return ''.join([random.choice(chars) for _ in xrange(size)])

def is_sorted(alist):
    '''
    alist is a list of ints
    '''

    first = alist[0]
    i = 1
    while i < len(alist):
        if first != alist[i] - 1:
            return False
        first = alist[i]
        i += 1
    return True

def strength(password):
    '''
    return 0..1
    '''

    strength = -5

    # bad passwords tests (-20 or -15)
    bad_passwords = ('', 'qwerty', 'asdf', 'zxcv', '123', '1234')
    if password in bad_passwords:
        return -20
    ord_pass = [ord(i) for i in password]
    inverted_pass = ord_pass[:]
    inverted_pass.reverse()
    if is_sorted(ord_pass) or is_sorted(inverted_pass):
        return -15

    # len tests (min -10, max 5)
    if len(password) <= 4:
        strength -= 10
    elif len(password) <= 6:
        strength -= 8
    elif len(password) <= 8:
        strength -= 5
    elif len(password) >= 14:
        strength += 5

    # chars tests (max +20)
    for chars_string in LOWER, UPPER, DIGITS, PUNCT:
        for j in chars_string:
            if j in password:
                strength += 5
                break

    return ((strength + 20) / 40.0)


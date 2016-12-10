#!/usr/bin/python
# -*- coding: utf-8 -*-
symbol_map = {
    u' \u0308': u'_"', u'g': u'g', u'\xe6': u'{', u'\xe7': u'C',
    u'\xf0': u'D', u'\xf8': u'2', u'\u0127': u'X\\', u'\u014b': u'N',
    u'\u0153': u'9', u'\u01c0': u'|\\', u'\u01c2': u'=\\', u'\u01c3': u'!\\',
    u'\u0250': u'6', u'\u0251': u'A', u'\u0252': u'Q', u'\u0253': u'b_<',
    u'\u0254': u'O', u'\u0255': u's\\', u'\u0256': u'd`', u'\u0257': u'd_<',
    u'\u0258': u'@\\', u'\u0259': u'@', u'\u025b': u'E', u'\u025c': u'3',
    u'\u025e': u'3\\', u'\u025f': u'j\\', u'\u0260': u'g_<', u'\u0262': u'G\\',
    u'\u0263': u'G', u'\u0264': u'7', u'\u0265': u'H', u'\u0266': u'h\\',
    u'\u0267': u'x\\', u'\u0268': u'1', u'\u026a': u'I', u'\u026c': u'K',
    u'\u026d': u'l`', u'\u026e': u'K\\', u'\u026f': u'M', u'\u0270': u'M\\',
    u'\u0271': u'F', u'\u0272': u'J', u'\u0273': u'n`', u'\u0274': u'N\\',
    u'\u0275': u'8', u'\u0276': u'&', u'\u0278': u'p\\', u'\u0279': u'r\\',
    u'\u027a': u'l\\', u'\u027b': u'r\\`', u'\u027d': u'r`', u'\u027e': u'4',
    u'\u0280': u'R', u'\u0281': u'R', u'\u0282': u's`', u'\u0283': u'S',
    u'\u0284': u'j\\_<', u'\u0288': u't`', u'\u0289': u'}', u'\u028a': u'U',
    u'\u028c': u'V', u'\u028d': u'W', u'\u028f': u'Y', u'\u0290': u's`',
    u'\u0291': u'z\\', u'\u0292': u'Z', u'\u0294': u'?', u'\u0295': u'?\\',
    u'\u0298': u'O\\', u'\u0299': u'B\\', u'\u029b': u'G\\_<',
    u'\u029c': u'H\\', u'\u029d': u'j\\', u'\u029f': u'L\\', u'\u02a1': u'>\\',
    u'\u02a2': u'<\\', u'\u02b0': u'_h', u'\u02b2': u'_j', u'\u02b7': u'_w',
    u'\u02bc': u'_>', u'\u02c6': u'_\\', u'\u02c7': u'_/', u'\u02c8': u'"',
    u'\u02cc': u'%', u'\u02d0': u':', u'\u02d1': u'.', u'\u02e0': u'_G',
    u'\u02e1': u'_l', u'\u02e4': u'_?\\', u'\u0300': u'_L', u'\u0301': u'_H',
    u'\u0302': u'_F', u'\u0303': u'_~', u'\u0304': u'_M', u'\u0306': u'_X',
    u'\u030b': u'_T', u'\u030c': u'_R', u'\u030f': u'_B', u'\u0318': u'_A',
    u'\u0319': u'_q', u'\u031a': u'_}', u'\u031c': u'_c', u'\u031d': u'_r',
    u'\u031e': u'_o', u'\u031f': u'_+', u'\u0320': u'_-', u'\u0324': u'_t',
    u'\u0325': u'_0', u'\u0329': u'=', u'\u032a': u'_d', u'\u032c': u'_v',
    u'\u032f': u'_^', u'\u0330': u'_k', u'\u0334': u'_e', u'\u0339': u'_O',
    u'\u033a': u'_a', u'\u033b': u'_m', u'\u033c': u'_N', u'\u033d': u'_x',
    u'\u03b2': u'B', u'\u03b8': u'T', u'\u03bb': u'L', u'\u03c7': u'X',
    u'\u1dc4': u'_H_T', u'\u1dc5': u'_B_L', u'\u1dc8': u'_R_F', u'\u207f': u'_n'
}


def convert(ipa):
    """
    convert ipa transcription to ascii-friendly sampa
    :param ipa: ipa transcription string
    :return: sampa transcription string

    >>> convert('k\xca\x8ct')
    u'kVt'
    """
    ipa = ipa if isinstance(ipa, unicode) else ipa.decode('utf-8')
    return ''.join([symbol_map.get(char, char) for char in ipa])


def write_sampa_file(ipa_file, sampa_filename):
    """
    expects each line of ipa file to be <word> <ipatransctiption>.
    """
    with open(ipa_file) as f_in, open(sampa_filename, 'w') as f_out:
        for line in f_in:
            word, ipa = line.split(' ', 1)
            sampa = convert(ipa.strip('\n'))
            f_out.write("%s %s\n" % (word.encode('utf-8'),
                                     sampa.encode('utf-8')))

if __name__ == '__main__':
    import doctest
    doctest.testmod()


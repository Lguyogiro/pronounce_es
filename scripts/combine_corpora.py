from BetterDicts import BetterDict, merged


def make_trans_dict(fname):
    trans_dict = BetterDict()
    with open(fname) as f:
        for line in f:
            word, trans = line.strip('\n').split(' ', 1)
            trans_dict[word] = trans
    return trans_dict


def main():
    ipa_dict = make_trans_dict('../corpora/ipa_transcriptions_es.txt')
    sampa_dict = make_trans_dict('../corpora/sampa_transcriptions_es.txt')
    transcriptions = merged(ipa_dict, sampa_dict, lambda a, b: [a, b])
    words = [line.strip('\n') for line in open('../corpora/wordlist_es.txt')]
    with open('master_transcription_file.txt', 'w') as fout:
        for word in words:
            ipa, sampa = transcriptions.get(word, ["", ""])
            row = "%s %s %s\n" % (word, ipa, sampa)
            fout.write(row)

if __name__ == '__main__':
    main()
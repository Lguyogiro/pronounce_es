import re
import requests

# find the ipa trascription ('pronunciation key') on the page
pattern = re.compile('<span onclick=\"pron_key\(1\)\" '
                     'class=\"pron\">([^<]+)</span>')


url = "https://es.thefreedictionary.com"
wordlist = open("wordlist_es.txt", "r")

word_pron_pairs = []
for i, word in enumerate(wordlist):
    if i % 500 == 0:
        print "Processed %s words" % i
        print "%s words with ipa transcription" % len(word_pron_pairs)
    word = word.strip('\n')
    html = requests.get("%s/%s" % (url, word)).text
    pron_match = re.search(pattern, html)
    ipa = pron_match.groups(0)[0] if pron_match else ""
    if ipa:
        word_pron_pairs.append("%s\t%s" % (word, ipa.encode('utf-8')))


with open("pronounce_es.txt", "w") as f:
    f.write('\n'.join([line for line in word_pron_pairs]))


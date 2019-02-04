from nltk import word_tokenize
from nltk import pos_tag
from nltk import WordNetLemmatizer
from common import HyperHypoCouple as HH
import spacy
import gzip
import shutil
import parsed_sentence as ps
nlp = spacy.load('en_core_web_sm')
from spacy.lang.en.stop_words import STOP_WORDS
stopWords = set(STOP_WORDS)
lemma = WordNetLemmatizer()


def get_sentences(corpus_file):
    """
    Returns all the (content) sentences in a processed corpus file
    :param corpus_file: the compressed processed corpus file (.gz)
    :return: the next sentence (yield)
    """
    sent = ps.parsed_sentence()
    # Read all the sentences in the file
    if str(corpus_file).endswith(".gz"):
        f_in = gzip.open(corpus_file, 'r')
    elif str(corpus_file).endswith(".txt"):
        f_in = open(corpus_file, 'r')
    else:
        print "wrong input file."
        yield ""
    # with gzip.open(corpus_file, 'r') as f_in:
    s = []
    isNP = False
    is_root = False
    root = ""
    ri = 0
    np = ""
    np_indexes = []
    for line in f_in:
        line = line.decode('ISO-8859-2')
        # Ignore start and end of doc
        if '<text' in line or '</Text' in line or '<s>' in line:
            continue
        # End of sentence
        elif '</s>' in line:
            yield sent
            sent = ps.parsed_sentence()
        elif '<NP>' in line:
            isNP = True
        elif '</NP>' in line:
            isNP = False
            sent.add_NP(np.strip(), root, ri, min(np_indexes), max(np_indexes))
            np = ""
            np_indexes = []
        elif '<root>' in line:
            is_root = True
        elif '</root>' in line:
            is_root = False
        else:
            try:
                word, lemma, pos, index, parent, parent_index, dep, type = line.split("\t")
                if is_root:
                    root = word
                    ri = int(index)
                if isNP:
                    np_indexes.append(int(index))
                    np = np + " " + word
                sent.add_word(word, lemma, pos, int(index), parent, int(parent_index), dep, type.strip())
            # One of the items is a space - ignore this token
            except Exception, e:
                print str(e)
                continue

def remove_first_occurrences_stopwords(text):
    """
    :param text: text string
    :return: the text after removing the first occurrences of stop words in the text
    """
    if text == "":
        return text
    words = text.split()
    if words[0] in stopWords:
        text = str(" " + text + " ").replace(" " + words[0] + " ", "").strip()
        return remove_first_occurrences_stopwords(text)
    else:
        return text

def noun_phrase_chunker(sentence):
    """
    :param sentence: a sentence string
    :return: a list of sentence noun phrases
    """
    nps = []
    sentParsing = nlp(sentence.decode("ascii", "ignore"))
    for chunk in sentParsing.noun_chunks:
        np = chunk.text.lower().encode("ascii", "ignore")
        np = remove_first_occurrences_stopwords(np)
        nps.append(np)
    return nps

def label_sentence(sentence, couples):
    """
    :param sentence: a sentence string
    :param couples: list of dataset HH-couples
    :return: tuple (occur boolean, annotated sentence), the occur boolean is true if any of the couple occur at the sentence
    """
    nps = noun_phrase_chunker(sentence)
    sentence = " " + sentence.lower()
    for hh in couples:
        hypo = hh.hyponym
        hyper = hh.hypernym
        if hypo.lower() in nps and hyper.lower() in nps:
            hypo2 = hypo.replace(" ", "_")
            sentence2 = str(sentence).replace(" " + hypo + " ", " " + hypo2 + "_hypo ")
            hyper2 = hyper.replace(" ", "_")
            sentence3 = str(sentence2).replace(" " + hyper + " ", " " + hyper2 + "_hyper ")
            return True, sentence3.strip()
    return False, sentence.strip()


def enhanced_label_sentence(sentence, couples, min_gap = 1, max_gap = 7):
    """
    :param sentence: a sentence string
    :param couples: list of dataset HH-couples
    :param min_gap: the minimum gap between the index of occurrence of hypernym and hyponym (default = 1)
    :param max_gap: the maximum gap between the index of occurrence of hypernym and hyponym (default = 7)
    :return: tuple (occur boolean, annotated sentence), the occur boolean is true if any of the couple occur at the sentence
    """
    nps = noun_phrase_chunker(sentence)
    sentence = " " + sentence.lower()
    for hh in couples:
        hypo = hh.hyponym
        hyper = hh.hypernym
        if hypo.lower() in nps and hyper.lower() in nps:
            hypo2 = hypo.replace(" ", "_")
            sentence2 = str(sentence).replace(" " + hypo + " ", " " + hypo2 + "_hypo ")
            hyper2 = hyper.replace(" ", "_")
            sentence3 = str(sentence2).replace(" " + hyper + " ", " " + hyper2 + "_hyper ")
            hypoIndexes = get_indexes(sentence3, hypo2 + "_hypo")
            hyperIndexes = get_indexes(sentence3,  hyper2 + "_hyper")
            for index1 in hypoIndexes:
                for index2 in hyperIndexes:
                    if abs(index2 - index1) > min_gap and abs(index2 - index1) <= max_gap:
                        return True, sentence3.strip()
    return False, sentence.strip()

def get_indexes(sentence, token):
    """
    :param sentence: a string sentence
    :param token: a string token (such as word)
    :return: a list of all indexes where the token occurs in the sentence
    """
    tokens = word_tokenize(sentence)
    indexes = []
    while True:
        try:
            ind = tokens.index(token)
            indexes.append(ind)
            tokens[ind] = "_"
        except:
            break
    return indexes

def get_couples(datasetPath):
    """
    :param datasetPath: dataset file path (dataset format --> hyponym\thypernym\n)
    :return: return a list of dataset HH-couples
    """
    couples = []
    with open(datasetPath, "rb") as f:
        for line in f:
            hypo, hyper = line.split("\t")
            hh = HH.HHCouple(hypo.strip(), hyper.strip())
            couples.append(hh)
    f.close()
    return couples

def compressFile(output_file):
    with open(output_file, 'rb') as f_in, gzip.open(output_file + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)



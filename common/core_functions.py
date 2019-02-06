from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
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


def write_sentence_matching_result_into_file(f, ann_sent, couples, label, predicted, predicted_by):
    f.write("<s>\n")
    f.write(ann_sent + "\n")
    f.write(str(couples) + "\n")
    f.write("Label: " + label + "\n")
    f.write("Predicted: " + str(predicted) + "\n")
    f.write("Predicted by: " + str(predicted_by) + "\n")
    f.write("</s>\n")

def check_extracted_couples(extracted_couples, dataset_path):
    dataset_couples = get_couples(dataset_path)
    for extC in extracted_couples:
        if extC in dataset_couples:
            return True, "dataset"
        if check_wordNet_hypernymy(extC.hyponym, extC.hypernym):
            return True, "wordNet"
        lemma_extC = HH.HHCouple(HeadWithLemma(extC.hyponym), HeadWithLemma(extC.hypernym))
        if lemma_extC in dataset_couples:
            return True, "dataset"
        if check_wordNet_hypernymy(lemma_extC.hyponym, lemma_extC.hypernym):
            return True, "wordNet"
    return False, "None"

def check_wordNet_hypernymy(hypo, hyper):
    hypos = wn.synsets(hypo)
    if len(hypos) == 0:
        return False
    hypo = hypos[0]
    hypers = set([i for i in hypo.closure(lambda s:s.hypernyms())])
    hypers2 = wn.synsets(hyper)
    if len(hypers2) == 0:
        return False
    hyper = hypers2[0]
    if hyper in hypers:
        return True
    else:
        return False


def get_couples_from_string(couples_string): #[(sonatas, works), (symphonies, works)]
    """
    get a string of couples and return them as list of HH couples
    :param couples_string: the string representing a list of couples
    :return: HH couples list
    """
    couples = []
    couples_temp = couples_string.replace("[", "").replace("]", "").split("),")
    for co in couples_temp:
        hypo, hyper = str(co).replace("(", "").replace(")", "").split(",")
        hh = HH.HHCouple(hypo.strip(), hyper.strip)
        couples.append(hh)
    return couples

def get_result_sentences(result_file):
    """
    Returns all the content of a matched corpus file
    :param result_file: the processed corpus file (.gz)
    :return: the next sentence result (yield)
    """
    sent = ps.parsed_sentence()
    # Read all the sentences in the file

    with open(result_file, 'r') as f_in:
        i = 0
        ann_sent = ""
        couples = []
        label = ""
        predicted = ""
        predicted_by = ""
        for line in f_in:
            line = line.decode('ISO-8859-2')
            # Ignore start and end of doc
            if '<s>' in line:
                i += 1
                continue
            # End of sentence
            elif '</s>' in line:
                yield ann_sent, couples, label, predicted, predicted_by
                i = 0
                ann_sent = ""
                couples = []
                label = ""
                predicted = ""
                predicted_by = ""
            else:
                if i == 1:
                    ann_sent = line
                elif i == 2:
                    couples = get_couples_from_string(line)
                elif i == 3:
                    label = line.split(":")[1].strip()
                elif i == 4:
                    predicted = line.split(":")[1].strip()
                elif i == 5:
                    predicted_by = line.split(":")[1].strip()
                i += 1
def get_sentences(corpus_file):
    """
    Returns all the (content) sentences in a processed corpus file
    :param corpus_file: the processed corpus file (may be compressed or not)
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
            s = []
            isNP = False
            is_root = False
            root = ""
            ri = 0
            np = ""
            np_indexes = []
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


def label_sentence(sentence, couples, min_gap = 1, max_gap = 10):
    """
    :param sentence: a sentence string
    :param couples: list of dataset HH-couples
    :param min_gap: the minimum gap between the index of occurrence of hypernym and hyponym (default = 1)
    :param max_gap: the maximum gap between the index of occurrence of hypernym and hyponym (default = 7)
    :return: tuple (occur boolean, annotated sentence), the occur boolean is true if any of the couple occur at the sentence
    """
    nps = noun_phrase_chunker(sentence)
    nps.sort(key=lambda s: len(s), reverse=True)
    sentence1 = " " + sentence
    for np in nps:
        np_ann = str(np).replace(" ", "_") + "_np"
        sentence1 = sentence1.lower().replace(" " + np + " ", " " + np_ann + " ")
    for hh in couples:
        hypo = hh.hyponym
        hyper = hh.hypernym
        if hypo.lower() in nps and hyper.lower() in nps:
            hypo_np = str(hypo).replace(" ", "_") + "_np"
            hypo2 = hypo_np.replace("_np", "_hypo")
            sentence2 = str(sentence1).replace(" " + hypo_np + " ", " " + hypo2 + " ")
            hyper_np = str(hyper).replace(" ", "_") + "_np"
            hyper2 = hyper_np.replace("_np", "_hyper")
            sentence3 = str(sentence2).replace(" " + hyper_np + " ", " " + hyper2 + " ")
            hypoIndexes = get_indexes(sentence3, hypo2)
            hyperIndexes = get_indexes(sentence3,  hyper2)
            for index1 in hypoIndexes:
                for index2 in hyperIndexes:
                    if abs(index2 - index1) > min_gap and abs(index2 - index1) <= max_gap:
                        for np in nps:
                            np_ann = str(np).replace(" ", "_") + "_np"
                            sentence3 = sentence3.replace(" " + np_ann + " ", " " + np + " ")
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

def HeadWithLemma(couple_term):
    if len(str(couple_term).split(" ")) == 1:
        try:
            hyper = lemma.lemmatize(couple_term)
        except:
            print "exception"
        return hyper
    nn = 0
    text = word_tokenize(couple_term)
    tags = pos_tag(text)
    allTags = [tag[1] for tag in tags]
    ConjFlag = False
    if "CC" in allTags:
        ConjFlag = True
    i = 0
    word = ""
    for tag in tags:
        if str(tag[1]).__eq__("IN") or (ConjFlag and str(tag[1]).__eq__(",")) or (ConjFlag and str(tag[1]).__eq__("CC")):
            break
        if str(tag[1]).__contains__("NN"):
            word = tag[0]
            nn += 1
    try:
        word = lemma.lemmatize(word)
    except:
        print "exception"
    if word == "":
        return couple_term
    return word

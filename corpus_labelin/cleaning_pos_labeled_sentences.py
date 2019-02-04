import re
import nltk
import spacy
from Hearst_patterns import HearstPattern
HP = HearstPattern.HearstPatterns()

def main():
    '''
    Goal: remove non semantically positive sentences from positive labeled sentences and select
    inputs:
    -posSentFile: a file paths for the corpus sentences labeled positive by the sentence labeling process
    -semPosSentOutputFile: an output file path of positive labeled sentences
    '''

    #inputs
    posSentFile = r"..\labeled_corpus\Music_Pos2.txt"
    semPosSentOutputFile = r"..\labeled_corpus\Music_Sem_Pos2.txt"

    #open output file
    ofsp = open(semPosSentOutputFile, "wb")

    #process each corpus file
    i = 0
    with open(posSentFile, "rb") as f:
        for line in f:
            annSent = line.decode("ascii", "ignore")
            i += 1
            print i
            if not is_non_sem_pos(annSent):
                ofsp.write(annSent.strip() + "\n")

    ofsp.close()
    f.close()

def is_non_sem_pos(annotatedSentence):
    # check if couples occur between brackets and not in the same brackets
    if btw_brackets(annotatedSentence):
        print "btw brackets"
        return True
    # check if there is conjunction relation between couple terms
    if is_conjunction(annotatedSentence):
        return True
    return False

def is_conjunction(sent):
    res = HP.label_cohyponyms(sent)
    if not res:
        return False
    cohyponymCouples = res[1]
    hypoFlag = False
    hyperFlag = False
    for cop in cohyponymCouples:
        if str(cop.hyponym).__contains__("hypo") or str(cop.hypernym).__contains__("hypo"):
            hypoFlag = True
        if str(cop.hyponym).__contains__("hyper") or str(cop.hypernym).__contains__("hyper"):
            hyperFlag = True
        if (hypoFlag and hyperFlag):
            return True
    return False

def btw_brackets(sent):
    brackets = re.findall(r'\((.*?)\)', sent)
    if len(brackets) == 0:
        return False
    hypoBrackets = []
    hyperBrackets = []
    i = 0
    for bracket in brackets:
        if str(bracket).__contains__("_hypo"):
            hypoBrackets.append(i)
        if str(bracket).__contains__("_hyper"):
            hyperBrackets.append(i)
        i += 1
    if len(hyperBrackets)==0 or len(hypoBrackets)==0:
        return False
    return not any(x in hyperBrackets for x in hypoBrackets)

def remove_HH_annotation(annSent):
    return annSent.replace("_hypo", "").replace("_hyper", "").replace("_", " ")
def get_hypo_hyper(annSent):
    words = str(annSent).strip().split()
    hypo = ""
    hyper = ""
    for word in words:
        if word.__contains__("_hypo"):
            hypo = word.replace("_hypo", "").replace("_", " ")
        elif word.__contains__("_hyper"):
            hyper = word.replace("_hyper", "").replace("_", " ")
    return hypo, hyper

# def is_conjunction(annSent):
#     sent = remove_HH_annotation(annSent)
#     hypo, hyper = get_hypo_hyper(annSent)
#     res = HP.label_cohyponyms(sent)
#     if not res:
#         return False
#     cohyponymCouples = res[1]
#     hypoFlag = False
#     hyperFlag = False
#     for cop in cohyponymCouples:
#         if str(cop.hyponym) == hypo or str(cop.hypernym) == hypo:
#             hypoFlag = True
#         if str(cop.hyponym) == hyper or str(cop.hypernym) == hyper:
#             hyperFlag = True
#         if (hypoFlag and hyperFlag):
#             return True
#     return False

if __name__ == '__main__':
    main()

# The dependency patterns:
#             ("nsubj(hyperHead, hypoHead), cop(hyperHead, was|were|is|are)"),
#             ("case(hypoHead, such), mwe(such, as), nmod:such_as(hyperHead, hypoHead)"),
#             ("case(hypoHead, including), nmod:including(hyperHead, hypoHead)"),
#             ("amod(hyperHead, such), case(hypoHead, as), nmod:as(hyperHead, hypoHead)"),
#             ("cc(hypoHead, and/or), amod(hyperHead, other), conj:and/or(hypoHead, hyperHead)"),
#             ("advmod(hyperHead, especially), dep(hyperHead, hypoHead)")

from common import HyperHypoCouple as HH
import common.core_functions as cf

def get_NP(NPs, index):
    for np in NPs:
        if int(index) in range(int(np.start), int(np.end) + 1):
            return np.text
    return ""

def get_couples(parsed_sentence, hyper_index, hypo_index):
    hyper_np = cf.remove_first_occurrences_stopwords(get_NP(parsed_sentence.NPs, hyper_index))
    hypo_np = cf.remove_first_occurrences_stopwords(get_NP(parsed_sentence.NPs, hypo_index))
    couples = []
    if hyper_np != "" and hypo_np != "" and hypo_np != hyper_np:
        hh = HH.HHCouple(hypo_np, hyper_np)
        couples.append(hh)
    parsed_words = parsed_sentence.words
    for i in range(int(hypo_index) + 1, len(parsed_words)):
        parsed_word = parsed_words[i]
        if str(parsed_word.dep_rel).__contains__("conj") and parsed_word.parent_index == hypo_index:
            new_hypo_index = parsed_word.index
            new_hypo_np = get_NP(parsed_sentence.NPs, new_hypo_index)
            if hyper_np != "" and hypo_np != "" and hypo_np != hyper_np:
                new_hh = HH.HHCouple(new_hypo_np, hyper_np)
                couples.append(new_hh)

    return couples


def such_A_as_B(parsed_sentence):
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i] #("amod(hyperHead, such), case(hypoHead, as), nmod:as(hyperHead, hypoHead)"),
        if str(parsed_word.dep_rel).__contains__("nmod:as"):
            hypo_index = parsed_word.index
            hyper_index = parsed_word.parent_index
            flag1 = False
            flag2 = False
            for j in range(i - 1, max(-1, i-10), -1):
                pre_word = parsed_words[j]
                if str(pre_word.dep_rel).__contains__("case") and pre_word.word == "as" and pre_word.parent_index == hypo_index:
                    flag1 = True
                elif str(pre_word.dep_rel).__contains__("amod") and pre_word.word == "such" and pre_word.parent_index == hyper_index:
                    flag2 = True
                if flag1 and flag2:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []

def A_is_a_B(parsed_sentence):
    vtb = ["is", "are", "was", "were"]
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i] #("nsubj(hyperHead, hypoHead), cop(hyperHead, was|were|is|are)"),
        if str(parsed_word.dep_rel).__contains__("nsubj"):
            hypo_index = parsed_word.index
            hyper_index = parsed_word.parent_index
            for j in range(i + 1, min(len(parsed_words), i + 10)):
                next_word = parsed_words[j]
                if str(next_word.dep_rel).__contains__("cop") and next_word.word in vtb and next_word.parent_index == hyper_index:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []


def A_and_other_B(parsed_sentence):
    conj = ["or", "and"]
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i]  #("cc(hypoHead, and/or), amod(hyperHead, other), conj:and/or(hypoHead, hyperHead)"),
        if str(parsed_word.dep_rel).__contains__("conj"):
            hyper_index = parsed_word.index
            hypo_index = parsed_word.parent_index
            flag1 = False
            flag2 = False
            for j in range(i - 1, max(-1, i - 10), -1):
                pre_word = parsed_words[j]
                if str(pre_word.dep_rel).__contains__("amod") and pre_word.word == "other" and pre_word.parent_index == hyper_index:
                    flag1 = True
                elif str(pre_word.dep_rel).__contains__(
                        "cc") and pre_word.word in conj and pre_word.parent_index == hypo_index:
                    flag2 = True
                if flag1 and flag2:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []


def A_especially_B(parsed_sentence):
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i] #("advmod(hyperHead, especially), dep(hyperHead, hypoHead)")
        if str(parsed_word.dep_rel).__contains__("dep"):
            hypo_index = parsed_word.index
            hyper_index = parsed_word.parent_index
            for j in range(i - 1, max(-1, i - 10), -1):
                pre_word = parsed_words[j]
                if str(pre_word.dep_rel).__contains__("advmod") and pre_word.word == "especially" and pre_word.parent_index == hyper_index:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []

def A_including_B(parsed_sentence):
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i] #("case(hypoHead, including), nmod:including(hyperHead, hypoHead)"),
        if str(parsed_word.dep_rel).__contains__("nmod:including"):
            hypo_index = parsed_word.index
            hyper_index = parsed_word.parent_index
            for j in range(i - 1, max(-1, i - 10), -1):
                pre_word = parsed_words[j]
                if str(pre_word.dep_rel).__contains__("case") and pre_word.word == "including" and pre_word.parent_index == hypo_index:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []

def A_such_as_B(parsed_sentence):
    parsed_words = parsed_sentence.words
    for i in range(len(parsed_words)):
        parsed_word = parsed_words[i]
        if str(parsed_word.dep_rel).__contains__("nmod:such_as"):
            hypo_index = parsed_word.index
            hyper_index = parsed_word.parent_index
            flag1 = False
            flag2 = False
            for j in range(i - 1, max(-1, i-10), -1):
                pre_word = parsed_words[j]
                if str(pre_word.dep_rel).__contains__("mwe") and pre_word.word == "as" and pre_word.parent == "such":
                    flag1 = True
                elif str(pre_word.dep_rel).__contains__("case") and pre_word.word == "such" and pre_word.parent_index == hypo_index:
                    flag2 = True
                if flag1 and flag2:
                    couples = get_couples(parsed_sentence, hyper_index, hypo_index)
                    if len(couples) > 0:
                        return True, couples
    return False, []

def sentence_couples_annotation(sentence, couples):
    for couple in couples:
        hyper = couple.hypernym
        hyper2 = hyper.replace(" ", "_")
        sentence = sentence.replace(" " + hyper + " ", " " + hyper2 + "_hyper ").strip()
        hypo = couple.hyponym
        hypo2 = hypo.replace(" ", "_")
        try:
            sentence = sentence.replace(" " + hypo + " ", " " + hypo2 + "_hypo ").strip()
        except:
            sentence = sentence
    return sentence

def DHP_matching(parsed_sentence, sentence = ""):
    couples = []
    patterns = []
    # NP such as NP
    flag, co = A_such_as_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("NP such as NP")
    # NP including NP
    flag, co = A_including_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("NP including NP")
    # NP is a NP
    flag, co = A_is_a_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("NP is a NP")
    # NP and other NP
    flag, co = A_and_other_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("NP and other NP")
    # NP especially NP
    flag, co = A_especially_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("NP especially NP")
    # such NP as NP
    flag, co = such_A_as_B(parsed_sentence)
    if flag:
        couples.extend(co)
        patterns.append("such NP as NP")
    if len(couples) == 0:
        return False, "", "", ""
    return True, couples, patterns, sentence_couples_annotation(sentence, couples)


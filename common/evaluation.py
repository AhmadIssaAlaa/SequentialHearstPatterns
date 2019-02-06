from os import listdir
from os.path import isfile, join
import core_functions as cf

def evaluate(res_files_directory, sem_pos_labeled_corpus_file):
    """
    Evaluate precision, recall, and F-measure from a set of files corresponding the results of matching patterns
    :param res_files_directory: the directory of result files
    :param sem_pos_labeled_corpus_file: the file path of semantically positive labeled corpus
    :return: the measures: precision, recall, and F-measure
    """
    all_pos = len(open(sem_pos_labeled_corpus_file).readlines())
    TM = 0
    PTM = 0
    FM = 0
    allfiles = [join(res_files_directory, f) for f in listdir(res_files_directory) if isfile(join(res_files_directory, f))]
    for file in allfiles:
        for res in cf.get_result_sentences(file):
            label = res[2]
            predicted =  res[3]
            if predicted == "True":
                TM += 1
                if label == "positive":
                    PTM += 1
            else:
                FM += 1
    FNM = all_pos - PTM
    precision = TM*1.0 / (TM + FM)
    recall = TM * 1.0 / (TM + FNM)
    f_measure = 2.0 * precision * recall / (precision + recall)
    return precision, recall, f_measure

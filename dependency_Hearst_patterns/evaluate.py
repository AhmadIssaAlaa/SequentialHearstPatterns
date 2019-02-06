from os import listdir
from os.path import isfile, join
from common import evaluation as ev

def main():
    """
    Goal: evaluate precision, recall, F-measure of DHP
    inputs:
    -res_files_directory: a directory path for the DHP matching result files
    -sem_pos_labeled_corpus: a file path for the semantically positive labeled sentences (all positive used to evaluate recall)
    """
    res_files_directory = r"..\matching_DHP_subcorpora"
    sem_pos_labeled_corpus = r"..\labeled_corpus\Music_Test_Sem_Pos.txt"

    precision, recall, f_measure = ev.evaluate(res_files_directory, sem_pos_labeled_corpus)
    print "DHP evaluation:"
    print "precision : " + str(precision)
    print "recall : " + str(recall)
    print "F-measure : " + str(f_measure)

if __name__ == '__main__':
    main()

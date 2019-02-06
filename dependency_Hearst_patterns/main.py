from common import core_functions as cf
from DHP import DHP_matching
def main():
    """
    Goal: Match DHP and output the couples extracted (with sentence annotation) by a specific pattern into a corresponding output file
    inputs:
    -sem_pos_file: a file path for the semantically positive sentences (result of cleaning process)
    -sem_pos_processed_file: a file path for the semantically positive sentences after processing (result of java preprocessing step)
    -neg_samples_file: a file path for samples of negative sentences (same number of semantically positive sentences may be selected randomly)
    -sem_pos_processed_file: a file path for samples of negative sentences after processing (result of java preprocessing step)
    -output_files: a list of output files, each one corresponds for a specific DHP
    -dataset_path: the path for the dataset file
    """
    sem_pos_file = r"..\labeled_corpus\Music_Sem_Pos.txt"
    sem_pos_processed_file = r"..\processed_corpus\Music_Sem_Pos_processed.txt"
    neg_samples_file = r"..\labeled_corpus\Music_Neg_samples.txt"
    neg_samples_processed_file = r"..\processed_corpus\Music_Neg_Samples_processed.txt"
    output_files = [r"..\matching_DHP_subcorpora\matching_such_as.txt",
                    r"..\matching_DHP_subcorpora\matching_including.txt",
                    r"..\matching_DHP_subcorpora\matching_is_a.txt",
                    r"..\matching_DHP_subcorpora\matching_and_other.txt",
                    r"..\matching_DHP_subcorpora\matching_especially.txt",
                    r"..\matching_DHP_subcorpora\matching_such_NP_as.txt"]
    dataset_path = r"..\datasets\Music.txt"
    patterns = ["NP such as NP", "NP including NP", "NP is a NP", "NP and other NP", "NP especially NP",
                "such NP as NP"]
    f0 = open(output_files[0], "w")
    f1 = open(output_files[1], "w")
    f2 = open(output_files[2], "w")
    f3 = open(output_files[3], "w")
    f4 = open(output_files[4], "w")
    f5 = open(output_files[5], "w")

    matching_DHP_and_write_into_files(sem_pos_file, sem_pos_processed_file, patterns, f0, f1, f2, f3, f4, f5, "positive", dataset_path)
    matching_DHP_and_write_into_files(neg_samples_file, neg_samples_processed_file, patterns, f0, f1, f2, f3, f4, f5, "negative", dataset_path)
    f0.close()
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()

def matching_DHP_and_write_into_files(file, processed_file, patterns, f0, f1, f2, f3, f4, f5, label, dataset_path):
    sentences = open(file).readlines()
    i = 0
    for parsed_sentence in cf.get_sentences(processed_file):
        sentence = sentences[i]
        print i
        i += 1
        res = DHP_matching(parsed_sentence, sentence)
        if res[0]:
            predicted, predicted_by = cf.check_extracted_couples(res[1], dataset_path)
            if res[2][0] == patterns[0]:
                cf.write_sentence_matching_result_into_file(f0, res[3], res[1], label, predicted, predicted_by)
            elif res[2][0] == patterns[1]:
                cf.write_sentence_matching_result_into_file(f1, res[3], res[1], label, predicted, predicted_by)
            elif res[2][0] == patterns[2]:
                cf.write_sentence_matching_result_into_file(f2, res[3], res[1], label, predicted, predicted_by)
            elif res[2][0] == patterns[3]:
                cf.write_sentence_matching_result_into_file(f3, res[3], res[1], label, predicted, predicted_by)
            elif res[2][0] == patterns[4]:
                cf.write_sentence_matching_result_into_file(f4, res[3], res[1], label, predicted, predicted_by)
            elif res[2][0] == patterns[5]:
                cf.write_sentence_matching_result_into_file(f5, res[3], res[1], label, predicted, predicted_by)



if __name__ == '__main__':
    main()

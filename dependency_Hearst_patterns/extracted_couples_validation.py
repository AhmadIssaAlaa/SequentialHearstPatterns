from os import listdir
from os.path import isfile, join
from common import core_functions as cf

def main():
    """
    Goal: validate the extracted couples using DHP
    inputs:
    -res_files_directory: a directory path for the DHP matching result files
    """
    res_files_directory = r"..\matching_DHP_subcorpora"

    allfiles = [join(res_files_directory, f) for f in listdir(res_files_directory) if
                isfile(join(res_files_directory, f))]
    dataset_path = r"..\datasets\Music.txt"

    for file in allfiles:
        s = ""
        for res in cf.get_result_sentences(file):
            s += "<s>\n"
            s += str(res[0]).strip() + "\n"
            s += str(res[1]) + "\n"
            s += "Label: " + str(res[2]).strip() + "\n"
            predicted, predicted_by = cf.check_extracted_couples(res[1], dataset_path)
            s += "Validated: " + str(predicted).strip() + "\n"
            s += "Validated by: " + str(predicted_by).strip() + "\n"
            s += "</s>\n"
        f = open(file, "w")
        f.write(s)
        f.close()

if __name__ == '__main__':
    main()

from nltk import word_tokenize
from nltk import sent_tokenize
from nltk import WordNetLemmatizer
import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.lang.en.stop_words import STOP_WORDS
stopWords = set(STOP_WORDS)
lemma = WordNetLemmatizer()
from common import core_functions as cf


def main():
    """
    Goal: Take a list of corpus text files and label the sentences as positive and negative according to a dataset
     after filtering the sentences that contains number of tokens above N
    inputs:
    -corpusFilesInput: A list of paths for corpus text files
    -posSentOutputFile: an output file path for positive labeled sentences
    -negSentOutputFile: an output file path for negative labeled sentences
    -datasetFilePath: a dataset file path
    -minTokens: minimum number of tokens in a sentence
    -maxTokens: maximum number of tokens in a sentence
    """
    #inputs
    corpusFilesInput = [r"E:\SemEvalData\SemEval18-Task9\corpuses\2B_music_bioreviews_tokenized_Training.txt",
                    r"E:\SemEvalData\SemEval18-Task9\corpuses\2B_music_bioreviews_tokenized_Testing.txt"]
    posSentOutputFile = r"..\labeled_corpus\Music_Pos2.txt"
    negSentOutputFile = r"..\labeled_corpus\Music_Neg2.txt"
    datasetFilePath = r"..\datasets\Music.txt"
    minTokens = 5
    maxTokens = 50

    #get dataset couples
    couples = cf.get_couples(datasetFilePath)

    #open output files
    ofp = open(posSentOutputFile, "wb")
    ofn = open(negSentOutputFile, "wb")

    #process each corpus file
    for cFile in corpusFilesInput:
        with open(cFile, "rb") as f:
            i = 0
            for line in f:
                line = line.decode("ascii", "ignore")
                i += 1
                print i
                sentences = sent_tokenize(line)
                for sentence in sentences:
                    tokens = word_tokenize(sentence)
                    if len(tokens) < minTokens or len(tokens) > maxTokens:
                        continue
                    else:
                        label, resSent = cf.label_sentence(sentence, couples)
                        if label:
                            ofp.write(resSent.encode("ascii", "ignore").strip()+"\n")
                        else:
                            ofn.write(resSent.encode("ascii", "ignore").strip()+"\n")
    ofp.close()
    ofn.close()
    f.close()

if __name__ == '__main__':
    main()

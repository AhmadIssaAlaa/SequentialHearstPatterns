# SequentialHearstPatterns
A new formalization of Hearst's patterns as dependency patterns (DHP), and a mining method to learn sequential Hearst's patterns (SHP).

# Requirements
We are using python 2.7 (Anaconda framework)

We are using nltk: pip install nltk

We are using spacy: pip install spacy

Take care to change the input of each process (such as paths for input and output files).

# Modules Structure

* M1 corpus labeling (corpus_labeling\sentence_labeling_pos_neg.py): module to label sentences of a corpus into positive and negative sentences.
* M2 corpus cleaning (corpus_labeling\cleaning_pos_labeled_sentences.py: module to remove non-semantically positive sentences.
* M3 DHP matching (dependency_Hearst_patterns\DHP_matching.py): module to match DHP on positive and negative sentences and identify HH couples.
* M4 extracted couples validation (dependency_Hearst_patterns\extracted_couples_validation.py): module to validate the extracted couples using a given dataset, WordNet, and structural method.
* M5 evaluate DHP (dependency_Hearst_patterns\evaluate.py): module to evalaute DHP by measuring precision, recall, and F-measure.



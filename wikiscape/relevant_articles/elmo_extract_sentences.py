import os
import sys
import pickle
import re
import pdb
import scipy
from allennlp.commands.elmo import ElmoEmbedder

task_steps = [["add","onion"],["add","rice"],["add","ham"],["add","kimchi"],["pour","sesame","oil"],["stir","mixture"]]
elmo = ElmoEmbedder()    

def print_list(input_list):
    for sentence in input_list:
        sentence_vec = elmo.embed_sentence(sentence)
        # now, check to see if the sentence has any of the task_step nouns (for every task step)
        # if yes, compare the embedding scores of the noun in the sentence, and in the task step
        # if lower than threshold, surround it with ****
        for task_step in task_steps:
            n_i = len(task_step) - 1
            noun = task_step[n_i] # typically the last word
            if noun in sentence: # FIXME: may be problem with capitalized words
                s_i = sentence.index(noun)
                sentence_vec = elmo.embed_sentence(sentence)
                task_vec = elmo.embed_sentence(task_step)
                distance = scipy.spatial.distance.cosine(task_vec[2][n_i], sentence_vec[2][s_i])
                sentence[s_i] += ">>>>>>>>" + str(distance)[0:5]
        print(sentence)
    pdb.set_trace()

def check_node_for(json_node, unwanted_sections):
    for section_name in unwanted_sections:
        if "children" in json_node \
            and len(json_node["children"]) > 0 \
            and "text" in json_node["children"][0] \
            and json_node["children"][0]["text"] == section_name:
            
            return True

class Error(Exception):
    pass

class ReachedCommunityQA(Error):
    pass

def extract_relevant_sentences(json_node, article_sentences):
    if check_node_for(json_node, ["Community Q&A"]):
        raise ReachedCommunityQA # nothing interesting after community Q&A
    
    unwanted_sections = ["Community Q&A", "Related wikiHows", "References", "Warnings", "Ingredients", "Tips", "Advice", "Caution"]
    if check_node_for(json_node, unwanted_sections):
        return

    elif "children" in json_node:
        for subnode in json_node["children"]:
            extract_relevant_sentences(subnode, article_sentences)

    elif "text" in json_node:
        for sentence in re.findall(r'([A-Z][^\.!?]*[\.!?])', json_node["text"]):
            stripped_sentence = re.sub(r'[.,?!@#$%^&*]','',sentence)
            split_sentence = str.split(stripped_sentence)
            article_sentences.append(split_sentence)
    
    

if __name__ == '__main__':

    for filename in os.listdir("."):
        if filename.endswith("105222.pkl"): #FIXME: remove 105222
            with open(filename, "rb") as handle:
                articles_list = pickle.load(handle)
                sentences_list = []
                for [article, _] in articles_list:
                    article_sentences = []
                    try:
                        extract_relevant_sentences(article, article_sentences)
                    except ReachedCommunityQA:
                        pass
                    
                    print_list(article_sentences)
                    sentences_list.append(article_sentences)

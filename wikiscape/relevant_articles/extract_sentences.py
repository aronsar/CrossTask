import os
import sys
import pickle
import re
import pdb

task_steps = ["add onion","add rice","add ham","add kimchi","pour sesame oil","stir mixture"]
task_steps_regex = "([Aa]dd (?:the )?onion|"\
"[Aa]dd (?:the )?rice|"\
"[Aa]dd (?:the )?ham|"\
"[Aa]dd (?:the )?kimchi|"\
"[Aa]dd (?:the )?(?:sesame )?oil|"\
"stir)"

def check_node_for(json_node, unwanted_sections):
    for section_name in unwanted_sections:
        if "children" in json_node \
            and len(json_node["children"]) > 0 \
            and "text" in json_node["children"][0] \
            and json_node["children"][0]["text"] == section_name:
            
            return True

def print_list(input_list):
    for x in input_list:
        print(re.sub(task_steps_regex, r"****\1****", x))
    pdb.set_trace()

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
            article_sentences.append(sentence)
    
    

if __name__ == '__main__':
    for filename in os.listdir("."):
        if filename.endswith("105222.pkl"):
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

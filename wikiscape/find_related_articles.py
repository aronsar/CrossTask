import pdb
import sys
import os
import json
from rouge import Rouge
import pickle as pkl

ARTICLES_PATH = "./content/"
RELEVANT_ARTICLES = []
RELEVANCE_THRESHOLD = .50

NONE_COUNTER = 0

def extract_related(json_node):
    if "children" in json_node \
        and len(json_node["children"]) > 1 \
        and "text" in json_node["children"][0] \
        and json_node["children"][0]["text"] == "Related wikiHows" \
        and "children" in json_node["children"][1]:
        
        # return list of {"text" : "How to do related thing"}
        return json_node["children"][1]["children"]

    if "children" in json_node:
        for subnode in json_node["children"]:
            return_value = extract_related(subnode)
            if return_value is not None:
                return return_value

    return None

def measure_relatedness(related_articles_1, related_articles_2):
    concat_ra_1 = ""
    concat_ra_2 = ""

    # concatenate all the related article titles together
    for element in related_articles_1:
        concat_ra_1 += element["text"]

    for element in related_articles_2:
        concat_ra_2 += element["text"]

    # remove all "how to" substrings from each list of titles
    concat_ra_1 = concat_ra_1.replace("How to", "")
    concat_ra_2 = concat_ra_2.replace("How to", "")

    # use rouge to obtain similarity metric (f score)
    rouge = Rouge()
    scores = rouge.get_scores(concat_ra_1, concat_ra_2)[0]
    avg_fscore = (scores['rouge-1']['f'] + scores['rouge-2']['f'])/2
    
    return avg_fscore

if __name__ == '__main__':
    input_article = sys.argv[1]
    with open(input_article) as article_handle:
        article_json = json.load(article_handle)
        input_article_related_articles = extract_related(article_json)
    for article_file in os.listdir(ARTICLES_PATH):
        article_path = os.path.join(ARTICLES_PATH, article_file)
        with open(article_path) as article_handle:
            article_json = json.load(article_handle)
            related_articles = extract_related(article_json)
            if related_articles is None:
                NONE_COUNTER+=1
                continue
            
            score = measure_relatedness(related_articles, 
                input_article_related_articles)
            if score > RELEVANCE_THRESHOLD:
                RELEVANT_ARTICLES.append([article_json, score])
    
    basename = os.path.basename(input_article)
    savename = "./relevant_articles/" + basename
    pkl.dump(RELEVANT_ARTICLES, open(savename, "wb"))

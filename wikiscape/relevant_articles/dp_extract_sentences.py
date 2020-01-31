import os
import sys
import pickle
import re
import pdb
import scipy
from allennlp.commands.elmo import ElmoEmbedder
from collections import defaultdict
from copy import deepcopy

TASKS_PRIMARY_PATH = "/data/aronsar/CrossTask/crosstask_release/tasks_primary.txt"
NUM_TASKS = 18 # number of primary tasks
TASK_STEPS = {}
SPLIT_TASK_STEPS = {}
EXTRACTED_ORDERS = defaultdict(list)
elmo = ElmoEmbedder()    

def load_task_steps():
    with open(TASKS_PRIMARY_PATH, "rb") as f:
        # lines 0, 6, 12, 18, ... have the task id
        # lines 4, 10, 16, 22, ... have the task_steps
        all_lines = f.readlines()
        for i in range(NUM_TASKS):
            task_id = all_lines[i*6].decode('UTF-8').rstrip()
            TASK_STEPS[task_id] = all_lines[i*6+4].decode('UTF-8').rstrip().split(",")
            SPLIT_TASK_STEPS[task_id] = [step.split(" ") for step in TASK_STEPS[task_id]]

def find_dp_order(required_order, step_matches):
    # required_order: [["add","onion"],["add","rice"],["add","ham"],..]
    # step_matches: [(["add","onion"], 0.4234, ['A', 'sentence'...]),...]
    dp = {}
    num_col = len(step_matches)
    num_row = len(required_order)
    
    # dynamic programming to find all possible orderings
    # that respect the required_order
    for r in range(-1, num_row):
        for c in range(-1, num_col):
            if r == -1: 
                dp[(r,c)] = [[]]

            elif c == -1:
                dp[(r,c)] = []

            elif required_order[r] != step_matches[c][0]:
                dp[(r,c)] = dp[(r, c-1)]

            else:
                dp[(r,c)] = dp[(r,c-1)] + [deepcopy(ordering) + [deepcopy(step_matches[c])] for ordering in dp[(r-1,c-1)]]
                
    # finding the best ordering
    all_orderings = dp[(num_row-1, num_col-1)]
    best_ordering = []
    lowest_dist_sum = 100 # some big number, should be Inf
    for ordering in all_orderings:
        dist_sum = sum([n for (_,n,_) in ordering])
        if dist_sum < lowest_dist_sum:
            best_ordering = deepcopy(ordering)
            lowest_dist_sum = dist_sum

    return best_ordering

def orderings_considered(task_steps):
    all_orderings = [task_steps]

    # consider any ordering with only one divergence from the canonical order
    for i, step in enumerate(task_steps):
        task_steps_without_step = deepcopy(task_steps)
        task_steps_without_step.remove(step)
        for j in range(len(task_steps)):
            if j != i and j != i-1:
                task_steps_diff_order = deepcopy(task_steps_without_step)
                task_steps_diff_order.insert(j, step)
                all_orderings.append(task_steps_diff_order)

    return all_orderings
        

def save_best_order(task_id, sentence_list):
    step_matches = []
    steps_present = set()

    for sentence in sentence_list:
        sentence_vec = elmo.embed_sentence(sentence)
        # now, check to see if the sentence has any of the task_step nouns (for every task step)
        # if yes, compare the embedding scores of the noun in the sentence, and in the task step

        for (task_step, split_task_step) in zip(TASK_STEPS[task_id], SPLIT_TASK_STEPS[task_id]):
            n_i = len(split_task_step) - 1 # noun index
            noun = split_task_step[n_i] # typically the last word
            if noun in sentence: # FIXME: watch capitalized words
                s_i = sentence.index(noun)
                sentence_vec = elmo.embed_sentence(sentence)
                task_vec = elmo.embed_sentence(split_task_step)
                distance = scipy.spatial.distance.cosine(task_vec[2][n_i], sentence_vec[2][s_i])
                sentence[s_i] += ">>>>>>>>" + str(distance)[0:5]
                step_matches.append((task_step, distance, deepcopy(sentence)))
                steps_present.add(task_step)
        print(sentence)
    
    # iterate through variations on the canonical ordering, find best order
    best_dp_order_sum = 100
    best_dp_order = []
    present_task_steps = [ts for ts in TASK_STEPS[task_id] if ts in steps_present]
    for modified_order_present_task_steps in orderings_considered(present_task_steps):
        dp_order = find_dp_order(modified_order_present_task_steps, step_matches)
        dp_order_sum = sum([n for (_,n,_) in dp_order])
        if len(dp_order) > 0 and dp_order_sum < best_dp_order_sum:
            best_dp_order = deepcopy(dp_order)
            best_dp_order_sum = dp_order_sum
            
    print("Best order: ")
    for i, step in enumerate(best_dp_order):
        sentence = ""
        for word in step[2]:
            sentence += word + " "
        print(str(i) + ") " + step[0] + ": " + sentence) 
    
    EXTRACTED_ORDERS[task_id].append([step[0] for step in best_dp_order])

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
    load_task_steps()
    for filename in os.listdir("."):
        if filename.endswith(".pkl"):
            task_id = os.path.basename(filename)[:-4] # remove .pkl
            with open(filename, "rb") as handle:
                articles_list = pickle.load(handle)
                sentences_list = []
                for [article, _] in articles_list:
                    article_sentences = []
                    try:
                        extract_relevant_sentences(article, article_sentences)
                    except ReachedCommunityQA:
                        pass
                    
                    save_best_order(task_id, article_sentences)
                    sentences_list.append(article_sentences)
    
    pdb.set_trace()
    pickle.dump(EXTRACTED_ORDERS, open('extracted_orders.pkl', 'wb'))

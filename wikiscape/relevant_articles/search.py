import os
import sys
import pickle
import pdb

FOUND_IT = 0

def search(json_node, phrase_to_find):
    if "children" in json_node:
        for subnode in json_node["children"]:
            search(subnode, phrase_to_find)

    elif "text" in json_node:
        if phrase_to_find in json_node["text"]:
            print(json_node["text"])
            print("FOUND IT!!!!")
            FOUND_IT = 1

if __name__ == '__main__':
    phrase_to_find = sys.argv[1]
    for filename in os.listdir("."):
        if filename.endswith(".pkl") and "extracted_orders" not in filename:
            with open(filename, "rb") as handle:
                articles_list = pickle.load(handle)
                for [article, _] in articles_list:
                    search(article, phrase_to_find)

    if FOUND_IT == 0:
        print("Did not find search query in any article")

import json
import sys

MIN_TEXT_LENGTH = 1 # minimum length of paragraph to be included, measured in
                      # number of characters
FORBIDDEN_WORDS = ['ArticleQuestion', 'wikiHow']

def passes_criteria(text):
    if len(text) < MIN_TEXT_LENGTH:
        return False

    if any(word in text for word in FORBIDDEN_WORDS):
        return False

    return True

def print_text(json_node):
    # output text
    if type(json_node) is dict and 'text' in json_node:
        text = json_node['text']
        assert type(text) is str or type(text) is unicode
        if passes_criteria(text):
            print(text)
            
        return
    
    # recursively descend through json tree
    if type(json_node is dict and 'children' in json_node):
        assert type(json_node['children']) is list
        for subnode in json_node['children']:
            print_text(subnode)

if __name__ == '__main__':
    input_file = sys.argv[1]
    with open(input_file) as json_file:
        data = json.load(json_file)
        print_text(data)
        import pdb; pdb.set_trace()

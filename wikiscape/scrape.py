#USAGE: scrape.py worker_num n_workers

import requests
from lxml import html, etree
import numpy as np
import pandas as pd
import nltk
import re
import json
import os
from bs4 import BeautifulSoup
from collections import Counter
import itertools
import codecs
import sys

CONTENT_DIR = '.'

def extract_text(tag):
    text = []
    for content in tag.contents:
        if content.name is None:
            text.append(content.strip())
    text = ' '.join(text)
    return text

def unwrap(soup, tag):
    for c in soup.find_all(tag, recursive=True):
        c.unwrap()
    return soup


def remove_urls(text):
    # remove URLs
    clean_text = re.sub(r'https?:\/\/.*\.\w*', '', text, flags=re.MULTILINE)
    return clean_text


def structurize(current_node, children, leafs):
    content = {}
    if current_node in leafs and leafs[current_node] != '':
        content['text'] = leafs[current_node]
    if current_node in children:
        content['children'] = []
        for c in children[current_node]:
            substruct = structurize(c, children, leafs)
            if substruct != {}:
                content['children'].append(substruct)
    return content


def get_content(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    for s in soup.find_all('script'): # removing scripts
        s.replace_with('')
    for s in soup.find_all('style'): # removing styles
        s.replace_with('')
    unwrap_list = ['a','b','i','p','li','ol','ul']
    for tag in unwrap_list:
        soup = unwrap(soup, tag)

    leaf_names = list(soup.find_all(attrs={'class':classes}, recursive=True))
    leafs = {leaf : remove_urls(extract_text(leaf)).strip() for leaf in leaf_names}
    n_leafs = len(leafs)
    children = {}
    for leaf in leaf_names:
        node = leaf
        while node.parent is not None:
            if node.parent in children:
                if node.parent not in children:
                    children[node.parent] = [node,]
                else:
                    if node not in children[node.parent]:
                        children[node.parent].append(node)
                break
            if node.parent not in children:
                children[node.parent] = [node,]
            else:
                if node not in children[node.parent]:
                    children[node.parent].append(node)
            node = node.parent

    modified = True
    while modified:
        reduced_children = {}
        modified = False
        for p, cs in children.items():
            if len(cs)>1 or p.parent is None or p in leafs:
                if p in reduced_children:
                    for c in cs:
                        if c not in reduced_children[p]:
                            reduced_children[p].append(c)#reduced_children[p].union(cs)
                else:
                    reduced_children[p] = cs
            else:
                modified = True
                if p.parent in reduced_children:
                    for c in cs:
                        if c not in reduced_children[p.parent]:
                            reduced_children[p.parent].append(c)#reduced_children[p.parent].union(cs)
                else:
                    reduced_children[p.parent] = cs
        children = reduced_children

    all_children = []
    for p,c in children.items():
        if c in all_children:
            children[p]
        all_children += c
    root = None
    for p in children.keys():
        if p not in all_children:
            root = p

    if root is None:
        print ('Problem while parsing ' + url)
        return {}
    content = structurize(root, children, leafs)
    
    return content

def get_text(content):
    text = []
    if 'text' in content:
        text.append(content['text'])
    if 'children' in content:
        text += [get_text(child) for child in content['children']]
    return '\n'.join(text)


def to_html(content):
    _html = ''
    if 'text' in content:
        _html += content['text']
    if 'children' in content:
        _html += '<ul>'
        for child in content['children']:
            _html += '<li>'+to_html(child)+'</li>'
        _html += '</ul>'
    return _html


if __name__ == '__main__':
    worker_num = int(sys.argv[1])
    n_workers = int(sys.argv[2])
    path = os.path.join(CONTENT_DIR,"tasks.tsv")
    task_ids = {}
    with codecs.open(os.path.join(CONTENT_DIR,"task_ids"),"r","utf-8") as f:
        for line in f:
            idx,task = line.split('\t')
            task_ids[task.strip()] = idx

    classes = set(['ur_review_text','qa_q_txt','checkbox-text','mwimg-caption-text','mw-headline','ur_author','step','qa_q_txt question','related-title-text','section_text','ur_review_more','qa_answer answer','gallerytext','selflink'])

    howtos = pd.read_csv(path, index_col=0, sep='\t')

    content_dir = os.path.join(CONTENT_DIR,'content')
    html_dir = os.path.join(CONTENT_DIR,'html')
    text_dir = os.path.join(CONTENT_DIR,'text')

    for i, (name, url) in enumerate(zip(howtos['name'], howtos['url'])):
        if i % n_workers == worker_num:
            task_id = task_ids[name]
        
            if task_id+'.json' not in os.listdir(content_dir):
                content = get_content(url)
                _html = to_html(content)
                text = get_text(content)
            
                with open(os.path.join(content_dir, task_id+'.json'), 'w') as f:
                    json.dump(content, f)
                with codecs.open(os.path.join(html_dir, task_id+'.html'), "w", "utf-8") as f:
                    f.write(_html)
                with codecs.open(os.path.join(text_dir, task_id+'.txt'), "w", "utf-8") as f:
                    f.write(text)

    ''' 
    for i,row in enumerate(howtos['url'].iteritems()):
        if i % n_workers == worker_num:
            name = row[0]
            url = row[1]
            task_id = task_ids[name]
        
            if task_id+'.json' not in os.listdir(content_dir):
                content = get_content(url)
                _html = to_html(content)
                text = get_text(content)
            
                with open(os.path.join(content_dir, task_id+'.json'), 'w') as f:
                    json.dump(content, f)
                with codecs.open(os.path.join(html_dir, task_id+'.html'), "w", "utf-8") as f:
                    f.write(_html)
                with codecs.open(os.path.join(text_dir, task_id+'.txt'), "w", "utf-8") as f:
                    f.write(text)

    '''

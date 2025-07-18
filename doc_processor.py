import os
import re
from collections import defaultdict

def read_document(directory, file, delimeter1, delimeter2, strip_new_line = False):

    with open(os.path.join(directory, file),"r") as f:
        lines = f.read().split(delimeter1)

    if strip_new_line == True:

        for i in lines:

            article = i.split(delimeter2)

            title = article[0].strip('\n')
            text = article[1].strip('\n')

            print(title)
            print(text)
    
    else:

        for i in lines:

            article = i.split(delimeter2)

            title = article[0]
            text = article[1]

            print(title)
            print(text)


def read_document_w_categories(directory, file, delims=[], strip_new_line = True, char_to_strip = ""):
    with open(os.path.join(directory, file),"r") as f:
        lines = f.read().split('\n')

    d = defaultdict(list)

    for i in lines:

        regex_pattern = '|'.join(map(re.escape, delims))

        article = re.split(regex_pattern, i)

        split_text = []

        category = article[0].strip('\n')

        for item in article[1:]:
            split_text.append(item.strip(char_to_strip))

        d[category].append(split_text)

    return d
            

#read_document("ISO27k", "Main.txt", "#", "£")

#read_document("ISO27k", "AnnexA.txt", "#", "£", strip_new_line = True)

#annexA = read_document_w_categories("ISO27k", "AnnexA.txt", delims=["£", "@"], strip_new_line = True, char_to_strip="#")
#Guidance = read_document_w_categories("ISO27k", "Guidance.txt", delims=["#"], strip_new_line = True, char_to_strip="@")

#CRA = read_document_w_categories("CRA", "reg-text.txt", delims=["#", "£", "@"], strip_new_line = True)

#print(annexA['Information & Communications Security'][0])
#print(Guidance[annexA['Information & Communications Security'][0][0]][0][0])

#print(test["8.34 Protection of information systems during audit testing."])

#selected_category = test["Cryptography"]


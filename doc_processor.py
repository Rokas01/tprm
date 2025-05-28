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


def read_document_w_categories(directory, file, delimeter1, delimeter2, delimeter3, strip_new_line = True):

    with open(os.path.join(directory, file),"r") as f:
        lines = f.read().split(delimeter1)

    d = defaultdict(list)

    for i in lines:

        delimiters =[delimeter2, delimeter3]
        regex_pattern = '|'.join(map(re.escape, delimiters))

        article = re.split(regex_pattern, i)

        category = article[0].strip('\n')
        title = article[1].strip('\n')
        text = article[2].strip('\n')

        d[category].append([title, text])


    return d
            

#read_document("ISO27k", "Main.txt", "#", "£")

#read_document("ISO27k", "AnnexA.txt", "#", "£", strip_new_line = True)

#test = read_document_w_categories("ISO27k", "AnnexA.txt", "#", "£", "@", strip_new_line = True)

#selected_category = test["Cryptography"]






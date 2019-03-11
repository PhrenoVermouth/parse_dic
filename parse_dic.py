#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 23:10:29 2019

@author: gyang
"""

import os,sys,re,getopt

def usage():
    usage = '''
    Usage: python parse_dict.py <Required> [Options]   
  -i   Input coordinate file.
  -o   Name of output file.
Ex: python parse_dict.py -i raw.txt -o new.txt    
'''
    sys.exit(usage)
    

def word_legality_check(word): 
    word = word.strip().split("\n")
    circle_first = word[0].find("◙")
    if  circle_first == -1:
        spell = str(word[0][6:-1] + word[0][-1])
        if spell.islower() and spell.isalpha():
            return True
        else:
            return False
    else:
        return False


def split_word_prop(raw_word,wordlist_splitted):
    all_prop = []
    for i in range(1,len(wordlist_splitted)):
        prop = raw_word[raw_word.find(wordlist_splitted[i-1]) + len(wordlist_splitted[i-1]) + 2 : raw_word.find(wordlist_splitted[i])]
        all_prop.append(prop)
    return all_prop
        
        
        
def split_multi_prop_words(word):
       word = word.strip()   
       pattern = re.compile(r'◙ verb|◙ noun|◙ adjective|◙ adverb')
       wordlist = pattern.split(word)
       for i in range(len(wordlist)):
           if wordlist[i].find("◙"):
               wordlist[i] = wordlist[i].split("◙")[0]
       return wordlist

#For simplicity, multi-pron words present the first one.    
def parse_name_and_pronunciation(wordlist_splitted):                              
    raw = wordlist_splitted[0].strip()
    name_index1 = raw.find("   ") + 3
    name_index2 = raw.find("\n")
    name = raw[name_index1:name_index2]
    pron_index = [(m.start(0))for m in re.finditer("/", raw)]
    if len(pron_index) < 0:
        return name,""
    else:
        pron = raw[pron_index[0]:pron_index[1]+1]
        return name,pron
 
def remove_hanzi(string):
    hanzi = re.compile(u"[\u4e00-\u9fa5]+")
    filtered_str = hanzi.sub(r'', string)
    return(filtered_str)          
              
def parse_verb(verb_block):
     output = {}
     key = 0
     raw = verb_block.strip()
     possible_redundancy = raw.find("【")
     if possible_redundancy == -1:
         pass
     else:
         raw = raw[:possible_redundancy].strip()
     raw = raw.split("\n")
     vt_vi = re.compile(r'\[with obj.\]|\[no obj.\]')
     defi_index = [i for i,x in enumerate(raw) if len(re.findall(vt_vi,x))==1] ###
     if defi_index == [0]:
         if "[with obj.]" in raw[0]:###no need of "\" anymore 
             prop = "vt"
         elif "[no obj.]" in raw[0]: 
             prop = "vi"            
         for i in range(1,len(raw)):    
             if "»" in raw[i]:
                 defi = remove_hanzi(raw[i-1])
                 defi_latter_index = defi.find("  •")
                 defi = defi[:defi_latter_index]
                 example = raw[i]
                 out = [prop, defi, example]
                 output[key] = out
                 key += 1
             elif len(raw) == 2:
                 defi = remove_hanzi(raw[1])
                 defi_latter_index = defi.find("  •")
                 defi = defi[:defi_latter_index]
                 example = ""     
                 out = [prop, defi, example]
                 output[key] = out
                 key += 1                 
     else:
         for i in defi_index:
             if "[with obj.]" in raw[i]:     ###no need of "\" anymore          
                 defi = remove_hanzi(raw[i])
                 defi_fowrard_index = defi.find("] ") + 1
                 defi_latter_index = defi.find("  •")
                 defi = defi[defi_fowrard_index:defi_latter_index]
                 if i+1 == len(raw):
                     example = ""
                 else:
                     if raw[i+1].strip().startswith("»"):
                         example = raw[i+1].strip()[1:]
                     else:
                         example = ""
                 out = ["vt", defi, example]
                 output[key] = out
                 key += 1
             if "[no obj.]" in raw[i]:             
                 defi = remove_hanzi(raw[i])
                 defi_fowrard_index = defi.find("] ")+ 1
                 defi_latter_index = defi.find("  •")
                 defi = defi[defi_fowrard_index:defi_latter_index]
                 if i+1 == len(raw):
                     example = ""
                 else:
                     if raw[i+1].strip().startswith("»"):
                         example = raw[i+1].strip()[1:]
                     else:
                         example = ""
                 out = ["vi", defi, example]
                 output[key] = out
                 key += 1
     return output

def pass_config():
#    if (len(sys.argv) < 11 or re.match("^-", sys.argv[1]) is None): 
#        sys.exit(usage)
    options,args = getopt.getopt(sys.argv[1:],"hi:o:",["help"])   
    for name,value in options:
        if name in ("-h","--help"):
            usage()
        elif name in ("-i"):
            fi = value
        elif name in ("-o"):
            fo = value
    print(fi + " pass_complete!")
    return fi,fo


def main():
    fi,fo = pass_config()
    with open(fi,'r') as fi:
        windows = fi.read().split("————————————")
        windows = windows[1:len(windows)]       
        for i in windows:
            if word_legality_check(i):
                splitted_word = split_multi_prop_words(i)
                splitted_word_prop = split_word_prop(i,splitted_word)
                name,pron = parse_name_and_pronunciation(splitted_word)
                if "verb" in splitted_word_prop:
                    verb_index = splitted_word_prop.index("verb") + 1 #Simplify: only one verb
                    content = parse_verb(splitted_word[verb_index])
                    with open(fo,'a') as foa:
                        foa.write(name + "\t" + pron + "\n")
                        for i in content:
                            foa.write("\t" + content[i][0] + "\t" + content[i][1] + "\t" + content[i][2] + "\n")
                        foa.write("----" + "\n")

if __name__ == "__main__":
    main()                       
            
        
        


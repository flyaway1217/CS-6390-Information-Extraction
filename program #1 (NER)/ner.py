import sys
import re 
LABEL = {'O':'0', 'B-PER':'1', 'I-PER':'2', 'B-LOC':'3', 'I-LOC':'4', 'B-ORG':'5', 'I-ORG':'6'}
ID = {}
WORD = set()
POS = set()
with open(sys.argv[1], 'r') as f:
    for line in f:
        if line.strip() != '':
            l = re.split(r'\s+', line.strip())
            WORD.add(l[-1])
            POS.add(l[-2])

WORD.add('PHI')
WORD.add('OMEGA')
POS.add('PHIPOS')
POS.add('OMEGAPOS')
word_list = sorted(list(WORD))
pos_list = sorted(list(POS))

ID_NUM = 0
for word in word_list:
    ID_NUM += 1
    ID['CURR---'+word+'---word'] = ID_NUM
    ID['PREV---'+word+'---word'] = ID_NUM+1
    ID['NEXT---'+word+'---word'] = ID_NUM+2
    ID_NUM += 2

for pos in pos_list:
    ID_NUM += 1
    ID['PREV---'+pos+'---pos'] = ID_NUM
    ID['NEXT---'+pos+'---pos'] = ID_NUM+1
    ID_NUM += 1

ID_NUM += 10
ID['CURR---UNKWORD'] = ID_NUM+1
ID['PREV---UNKWORD'] = ID_NUM+2
ID['NEXT---UNKWORD'] = ID_NUM+3
ID['PREV---UNKPOS'] = ID_NUM+4
ID['NEXT---UNKPOS'] = ID_NUM+5
ID['CAPI'] = ID_NUM+6

def build_feature(line, prev_line, next_line, mode):
    label, pos, word = re.split('\s+', line.strip())
    prev_label, prev_pos, prev_word = re.split(r'\s+', prev_line.strip())
    next_label, next_pos, next_word = re.split(r'\s+', next_line.strip())
    fl = []
    # word
    if word in word_list:
        fl.append(ID['CURR---'+word+'---word'])
    else:
        fl.append(ID['CURR---UNKWORD'])
    if mode == 'word':
        return LABEL[label]+' '+ ' '.join(str(x)+':1' for x in sorted(list(set(fl))))+'\n'
    # wordcap
    if word[0].isupper():
        fl.append(ID['CAPI'])
    if mode == 'wordcap':
        return LABEL[label]+' '+ ' '.join(str(x)+':1' for x in sorted(list(set(fl))))+'\n'
    # poscon
    if mode == 'poscon':
        if prev_pos in pos_list:
            fl.append(ID['PREV---'+prev_pos+'---pos'])
        else:
            fl.append(ID['PREV---UNKPOS'])
        if next_pos in pos_list:
            fl.append(ID['NEXT---'+next_pos+'---pos'])
        else:
            fl.append(ID['NEXT---UNKPOS'])
        return LABEL[label]+' '+ ' '.join(str(x)+':1' for x in sorted(list(set(fl))))+'\n'
    # lexcon
    if mode == 'lexcon':
        if prev_word in word_list:
            fl.append(ID['PREV---'+prev_word+'---word'])
        else:
            fl.append(ID['PREV---UNKWORD'])
        if next_word in word_list:
            fl.append(ID['NEXT---'+next_word+'---word'])
        else:
            fl.append(ID['NEXT---UNKWORD'])
        return LABEL[label]+' '+ ' '.join(str(x)+':1' for x in sorted(list(set(fl))))+'\n'
    # bothcon
    if  mode == 'bothcon':
        if prev_word in word_list:
            fl.append(ID['PREV---'+prev_word+'---word'])
        else:
            fl.append(ID['PREV---UNKWORD'])
        if next_word in word_list:
            fl.append(ID['NEXT---'+next_word+'---word'])
        else:
            fl.append(ID['NEXT---UNKWORD'])
        if prev_pos in pos_list:
            fl.append(ID['PREV---'+prev_pos+'---pos'])
        else:
            fl.append(ID['PREV---UNKPOS'])
        if next_pos in pos_list:
            fl.append(ID['NEXT---'+next_pos+'---pos'])
        else:
            fl.append(ID['NEXT---UNKPOS'])
        return LABEL[label]+' '+ ' '.join(str(x)+':1' for x in sorted(list(set(fl))))+'\n'

with open (sys.argv[1]+'.'+sys.argv[3], 'w') as g:
    with open(sys.argv[1], 'r') as f:
        for sentence in re.split(r'\n{2,}', f.read(),flags=re.DOTALL):
            if sentence.strip() != '':
                fs = ['X PHIPOS PHI']+re.split(r'\n+', sentence.strip(),flags=re.DOTALL)+['X OMEGAPOS OMEGA']
                len_fs = len(fs)
                for index in range(1,len_fs-1):
                    g.write(build_feature(fs[index],fs[index-1],fs[index+1],sys.argv[3]))

with open (sys.argv[2]+'.'+sys.argv[3], 'w') as g:
    with open(sys.argv[2], 'r') as f:
        for sentence in re.split(r'\n{2,}', f.read(),flags=re.DOTALL):
            if sentence.strip() != '':
                fs = ['X PHIPOS PHI']+re.split(r'\n+', sentence.strip(),flags=re.DOTALL)+['X OMEGAPOS OMEGA']
                len_fs = len(fs)
                for index in range(1,len_fs-1):
                    g.write(build_feature(fs[index],fs[index-1],fs[index+1],sys.argv[3]))
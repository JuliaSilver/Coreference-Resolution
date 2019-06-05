from os.path import join
from os import listdir
from os.path import splitext
import pandas as pd
import re
import string


TEXT_PATH = 'Texts'
CHAINS_PATH = 'Chains'
MORPH_PATH = 'morph'
rows_list = []
rows_list2 = []
SEMAN_PATH = 'For Sem Feat'
def count_lemmas_intersection(lemmas_set_1, lemmas_set_2):
    counter = 0
    anteclongerthree = 0
    anaphlongerthree = 0
    for elem1 in lemmas_set_1:
        for elem2 in lemmas_set_2:
            if elem1 == elem2:
                counter += 1
    len_1 = len(lemmas_set_1)
    len_2 = len(lemmas_set_2)
    if (len_1 > 3):
        anteclongerthree = 1
    if (len_2 > 3):
        anaphlongerthree = 1

    return counter, anteclongerthree, anaphlongerthree

def get_lemmas_set(mention, start, features_list):
    char_num_before = 0
    l = []
    splited_mention = mention.split()
    lemmas_set = []
    for men in splited_mention:
        punt_number_in_front = 0
        punt_number_beh = 0
        for i in men:
            #print(i)
            if i in '!"#$%&\'()*+,./:;<=>?@[\]^_`{|}~ «»':
                punt_number_in_front += 1
            else:
                break
        reversed_men = men[::-1]
        for i in reversed_men:
            if i in '!"#$%&\'()*+,./:;<=>?@[\]^_`{|}~ «»':
                punt_number_beh += 1
            else:
                break
        cur_men = re.sub("[^а-яёА-Я-1234567890a-zA-Z]+", '', men)
        cur_start = start + punt_number_in_front + char_num_before
        #print(punt_number_in_front)
        char_num_before += len(men) + 1
        #print(char_num_before, men, cur_start)
        #cur_men = re.sub("[^а-яА-Я-]+",'', men)
        #print(cur_men)
        inner_l = []
        inner_l.append(cur_men)
        inner_l.append(cur_start)
        l.append(inner_l)
        #print(l, 'не лемма')
        for elem in features_list:
            # print(elem)
            if 0 <= 5 < len(elem):
                if elem[1] == str(cur_start) and elem[2] == str(len(cur_men)):
                    lemma = elem[4]
                    if lemma == 'её':
                        lemma = 'она'
                    lemmas_set.append(lemma)
            else:
                continue




    return lemmas_set


def chech_punctuation(mention):
    punt_number = 0
    punt_number_in_front = 0
    for i in mention:
        if i in '!"#$%&\'()*,./:;<=>?@[\]^_`{|}~ «»':
            punt_number_in_front += 1
        else:
            break
    splited_mention = mention.split()
    for i in splited_mention:
        if i not in '!"#$%&\'()*,./:;<=>?@[\]^_`{|}~ «»':
            cur_men = i
            break

    return punt_number_in_front, cur_men

def get_lemma_morph_features(features_list, start, length, mention, filename):
    lemma = ''
    alterable_morph = []
    unalterable_morph = []
    num_char_bef_dash = 0
    for elem in features_list:
        #print(elem)
        if 0 <= 5 < len(elem):
            if elem[1] == str(start) and elem[2] == str(length):
                lemma = elem[4]
                unalterable = elem[5]
                unalterable_morph = unalterable.split(',')
                alterable = elem[6]
                alterable_morph = alterable.split(',')
        else:
            continue
    if not unalterable_morph:
        for i in mention:
            if i != '-':
                num_char_bef_dash += 1
            else:
                break
        for elem in features_list:
            # print(elem)
            if 0 <= 5 < len(elem):
                if elem[1] == str(start) and elem[2] == str(num_char_bef_dash):
                    lemma = elem[4]
                    unalterable = elem[5]
                    unalterable_morph = unalterable.split(',')
                    alterable = elem[6]
                    alterable_morph = alterable.split(',')

    if not unalterable_morph:
        print('unalterable_morph is empty, perhaps the length or start is wrong')
        print(mention, start, length, filename)
    if not alterable_morph:
        print('alterable_morph is empty, perhaps the length or start is wrong')
        print(mention, start, length, filename)
    return lemma, unalterable_morph, alterable_morph

def prepare_morph_features(mention_1, mention_2, start_1, start_2, len_1, len_2, chains_filename):
    with open(join(MORPH_PATH, chains_filename), encoding='utf8') as f:
        content = f.readlines()
        content_list = [x.split() for x in content]
        #print(mention_1, mention_2)
        num_punc_in_front_men_1, cur_mention_1 = chech_punctuation(mention_1)
        num_punc_in_front_men_2, cur_mention_2 = chech_punctuation(mention_2)
        replaced_1 = re.sub("[^а-яёА-Я-1234567890a-zA-Z ]+", '', cur_mention_1)
        replaced_2 = re.sub("[^а-яёА-Я-1234567890a-zA-Z ]+", '', cur_mention_2)
        lemmas_set_mention_1 = get_lemmas_set(mention_1, start_1, content_list)
        lemmas_set_mention_2 = get_lemmas_set(mention_2, start_2, content_list)
        #print(lemmas_set_mention_1, mention_1, start_1)
        #print(lemmas_set_mention_2, mention_2, start_2)
        #cur_mention_1 = replaced_1.split()
        #cur_mention_2 = replaced_2.split()
        lemma_mention_1, unalterable_morph_1, alterable_morph_1 = get_lemma_morph_features(
                content_list, start_1 + num_punc_in_front_men_1, len(replaced_1), replaced_1, chains_filename)
            #print(lemma_mention_1, unalterable_morph_1, alterable_morph_1)


        lemma_mention_2, unalterable_morph_2, alterable_morph_2 = get_lemma_morph_features(
                content_list, start_2 + num_punc_in_front_men_2, len(replaced_2), replaced_2, chains_filename)
            #print(lemma_mention_2, unalterable_morph_2, alterable_morph_2)

    return lemma_mention_1, lemma_mention_2, unalterable_morph_1, unalterable_morph_2, alterable_morph_1, alterable_morph_2, lemmas_set_mention_1, lemmas_set_mention_2


def compare_morph_features(lemma_mention_1, lemma_mention_2, unalterable_morph_1, unalterable_morph_2, alterable_morph_1, alterable_morph_2):
    lemma_equality = 0
    antec_is_noun = 0
    anaph_is_noun = 0
    antec_is_pro = 0
    anaph_is_pro = 0
    antec_is_adj = 0
    anaph_is_adj = 0
    antec_is_numb = 0
    anaph_is_numb = 0
    antec_is_geox = 0
    anaph_is_geox = 0
    antec_is_name = 0
    anaph_is_name = 0
    antec_is_orgn = 0
    anaph_is_orgn = 0
    gender = 0
    number = 0
    animation = 0
    cur_gender_1 = ''
    cur_gender_2 = ''
    cur_number_1 = ''
    cur_number_2 = ''
    cur_anim_1 = ''
    cur_anim_2 = ''
    #print(unalterable_morph_2)
    #print(unalterable_morph_1)
    if lemma_mention_1 == lemma_mention_2:
        lemma_equality = 1
    if ('NOUN' in unalterable_morph_1):
        antec_is_noun = 1
    if ('NOUN' in unalterable_morph_2):
        anaph_is_noun = 1
    if ('NPRO' in unalterable_morph_1):
        antec_is_pro = 1
    if ('NPRO' in unalterable_morph_2):
        anaph_is_pro = 1
    if ('ADJF' in unalterable_morph_1):
        antec_is_adj = 1
    if ('ADJF' in unalterable_morph_2):
        anaph_is_adj = 1
    if ('NUMB' in unalterable_morph_1):
        antec_is_numb = 1
    if ('NUMB' in unalterable_morph_2):
        anaph_is_numb = 1
    if ('Geox' in unalterable_morph_1):
        antec_is_geox = 1
    if ('Geox' in unalterable_morph_2):
        anaph_is_geox = 1
    if ('Name' in unalterable_morph_1) or ('Surn' in unalterable_morph_1):
        antec_is_name = 1
    if ('Name' in unalterable_morph_2) or ('Surn' in unalterable_morph_2):
        anaph_is_name = 1
    if ('Orgn' in unalterable_morph_1):
        antec_is_orgn = 1
    if ('Orgn' in unalterable_morph_2):
        anaph_is_orgn = 1

    for feature in unalterable_morph_1:
        if feature == 'masc' or feature == 'femn' or feature == 'neut':
            cur_gender_1 = feature
        if feature == 'sing' or feature =='plur':
            cur_number_1 = feature
        if feature == 'anim' or feature == 'inan':
            cur_anim_1 = feature

    for feature in alterable_morph_1:
        if feature == 'masc' or feature == 'femn' or feature == 'neut':
            cur_gender_1 = feature
        if feature == 'sing' or feature =='plur':
            cur_number_1 = feature
    for feature in unalterable_morph_2:
        if feature == 'masc' or feature == 'femn' or feature == 'neut':
            cur_gender_2 = feature
        if feature == 'sing' or feature =='plur':
            cur_number_2 = feature
        if feature == 'anim' or feature == 'inan':
            cur_anim_2 = feature
    for feature in alterable_morph_2:
        if feature == 'masc' or feature == 'femn' or feature == 'neut':
            cur_gender_2 = feature
        if feature == 'sing' or feature =='plur':
            cur_number_2 = feature
    if cur_gender_1 == cur_gender_2:
        gender = 1
    if cur_number_1 == cur_number_2:
        number = 1
    if cur_anim_1 == cur_anim_2:
        animation = 1
    return lemma_equality, gender, number, animation, lemma_mention_1, lemma_mention_2, antec_is_noun, anaph_is_noun, \
           antec_is_pro, anaph_is_pro, antec_is_adj, anaph_is_adj, antec_is_numb, anaph_is_numb, antec_is_geox, \
           anaph_is_geox, antec_is_name, anaph_is_name, antec_is_orgn, anaph_is_orgn
# build data frame row
def build_row(mention_1, mention_2, start_1, start_2, len_1, len_2, text_len, are_from_same_group,
              chains_filename, lemma_equality, gender, number, animation, lemmas_equality_num, antec_is_noun, anaph_is_noun, \
           antec_is_pro, anaph_is_pro, antec_is_adj, anaph_is_adj, antec_is_numb, anaph_is_numb, antec_is_geox, \
           anaph_is_geox, antec_is_name, anaph_is_name, antec_is_orgn, anaph_is_orgn, anteclongerthree, anaphlongerthree, dist_of_means, dist_of_max ):
    men_1_lower = mention_1.lower()
    men_2_lower = mention_2.lower()
    row = {}
    row['Equality'] = int(men_1_lower == men_2_lower)
    row['M1ContainsM2'] = int(men_1_lower in men_2_lower)
    row['M2ContainsM1'] = int(men_2_lower in men_1_lower)
    row['Distance'] = abs(start_2 - (start_1 + len_1))
    row['RelativeDistance'] = row['Distance'] / text_len
    row['Mention1'] = mention_1
    row['Mention2'] = mention_2
    row['Mention1Id'] = (start_1, len_1)
    row['Mention2Id'] = (start_2, len_2)
    row['SameGroup'] = int(are_from_same_group)
    row['ChainsFilename'] = chains_filename
    row['SameLemma'] = lemma_equality
    row['SameGender'] = gender
    row['SameNumber'] = number
    row['SameAnimation'] = animation
    row['LemmasEquality'] = lemmas_equality_num
    row['AntecLongerThree'] = anteclongerthree
    row['AnaphLongerThree'] = anaphlongerthree
    row['AntecIsNoun'] = antec_is_noun
    row['AnaphIsNoun'] = anaph_is_noun
    row['AntecIsPro'] = antec_is_pro
    row['AnaphIsPro'] = anaph_is_pro
    row['AntecIsAdj'] = antec_is_adj
    row['AnaphIsAdj'] = anaph_is_adj
    row['AntecIsNumb'] = antec_is_numb
    row['AnaphIsNumb'] = anaph_is_numb
    row['AntecIsGeox'] = antec_is_geox
    row['AnaphIsGeox'] = anaph_is_geox
    row['AntecIsName'] = antec_is_name
    row['AnaphIsName'] = anaph_is_name
    row['AntecIsOrgn'] = antec_is_orgn
    row['AnaphIsOrgn'] = anaph_is_orgn
    row['DistMeanVectors'] = dist_of_means
    row['DistMaxVectors'] = dist_of_max
    return row

def build_row2(mention_1, mention_2, start_1, start_2, len_1, len_2, text_len, are_from_same_group,
              chains_filename, lemma_equality, gender, number, animation, lemmas_equality_num, antec_is_noun, anaph_is_noun, \
           antec_is_pro, anaph_is_pro, antec_is_geox, \
           anaph_is_geox, antec_is_name, anaph_is_name, anteclongerthree, anaphlongerthree):
    men_1_lower = mention_1.lower()
    men_2_lower = mention_2.lower()
    row = {}
    row['Equality'] = int(men_1_lower == men_2_lower)
    row['M1ContainsM2'] = int(men_1_lower in men_2_lower)
    row['M2ContainsM1'] = int(men_2_lower in men_1_lower)
    row['Distance'] = abs(start_2 - (start_1 + len_1))
    row['RelativeDistance'] = row['Distance'] / text_len
    row['Mention1'] = mention_1
    row['Mention2'] = mention_2
    row['Mention1Id'] = (start_1, len_1)
    row['Mention2Id'] = (start_2, len_2)
    row['SameGroup'] = int(are_from_same_group)
    row['ChainsFilename'] = chains_filename
    row['SameLemma'] = lemma_equality
    row['SameGender'] = gender
    row['SameNumber'] = number
    row['SameAnimation'] = animation
    row['LemmasEquality'] = lemmas_equality_num
    row['AntecLongerThree'] = anteclongerthree
    row['AnaphLongerThree'] = anaphlongerthree
    row['AntecIsNoun'] = antec_is_noun
    row['AnaphIsNoun'] = anaph_is_noun
    row['AntecIsPro'] = antec_is_pro
    row['AnaphIsPro'] = anaph_is_pro
    row['AntecIsGeox'] = antec_is_geox
    row['AnaphIsGeox'] = anaph_is_geox
    row['AntecIsName'] = antec_is_name
    row['AnaphIsName'] = anaph_is_name

    return row



for filename in listdir(TEXT_PATH):
    print(filename)
    with open(join(TEXT_PATH, filename), encoding='utf16') as f:
        text = f.read()
    text_len = len(text)
    if text_len > 0:
        chains_entries = []
        with open(join(SEMAN_PATH, filename), encoding='utf16') as f2:
            content = f2.readlines()
            sem_list = [x.split() for x in content]
        with open(join(CHAINS_PATH, filename), encoding='utf8') as f:
            for line in f:
                chains_entries.append(tuple(map(lambda x: int(x), line.strip().split(' '))))
            # print(len(chains_entries), 'tut')
        count = 0
        chains_entries_len = len(chains_entries)
        for i in range(chains_entries_len):
            _, start_i, len_i, chain_i = chains_entries[i]
            # print(_, start_i, len_i, chain_i)
            men_i = text[start_i:start_i + len_i]
            # print(men_i)
            for j in range(i + 1, chains_entries_len):
                mention_flag = 0
                _, start_j, len_j, chain_j = chains_entries[j]
                for elem in sem_list:
                    if (str(start_i) == elem[0]) and (str(len_i) == elem[1]) and (str(start_j) == elem[2]) and (str(len_j) == elem[3]):
                        count += 1
                        dist_of_means = elem[4]
                        dist_of_max = elem[5]
                        mention_flag = 1
                if mention_flag == 0:
                    continue
                men_j = text[start_j:start_j + len_j]
                # print(_, start_j, len_j, chain_j, men_j)
                lemma_mention_1, lemma_mention_2, unalterable_morph_1, unalterable_morph_2, alterable_morph_1, alterable_morph_2, lemmas_set_1, lemmas_set_2 = prepare_morph_features(
                    men_i, men_j, start_i, start_j, len_i, len_j, filename)
                # print(lemma_mention_1, lemma_mention_2, unalterable_morph_1, unalterable_morph_2, alterable_morph_1, alterable_morph_2)
                lemma_equality, gender, number, animation, lemma_mention_1, lemma_mention_2, antec_is_noun, anaph_is_noun, \
                antec_is_pro, anaph_is_pro, antec_is_adj, anaph_is_adj, antec_is_numb, anaph_is_numb, antec_is_geox, \
                anaph_is_geox, antec_is_name, anaph_is_name, antec_is_orgn, anaph_is_orgn = compare_morph_features(
                    lemma_mention_1, lemma_mention_2, unalterable_morph_1, unalterable_morph_2,
                    alterable_morph_1, alterable_morph_2)
                # print(lemma_equality, noun_and_pro, gender, number, animation, lemma_mention_1, lemma_mention_2)
                lemmas_equality_num, anteclongerthree, anaphlongerthree = count_lemmas_intersection(lemmas_set_1, lemmas_set_2)
                row = build_row(men_i, men_j, start_i, start_j, len_i, len_j, text_len, chain_i == chain_j,
                                filename, lemma_equality, gender, number, animation, lemmas_equality_num, antec_is_noun,
                                anaph_is_noun, antec_is_pro, anaph_is_pro, antec_is_adj, anaph_is_adj, antec_is_numb, anaph_is_numb,
                                antec_is_geox, anaph_is_geox, antec_is_name, anaph_is_name, antec_is_orgn, anaph_is_orgn,
                                anteclongerthree, anaphlongerthree, dist_of_means, dist_of_max)
                #print(row)
                #row2 = build_row2(men_i, men_j, start_i, start_j, len_i, len_j, text_len, chain_i == chain_j,
                                  #filename, lemma_equality, gender, number, animation, lemmas_equality_num, antec_is_noun,
                                  #anaph_is_noun, antec_is_pro, anaph_is_pro, antec_is_geox, anaph_is_geox,
                                  #antec_is_name, anaph_is_name, anteclongerthree, anaphlongerthree)
                rows_list.append(row)
                #rows_list2.append(row2)
                # print(chain_i)
                count += 1
                #print(count)
df = pd.DataFrame(rows_list)
#df2 = pd.DataFrame(rows_list2)
df.to_csv('data_set.csv', encoding='utf16')
#df2.to_csv('classifier_output_dis.csv', encoding='utf16')
#rate = 2
#num_pos = df.loc[df['SameGroup'] == 1].shape[0]
#num_neg = df.loc[df['SameGroup'] == 0].shape[0]
#frac = 1 - ((num_pos * 5) / num_neg)
#print(num_pos, num_neg, frac)
#df2 = df.drop(df.query("SameGroup == 0").sample(frac=frac).index)
#print(df.loc[df['SameGroup'] == 0].shape[0])
#df2.to_csv('test_model_fixed_k5.csv', encoding='utf16')
#frac2 = 1 - ((num_pos * 6) / num_neg)
#frac3 = 1 - ((num_pos * 4) / num_neg)
#df3 = df.drop(df.query("SameGroup == 0").sample(frac=frac2).index)
#df4 = df.drop(df.query("SameGroup == 0").sample(frac=frac3).index)
#df3.to_csv('test_model_fixed_k6.csv', encoding='utf16')
#df4.to_csv('test_model_fixed_k4.csv', encoding='utf16')

        #print('Number of chains entries', len(chains_entries), 'Number of mention pairs', count)
    #else:
        #print('No chains: text is empty.')

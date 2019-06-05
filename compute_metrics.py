'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
скрипт проверяет формат входных данных (key и response) и считает метрики muc6, b cube и ceafe  
проверяет:
-сколько чисел в строке (должно быть 4)
-не повторяются ли упоминания в одном документе
находя данные несоответствия в key или response, выводит предупреждение и имя файла, исключает файл и не считает для него метрики

-нет ли цепочек только с 1 упоминанием
находя данное несоответсвтие в key, выводит предупреждение и имя файла

если при подсчете метрики происходит деление на нуль, то метрика зануляется. 
если recall и precision равны нулям, то f-measure зануляется.

если в документе отсутствует цепочка (e.g. 1, 2, 4, 5), выводит соответствующее предупреждение и имя файла, и 
метрики для данного документа будут посчитаны НЕВЕРНО

все метрики считаются для каждого документа, записываются в списки, которые выгружаются в файл формата csv

обратите внимание, что однозначные метрики могут записаться в cvs файл в виде даты. во избежание этого, поменяйте
 в системных настройках (Windows), а именно в панели управления - язык и международные (региональные) стандарты, 
 разделители с запятой на точку.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from os import listdir
from os.path import join
import os.path
import os
import itertools
from os.path import join
from scipy.optimize import linear_sum_assignment
import numpy as np
import pandas as pd
KEY_PATH = './keys'
RESPONSE_PATH = './responses'

filenames = []     # списки для pandas
key_mentions_num = []
key_chains_num = []
response_mentions_num = []
response_chains_num = []
muc6_recall_list = []
muc6_precision_list = []
muc6_f_measure_list = []
b3_recall_list = []
b3_precision_list = []
b3_f_measure_list = []
ceafe_recall_list = []
ceafe_precision_list = []
ceafe_f_measure_list = []

START_IND = 1
LENGTH_IND = 2
CHAIN_NUM_IDX = 3


def check_line_in_doc(list_of_lists):   #проверить сколько чисел в строчке текущего документа
    for line in list_of_lists:
        if len(line) != 4:
            return False
        else:
            continue
    return True

def list_to_dict(mentions_list): #подготовка словарей для вычисления muc6

    mentions_dict = {}
    for m in mentions_list:
        ch = m[CHAIN_NUM_IDX]
        if ch not in mentions_dict:
            mentions_dict[ch] = [m]
        else:
            l = mentions_dict[ch]
            l.append(m)


    return mentions_dict

    #возвращает словарь номер цепочки: список упоминаний в этой цепочке


def list_to_dict_muc6(mentions_list):  # подготовка второго словаря для muc6
    mentions_dict = {}

    for m in mentions_list:
        start_length = m[START_IND], m[LENGTH_IND]
        mentions_dict[start_length] = m
    return mentions_dict  # возвращает словарь начало, конец упоминания: список с данными об упоминании (номер, н
    # длина, цепочка)


def compute_muc6(keys_mentions_dict, responses_mentions_dict):  # вычисляется числитель и знаменатель для метрики muc6

    muc6_numerator = 0
    muc6_denominator = 0
    if '0' in keys_mentions_dict:
        for i in range(0, len(keys_mentions_dict)):
            try:
                values = keys_mentions_dict[str(i)]  # записали все упоминания по i-цепочке
            except KeyError:
                print(key_filename, 'does not contain chain', i)
                break
            singleton = 0
            response_chains = set()  # создали сет для i-цепочки
            for elem in values:
                key = elem[START_IND], elem[LENGTH_IND]
                if key in responses_mentions_dict:
                    response_elem = responses_mentions_dict[key]  # достаем значения из респонза по началу и длине
                    response_elem_ch = int(response_elem[CHAIN_NUM_IDX])
                    response_chains.add(response_elem_ch)
                else:
                    singleton += 1
            partition = len(response_chains) + singleton
            k = len(values)
            muc6_numerator += k - partition
            muc6_denominator += k - 1
    else:
        for i in range(1, len(keys_mentions_dict) + 1):
            try:
                values = keys_mentions_dict[str(i)]  # записали все упоминания по i-цепочке
            except KeyError:
                print(key_filename, 'does not contain chain', i)
                break
            singleton = 0
            response_chains = set()  # создали сет для i-цепочки
            for elem in values:
                key = elem[START_IND], elem[LENGTH_IND]
                if key in responses_mentions_dict:
                    response_elem = responses_mentions_dict[key]  # достаем значения из респонза по началу и длине
                    response_elem_ch = int(response_elem[CHAIN_NUM_IDX])
                    response_chains.add(response_elem_ch)
                else:
                    singleton += 1
            partition = len(response_chains) + singleton
            k = len(values)
            muc6_numerator += k - partition
            muc6_denominator += k - 1

    return muc6_numerator, muc6_denominator


def round_n(number):  # перевод в проценты и округление до 2х знаков
    return round(number * 100, 2)


def list_to_dict_chains(mentions_list): # подготовка словарей для b3 и ceafe

    dictionary = {}

    for m in mentions_list:
        ch = m[CHAIN_NUM_IDX]
        if ch not in dictionary:
            dictionary[ch] = [tuple(m[START_IND:3])]
        else:
            l = dictionary[ch]
            l.append(tuple(m[START_IND:3]))
    return dictionary #возвращает словарь номер цепочки: список пар начало, длина для каждого упоминания в этой цепочке

def compute_b3(keys_dict, response_dict): #вычисляется b3
    b3_numerator = 0
    k = 0
    if '0' in keys_dict:
        for i in range(0, len(keys_dict)):
            try:
                key_values = keys_dict[str(i)]
            except KeyError:
                print(key_filename, 'does not contain chain', i)
                break
            k += len(key_values)
            if '0' in response_dict:
                for m in range(0, len(response_dict)):
                    try:
                        response_values = response_dict[str(m)]
                    except KeyError:
                        print(key_filename, 'does not contain chain', m)
                        break
                    intersection_len = len(list(set(key_values) & set(response_values)))
                    b3_numerator += (intersection_len ** 2) / len(key_values)
            else:
                for m in range(1, len(response_dict) + 1):
                    try:
                        response_values = response_dict[str(m)]
                    except KeyError:
                        print(key_filename, 'does not contain chain', m)
                        break
                    intersection_len = len(list(set(key_values) & set(response_values)))
                    b3_numerator += (intersection_len ** 2) / len(key_values)

    else:
        for i in range(1, len(keys_dict) + 1):
            try:
                key_values = keys_dict[str(i)]
            except KeyError:
                print(key_filename, 'does not contain chain', i)
                break
            k += len(key_values)
            if '0' in response_dict:
                for m in range(0, len(response_dict)):
                    try:
                        response_values = response_dict[str(m)]
                    except KeyError:
                        print(key_filename, 'does not contain chain', m)
                        break
                    intersection_len = len(list(set(key_values) & set(response_values)))
                    b3_numerator += (intersection_len ** 2) / len(key_values)
            else:
                for m in range(1, len(response_dict) + 1):
                    try:
                        response_values = response_dict[str(m)]
                    except KeyError:
                        print(key_filename, 'does not contain chain', m)
                        break
                    intersection_len = len(list(set(key_values) & set(response_values)))
                    b3_numerator += (intersection_len ** 2) / len(key_values)


    return 0.0 if k == 0 else b3_numerator / k

def compute_ceafe(weight_matrix, key_chain_dict, response_chain_dict): #вычисляется ceafe
    row_ind, col_ind = linear_sum_assignment(weight_matrix)
    sum = weight_matrix[row_ind, col_ind].sum()
    recall = -sum / len(key_chain_dict)
    precision = -sum / len(response_chain_dict)
    return recall, precision


def get_weight_matrix(key_dict, response_dict): #вычисляется матрица весов для ceafe
    matrix = np.zeros((len(key_dict), len(response_dict)))
    for row_idx, key_key in enumerate(key_dict.keys()): #key_key - номер цепочки в key
        for col_idx, response_key in enumerate(response_dict.keys()): #response_key - номер цеочки в response
            key_mention = key_dict[key_key] #запоминаем значние по ключу (по номеру цепочки)
            response_mention = response_dict[response_key]
            matrix[row_idx, col_idx] = compute_fi(key_mention, response_mention)
    return matrix


def compute_fi(key_chain, response_chain):  #вычисляется функции фи для ceafe
    intersection_len = len(list(set(key_chain) & set(response_chain)))
    return -(2 * intersection_len / (len(key_chain) + len(response_chain)))


for key_filename in listdir(KEY_PATH):
    print(key_filename)


    with open(join(KEY_PATH, key_filename), encoding='utf-8') as f:
        key_file = f.read()
        keys = []
        key = key_file.splitlines()
        [keys.append(mention.split()) for mention in key]
        filenames.append(key_filename)
        key_mentions_num.append(len(keys))
        keys_cur_dict = {}
        keys_cur_dict = list_to_dict_chains(keys)
        key_chains_num.append(len(keys_cur_dict))
        if not os.path.exists(join(RESPONSE_PATH, key_filename)):   #проверяем, если ли в response файл с таким же названием
            response_mentions_num.append('0')
            response_chains_num.append('0')
            muc6_recall_list.append('0')
            muc6_precision_list.append('0')
            muc6_f_measure_list.append('0')
            b3_recall_list.append('0')
            b3_precision_list.append('0')
            b3_f_measure_list.append('0')
            ceafe_recall_list.append('0')
            ceafe_precision_list.append('0')
            ceafe_f_measure_list.append('0')
            continue

        else:
            if (os.path.getsize(join(RESPONSE_PATH, key_filename))) and (os.path.getsize(join(KEY_PATH, key_filename)) == 0):
                response_mentions_num.append('0')
                response_chains_num.append('0')
                muc6_recall_list.append('0')
                muc6_precision_list.append('0')
                muc6_f_measure_list.append('0')
                b3_recall_list.append('0')
                b3_precision_list.append('0')
                b3_f_measure_list.append('0')
                ceafe_recall_list.append('0')
                ceafe_precision_list.append('0')
                ceafe_f_measure_list.append('0')
                continue
            else:
                if not check_line_in_doc(keys):  #проверяем формат строки в key
                    print('A line in', key_filename, 'contains less/more numbers than required')
                    filenames.remove(key_filename)
                    key_mentions_num.pop()
                    key_chains_num.pop()
                    continue
                else:
                    cur_list = []
                    cur_set = set()
                    values = keys_cur_dict.values()
                    cur_list = list(itertools.chain(*values))
                    cur_set = set(cur_list)
                    if len(cur_list) != len(cur_set):
                        print(cur_list.difference(cur_set))
                        print(cur_set.difference(cur_list))#проверяем нет ли повторяющихся упоминаний в одном документе в key
                        print('The same mentions in', key_filename)
                        filenames.remove(key_filename)
                        key_mentions_num.pop()
                        key_chains_num.pop()
                        continue


                    keys_cur_dict = list_to_dict(keys)   #проверяем, нет ли цепочек с 1 упоминанием в key
                    values = keys_cur_dict.values()
                    for elem in values:
                        if len(elem) < 2:
                            print('A chain contains only 1 mention in', key_filename)
                    with open(join(RESPONSE_PATH, key_filename), encoding='utf-8') as f:
                        response_file = f.read()
                        responses = []
                        response = response_file.splitlines()
                        [responses.append(mention.split()) for mention in response]

                        if not check_line_in_doc(responses):  #проверяем формат строки в response
                            print('A line in', key_filename, 'contains less/more numbers than required')
                            filenames.remove(key_filename)
                            key_mentions_num.pop()
                            key_chains_num.pop()
                            continue
                        else:
                            response_mentions_num.append(len(responses))
                            responses_cur_dict = {}
                            cur_list = []
                            cur_set = set()
                            responses_cur_dict = list_to_dict_chains(responses)
                            response_chains_num.append(len(responses_cur_dict))
                            values = responses_cur_dict.values()
                            cur_list = list(itertools.chain(*values))
                            cur_set = set(cur_list)
                            if len(cur_list) != len(cur_set):     #проверяем, нет ли повторяющихся упоминаний в одном документе в key
                                print('The same mentions in', key_filename)
                                muc6_recall_list.append('0')
                                muc6_precision_list.append('0')
                                muc6_f_measure_list.append('0')
                                b3_recall_list.append('0')
                                b3_precision_list.append('0')
                                b3_f_measure_list.append('0')
                                ceafe_recall_list.append('0')
                                ceafe_precision_list.append('0')
                                ceafe_f_measure_list.append('0')
                                continue
                            else:
                                #muc6
                                muc6_recall = 0
                                muc6_precision = 0
                                muc6_f_measure = 1  # 1 выступает в роли флага
                                b3_recall = 0
                                b3_precision = 0
                                b3_f_measure = 0
                                ceafe_recall = 0
                                ceafe_precision = 0
                                ceafe_f_measure = 0
                                muc6_recall_numerator, muc6_recall_denominator = compute_muc6(list_to_dict(keys), list_to_dict_muc6(responses))
                                muc6_precision_numerator, muc6_precision_denominator = compute_muc6(list_to_dict(responses), list_to_dict_muc6(keys))
                                if muc6_recall_denominator == 0:
                                    muc6_recall = 0
                                    muc6_f_measure = 0
                                else:
                                    muc6_recall = muc6_recall_numerator / muc6_recall_denominator
                                if muc6_precision_denominator == 0:
                                    muc6_precision = 0
                                    muc6_f_measure = 0
                                else:
                                    muc6_precision = muc6_precision_numerator / muc6_precision_denominator
                                if (muc6_recall and muc6_precision) == 0:
                                    muc6_f_measure = 0
                                elif muc6_f_measure == 1:
                                    muc6_f_measure = 2 * muc6_precision * muc6_recall / (muc6_precision + muc6_recall)
                                muc6_recall_list.append(str(round_n(muc6_recall)))
                                muc6_precision_list.append(str(round_n(muc6_precision)))
                                muc6_f_measure_list.append(str(round_n(muc6_f_measure)))

                                #b3
                                b3_recall = compute_b3(list_to_dict_chains(keys), list_to_dict_chains(responses))
                                b3_precision = compute_b3(list_to_dict_chains(responses), list_to_dict_chains(keys))
                                if b3_recall == 0 and b3_precision == 0:
                                    b3_f_measure = 0
                                else:
                                    b3_f_measure = 2 * b3_precision * b3_recall / (b3_precision + b3_recall)
                                b3_recall_list.append(str(round_n(b3_recall)))
                                b3_precision_list.append(str(round_n(b3_precision)))
                                b3_f_measure_list.append(str(round_n(b3_f_measure)))

                                #ceafe
                                key_chain_dict = list_to_dict_chains(keys)
                                response_chain_dict = list_to_dict_chains(responses)
                                ceafe_recall, ceafe_precision = compute_ceafe(
                                    get_weight_matrix(key_chain_dict, response_chain_dict), key_chain_dict,
                                    response_chain_dict)
                                if ceafe_recall == 0 and ceafe_precision == 0:
                                    ceafe_f_measure = 0
                                else:
                                    ceafe_f_measure = 2 * ceafe_recall * ceafe_precision / (ceafe_recall + ceafe_precision)
                                ceafe_recall_list.append(str(round_n(ceafe_recall)))
                                ceafe_precision_list.append(str(round_n(ceafe_precision)))
                                ceafe_f_measure_list.append(str(round_n(ceafe_f_measure)))


df = pd.DataFrame({
'file name': filenames,
'number of mentions in key': key_mentions_num,
'number of chains in key': key_chains_num,
'number of mentions in response': response_mentions_num,
'number of chains in response': response_chains_num,
'muc6 recall': muc6_recall_list,
'muc6 precision': muc6_precision_list,
'muc6 f_measure': muc6_f_measure_list,
'b cube recall': b3_recall_list,
'b cube precision': b3_precision_list,
'b cube f_measure': b3_f_measure_list,
'ceafe recall': ceafe_recall_list,
'ceafe precision': ceafe_precision_list,
'ceafe f_measure': ceafe_f_measure_list,
})

df.to_csv("my_metrics.csv", sep=';')


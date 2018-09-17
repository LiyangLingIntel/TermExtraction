# coding: utf-8

import xlrd
import nltk
import os
import csv
import pickle
import re
from settings import OUTPUT_ROOT, PROJECT_NAME, PICKLED_SINGLE_WORD_TRUE_TERM_FILE, DATA_SOURCE_FOLDER, SOURCE_TRUE_TERMS, TOOL_BASE_FOLDER
from utility import FileIOUtil
from data_processing.data_clean import ENTITY, DataCleanUtil

OUTPUT_FOLDER = OUTPUT_ROOT + '\\' + PROJECT_NAME
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


def true_term_filter(source_path):
    """
    filter single-word terms and multi-word terms into different files
    :param source_path: source term full path
    :return: multi_word_term_path, output files of single-word terms and multi-word terms
    """
    single_word_true_term_dict_path = os.path.join(OUTPUT_ROOT, PICKLED_SINGLE_WORD_TRUE_TERM_FILE)
    # if os.path.exists(single_word_true_term_dict_path):
    #     with open(single_word_true_term_dict_path, "rb+") as pickled_file:
    #         single_word_term_dict = pickle.load(pickled_file)
    # else:
    #     single_word_term_dict = {}
    single_word_term_dict = FileIOUtil.input_from_json(TOOL_BASE_FOLDER, '', 'SINGLE_WORD_TRUE_TERMS')
    multi_word_term_dict = FileIOUtil.input_from_json(TOOL_BASE_FOLDER, '', 'MULTI_WORD_TRUE_TERMS')

    source_terms = []
    if source_path.endswith(('.xlsx', '.xls')):
        with xlrd.open_workbook(source_path) as source_file:
            table = source_file.sheet_by_index(0)
            if PROJECT_NAME == 'OSCE':
                source_terms = table.col_values(3)[1:]    # OSCE
            elif PROJECT_NAME == 'WFBS':
                source_terms = table.col_values(0)[1:]    # WFBS
    elif source_path.endswith('csv'):
        with open(source_path, 'r', encoding='utf-8') as source_file:
            if PROJECT_NAME == 'Ti':
                clean_util = DataCleanUtil()             # Ti
                reader = csv.reader(source_file)
                source_terms = []
                for row in reader:
                    text = row[1]
                    while ENTITY.search(text):
                        text = clean_util._unescape(text)
                    term = re.sub(r'\?', '™', text)
                    source_terms.append(term)
                source_terms = source_terms[1:]

    self_single_word_term_list = []
    self_multi_word_term_list = []
    for term in source_terms:
        term = term.strip()
        if ' ' not in term:
            if term and term not in single_word_term_dict:
                single_word_term_dict[term] = ''
            # self_single_word_term_list.append(term)
        else:
            if term and term not in multi_word_term_dict:
                multi_word_term_dict[term] = ''
            # self_multi_word_term_list.append(term)

    # FileIOUtil.output_list_to_file(self_single_word_term_list, OUTPUT_FOLDER, PROJECT_NAME, 'SINGLE_WORD_TRUE_TERM', time_tag=False)
    # FileIOUtil.output_list_to_file(self_multi_word_term_list, OUTPUT_FOLDER, PROJECT_NAME, 'MULTI_WORD_TRUE_TERM', time_tag=False)
    FileIOUtil.output_to_json(single_word_term_dict, TOOL_BASE_FOLDER, '', 'SINGLE_WORD_TRUE_TERMS')
    FileIOUtil.output_to_json(multi_word_term_dict, TOOL_BASE_FOLDER, '', 'MULTI_WORD_TRUE_TERMS')
    # with open(single_word_true_term_dict_path, 'wb+') as pickled_file:
    #     pickle.dump(single_word_term_dict, pickled_file)


def term_feature_statistics(multi_word_term_path):
    """
    tag multi_word terms, output their tags features
    :param multi_word_term_path:
    :return: none, output output current project tag feature, overall tag feature and multi-word terms tags
    """
    multi_word_features_dict_path = os.path.join(OUTPUT_ROOT, 'MULTI_WORD_TERM_FEATURES_STATISTIC.txt')
    if os.path.exists(multi_word_features_dict_path):
        with open(multi_word_features_dict_path, 'rb+') as pickled_file:
            multi_word_features = pickle.load(pickled_file)
    else:
        multi_word_features = {}

    with open(multi_word_term_path, 'r', encoding='utf-8') as multi_word_term_file:
        terms = multi_word_term_file.readlines()
        multi_word_terms = [term.strip() for term in terms]

    multi_word_terms_tagged = {}
    for term in multi_word_terms:
        word_tokens = nltk.tokenize.word_tokenize(term)
        term_tagged = nltk.pos_tag(word_tokens)
        term_tagged = list(zip(*term_tagged))
        multi_word_terms_tagged[term] = term_tagged

    self_project_tag_feature = {}
    for term_feature in multi_word_terms_tagged.values():
        feature = term_feature[1]
        if feature not in self_project_tag_feature:
            self_project_tag_feature[feature] = 0
        self_project_tag_feature[feature] += 1

    for feature, number in self_project_tag_feature.items():
        if feature not in multi_word_features:
            multi_word_features[feature] = 0
        multi_word_features[feature] += number

    FileIOUtil.output_dict_to_file(multi_word_terms_tagged, OUTPUT_FOLDER, PROJECT_NAME, 'TRUE_TERM_TAGGED')
    FileIOUtil.output_dict_to_file(self_project_tag_feature, OUTPUT_FOLDER, PROJECT_NAME, 'TAG_FEATURE', sort=True, time_tag=True)
    FileIOUtil.output_dict_to_file(multi_word_features, OUTPUT_ROOT, 'OVERALL', 'TERM_TAG_FEATURE_STATISTIC', sort=True, time_tag=False)
    with open(multi_word_features_dict_path, 'wb+') as pickled_file:
        pickle.dump(multi_word_features, pickled_file)


if __name__ == '__main__':

    # multi_word_term_path = os.path.join(OUTPUT_FOLDER, PROJECT_NAME + '_MULTI_WORD_TRUE_TERM.txt')
    # source_path = os.path.join(DATA_SOURCE_FOLDER, SOURCE_TRUE_TERMS)
    # true_term_filter(source_path)
    # term_feature_statistics(multi_word_term_path)

    source_path = r'D:\Files\Projects\python\TermExtraction\data_materials\source_file\WFBS_Terminology_(P1,P2,NewWording)_20180403.xlsx'
    true_term_filter(source_path)

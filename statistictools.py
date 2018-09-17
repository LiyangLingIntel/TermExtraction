
# coding: utf-8

import os
from math import log
from settings import PROJECT_NAME, LING_FOLDER, STAT_FOLDER, OUTPUT_ROOT, PICKLED_SINGLE_WORD_TRUE_TERM_FILE
from utility import FileIOUtil
from collections import OrderedDict


"""
{
    candidate: [O_11, [R_1, C_1, ...], E_11],
    ...
}
O_11: full words matched candidate number
R_1 = O_11 + O_12 : first word matched candidate number
C_1 = O_11 + O_21 : second word matched candidate number
... 
E_11 = (R_1 + C_1 + ...)/N^(len-1) : candidate expected number
"""


class StatisticsUtil(object):

    def __init__(self, candidates):

        self.candidates_info, self.total_number = self._base_info_prepare(candidates)

    def output_ranked_candidate(self, ranked_candidate, rank_type):

        file_name = rank_type + '_candidates'
        FileIOUtil.output_dict_to_file(ranked_candidate, STAT_FOLDER, PROJECT_NAME, file_name+'_sorted', sort=True, time_tag=False)
        FileIOUtil.output_to_json(ranked_candidate, STAT_FOLDER, PROJECT_NAME, file_name)

    def input_ranked_candidates(self, rank_type):
        """
        :param rank_type:
        :return: Ordered_dict, ranked value sorted DESC
        """
        ordered_data = OrderedDict()
        file_name = rank_type + '_candidates'
        data = FileIOUtil.input_from_json(STAT_FOLDER, PROJECT_NAME, file_name)

        # str(float) including positive & negative value can be sorted correctly, tested
        data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        for item in data:
            ordered_data[item[0]] = float(item[1])
        return ordered_data

    def _base_info_prepare(self, candidates):
        """
        :param candidates: multi_word_candidate_dict
        :return: candidates_info
        """
        candidates_info = {}
        # with open(MULTI_WORD_CANDIDATE_PATH, 'rb') as pickled_cadidates:
        #     candidates_info = pickle.load(pickled_cadidates)
        word_statistic = {}
        total_number = sum(list(candidates.values()))

        for candidate_tuple, number in candidates.items():
            for word in candidate_tuple:
                if word not in word_statistic:
                    word_statistic[word] = 0
                word_statistic[word] += number

        for candidate_tuple, number in candidates.items():
            candidate_str = ''
            candidate_len = len(candidate_tuple)
            edge_number = []
            for word in candidate_tuple:
                candidate_str += word + ' '
                edge_number.append(word_statistic[word])
            expect_number = float(sum(edge_number))/(total_number**(candidate_len-1))
            candidates_info[candidate_str.strip()] = [number, edge_number, expect_number]

        return candidates_info, total_number

    def frequency_rank(self):
        """
        :return: frequency_ranked_candidate{candidate:  value}
                output sorted result to file
        """
        term_frequency_ranked = {}
        for candidate, info in self.candidates_info.items():
            term_frequency_ranked[candidate] = info[0]/self.total_number

        self.output_ranked_candidate(term_frequency_ranked, 'frequency_ranked')

        return term_frequency_ranked

    def t_score_rank(self):
        """
        :return: t_score_ranked_candidate{candidate:  value}
                output sorted result to file
        """
        term_t_score_ranked = {}
        for candidate, info in self.candidates_info.items():
            term_t_score_ranked[candidate] = (info[0]-info[2])/info[0]**0.5

        self.output_ranked_candidate(term_t_score_ranked, 't_score_ranked')

        return term_t_score_ranked

    def mi_rank(self):
        """
        :return: mi_ranked_candidate{candidate: value}
                output sorted result to file
        mi means Church Mutual Information
        """
        term_mi_ranked = {}
        for candidate, info in self.candidates_info.items():
            term_mi_ranked[candidate] = log(info[0]/info[2], 2)

        self.output_ranked_candidate(term_mi_ranked, 'mi_ranked')

        return term_mi_ranked

    def mi_3_rank(self):
        """
        :return: mi_ranked_candidate{candidate: value}
                output sorted result to file
        mi means Church Mutual Information
        """
        term_mi_3_ranked = {}
        for candidate, info in self.candidates_info.items():
            term_mi_3_ranked[candidate] = log(info[0]**3/info[2], 2)

        self.output_ranked_candidate(term_mi_3_ranked, 'mi_3_ranked')

        return term_mi_3_ranked

    def dice_factor_rank(self):
        """
        :return: dice_factor_candidate{candidate:  value}
                output sorted result to file
        """
        term_dice_factor_ranked = {}
        for candidate, info in self.candidates_info.items():
            term_dice_factor_ranked[candidate] = log(info[0] / info[2], 2)

        self.output_ranked_candidate(term_dice_factor_ranked, 'dice_factor_ranked')

        return term_dice_factor_ranked

    def c_value_rank(self):
        """
        :return: c_value_ranked_candidate{candidate:  value}
                output sorted result to file
        """
        term_c_value_ranked = {}
        candidate_number = len(list(self.candidates_info.keys()))
        for candidate, info in self.candidates_info.items():
            candidate_len = len(info[1])
            term_c_value_ranked[candidate] = (candidate_len-1)*(info[0]-self.total_number/candidate_number)

        self.output_ranked_candidate(term_c_value_ranked, 'c_value_ranked')

        return term_c_value_ranked

    def llr_rank(self):               # unfinished
        """
        :return: llr_ranked_candidate{candidate:  value}
                output sorted result to file
        llr means Log Likelihood Radio
        """
        def l(k ,n, r):
            return r**k*(1-r)**(n-k)
        term_c_value_ranked = {}
        candidate_number = len(list(self.candidates_info.keys()))
        for candidate, info in self.candidates_info.items():
            candidate_len = len(info[1])
            # term_c_value_ranked[candidate] = (candidate_len-1)*(info[0]-total_number/candidate_number)
            raise Exception('function llr_rank has not been finished yet!')

        self.output_ranked_candidate(term_c_value_ranked, 'llr_ranked')

        return term_c_value_ranked


class ResultProcessUtil(object):

    def __init__(self, data):
        """
        data: OrderedDict, score already sorted DESC
        """
        self.data = data

        self.pre_analyze()
        self.norm_data = self.norm()

    def pre_analyze(self):
        data = self.data
        num = len(data)

        total = 0
        max_length = 0
        max_score = min_score = list(data.values())[0]

        for term, score in data.items():
            total += score
            if score > max_score:
                max_score = score
            if score < min_score:
                min_score = score

            term_len = len(term.split())

            if term_len > max_length:
                max_length = term_len

        average = total / num

        self.data_num = num
        self.average_score = average
        self.max_score = max_score
        self.min_score = min_score
        self.max_length = max_length

    def norm(self):
        norm_data = OrderedDict()
        diff = self.max_score - self.min_score

        for term, score in self.data.items():
            if diff != 0:
                norm_score = (score - self.average_score) / diff
            else:
                norm_score = 0
            norm_data[term] = norm_score

        self.norm_data = norm_data
        return norm_data

    def classify(self, threshold=None):
        """
        :param int, threshold: maximum of words in a phrase will be concerned
        :return: dict
        """

        classified_data = {}

        if not threshold:
            max_threshold = self.max_length
        else:
            max_threshold = min(threshold, self.max_length)

        for i in range(1, max_threshold + 1):
            classified_data[i] = OrderedDict()

        for term, score in self.norm_data.items():
            term_len = min(len(term.split()), max_threshold)
            classified_data[term_len][term] = [score]

        self.classified_data = classified_data
        return classified_data

    def merge(self, *args):

        import copy
        merge_data = copy.deepcopy(self.classified_data)

        for term_len, term_pair in merge_data.items():
            for term, score in term_pair.items():
                for data_util in args:
                    score.extend(data_util.classified_data[term_len][term])

        return merge_data


def do_statistic_processing(pickled_candidate_file='PICKLED_multi_word_candidate'):

    candidates_dict = FileIOUtil.input_from_pickled_file(LING_FOLDER, PROJECT_NAME, pickled_candidate_file)

    stat_util = StatisticsUtil(candidates_dict)

    frequency_ranked = stat_util.frequency_rank()
    t_score_ranked = stat_util.t_score_rank()
    mi_ranked = stat_util.mi_rank()
    mi_3_ranked = stat_util.mi_3_rank()
    dice_factor_ranked = stat_util.dice_factor_rank()
    c_value_ranked = stat_util.c_value_rank()

    rank_types = ['frequency_ranked', 't_score_ranked', 'mi_ranked', 'mi_3_ranked', 'dice_factor_ranked', 'c_value_ranked']

    for type in rank_types:
        data = stat_util.input_ranked_candidates(type)
        result_util = ResultProcessUtil(data)
        result_util.norm()
        classified_data = result_util.classify()
        for key in classified_data:
            output_name = type + '_' + str(key) + '_' + 'word'
            FileIOUtil.output_rank_result(classified_data[key], STAT_FOLDER, PROJECT_NAME, output_name)


def do_statistic_processing_by_length(pickled_candidate_file='PICKLED_multi_word_candidate'):

    candidates_dict = FileIOUtil.input_from_pickled_file(LING_FOLDER, PROJECT_NAME, pickled_candidate_file)

    classified_candidates = {}
    for term_tuple in candidates_dict:
        length = len(term_tuple)
        if str(length) not in classified_candidates:
            classified_candidates[str(length)] = {}
        classified_candidates[str(length)][term_tuple] = candidates_dict[term_tuple]

    for length in classified_candidates:
        stat_util = StatisticsUtil(classified_candidates[length])

        frequency_ranked = stat_util.frequency_rank()
        t_score_ranked = stat_util.t_score_rank()
        mi_ranked = stat_util.mi_rank()
        mi_3_ranked = stat_util.mi_3_rank()
        dice_factor_ranked = stat_util.dice_factor_rank()
        c_value_ranked = stat_util.c_value_rank()

        rank_types = ['frequency_ranked', 't_score_ranked', 'mi_ranked', 'mi_3_ranked', 'dice_factor_ranked',
                      'c_value_ranked']

        for type in rank_types:
            data = stat_util.input_ranked_candidates(type)
            result_util = ResultProcessUtil(data)
            norm_data = result_util.norm()
            output_name = length + '_' + 'word' + '_' + type
            FileIOUtil.output_rank_result(norm_data, STAT_FOLDER, PROJECT_NAME, output_name)

#
# if __name__ == '__main__':
#
#     import codecs
#     import re
#     import json
#
#     file_path = os.path.join(OUTPUT_FOLDER, 'Ti_c_value_ranked_candidates_1804261615.txt')
#
#     with codecs.open(file_path, 'r', encoding='utf-8') as f:
#         raw_data = f.readlines()
#
#     data = OrderedDict()
#     count = 0
#
#     for line in raw_data:
#         match = re.match(r'^(.*?):\s+-?([\d.]+)$', line.rstrip())
#         if match:
#             data[match.group(1)] = float(match.group(2))
#         else:
#             print(line)
#
#     print(len(data))
#     data_util = ResultProcessUtil(data)
#     data_util.norm()
#     classified_data = data_util.classify()
#
#     # print(json.dumps(classified_data[2]))
#
#     FileIOUtil.output_dict_to_file(classified_data[4], OUTPUT_FOLDER, PROJECT_NAME, 'len_4_candidate', sort=True, time_tag=False)
#     FileIOUtil.output_dict_to_file(classified_data[5], OUTPUT_FOLDER, PROJECT_NAME, 'len_5_candidate', sort=True, time_tag=False)
#     FileIOUtil.output_dict_to_file(classified_data[6], OUTPUT_FOLDER, PROJECT_NAME, 'len_6_candidate', sort=True, time_tag=False)
#     FileIOUtil.output_dict_to_file(classified_data[7], OUTPUT_FOLDER, PROJECT_NAME, 'len_7_candidate', sort=True, time_tag=False)
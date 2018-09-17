
import os
import codecs
from settings import PROJECT_NAME, TOOL_BASE_FOLDER, MULTI_WORD_TRUE_TERM_FILE, PROJECT_ROOT
from utility import FileIOUtil, PathUtil


class EvaluatUtil(object):

    def __init__(self, winner, loser, term_length):

        # checked_file_name = PROJECT_NAME + '_' + checked_file_name
        self._prepare_data(winner, loser, term_length)

    def _prepare_data(self, winner, loser, term_length):

        def is_positive(layered_tags):
            for tag in layered_tags:
                if int(tag.value) == 1:
                    return True
            return False

        multi_true_terms = FileIOUtil.input_from_json(TOOL_BASE_FOLDER, '', MULTI_WORD_TRUE_TERM_FILE)
        actual_terms = FileIOUtil.input_from_json(
            r'D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Statistic_Result', PROJECT_NAME,
            'actual_term_set')

        # winner_file = checked_file_name + '_winner_checked.txt'
        # loser_file = checked_file_name + '_loser_checked.txt'
        # source_folder = PathUtil.get_latest_folder(PROJECT_ROOT, '180428', 1)
        # source_folder = os.path.join(source_folder, 'Statistic_Result')
        # winner_path = os.path.join(source_folder, winner_file)
        # loser_path = os.path.join(source_folder, loser_file)

        self.true_positive = {}
        self.true_negative = {}
        self.false_negative = {}
        self.false_positive = {}
        self.new_found = {}

        for term, value in winner.items():
            if term in actual_terms[str(term_length)]:
                self.true_positive[term] = value
                if term not in multi_true_terms:
                    self.new_found[term] = value
            else:
                self.false_positive[term] = value
        for term, value in loser.items():
            if term in actual_terms[str(term_length)]:
                self.false_negative[term] = value
                if term not in multi_true_terms:
                    self.new_found[term] = value
            else:
                self.true_negative[term] = value

        # winnner_terms = FileIOUtil.input_checked_term_from_excel(r"D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-0252\Statistic_Result", PROJECT_NAME, checked_file_name)
        # # loser_terms = {}
        # for term, values in winnner_terms.items():
        #     if is_positive(values[-4:-1]):
        #         self.true_positive[term] = values[:-1]
        #         if term.value not in multi_true_terms:
        #             self.new_found[term] = values[:-1]
        #     else:
        #         self.false_positive[term] = values[:-1]

        # with open(winner_path, 'r') as f1:
        #     data = {}
        #     lines = f1.readlines()
        #     for line in lines:
        #         line = line.strip().split('\t')
        #         data[line[0]] = line[1:]
        #     for term, values in data.items():
        #         if str(values[-1]) == '0':
        #             self.false_positive[term] = values[:-1]
        #         else:
        #             self.true_positive[term] = values[:-1]
        #             if term not in multi_true_terms:
        #                 self.new_found[term] = values[:-1]
        #
        # with open(loser_path, 'r') as f2:
        #     data = {}
        #     lines = f2.readlines()
        #     for line in lines:
        #         line = line.strip().split('\t')
        #         data[line[0]] = line[1:]
        #     for term, values in data.items():
        #         if values[-1] == '0':
        #             self.true_negative[term] = values[:-1]
        #         else:
        #             self.false_negative[term] = values[:-1]

    def precision_recall(self):

        true_positive = len(self.true_positive.keys())
        false_positive = len(self.false_positive.keys())
        false_negative = len(self.false_negative.keys())

        if true_positive + false_positive == 0:
            precision = 0
        else:
            precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)

        if precision + recall == 0:
            f_score = 0
        else:
            f_score = 2*precision*recall / (precision + recall)

        return precision, recall, f_score

    def discover(self):

        new_found = len(self.new_found.keys())
        found = len(self.true_positive.keys())

        discover_rate = new_found / found

        return discover_rate

if __name__=='__main__':

    # def is_positive(layered_tags):
    #     for tag in layered_tags:
    #         if int(tag.value) == 1:
    #             return True
    #     return False
    #
    # actual_terms = {}
    # for i in range(2, 7):
    #     actual_terms[i] = {}
    #     term_file_name = 'c_value_ranked_'+str(i)+'_word'
    #
    #     term_dic = FileIOUtil.input_checked_term_from_excel(
    #         r"D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-0252\Statistic_Result", PROJECT_NAME,
    #         term_file_name)
    #     for term, values in term_dic.items():
    #         if is_positive(values[-4:-1]):
    #             if term not in actual_terms[i]:
    #                 actual_terms[i][term.value] = ''
    #
    # FileIOUtil.output_to_json(actual_terms,
    #                           r"D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Statistic_Result",
    #                           PROJECT_NAME, 'actual_term_set')

    rank_types = ['frequency_ranked', 't_score_ranked', 'mi_ranked', 'mi_3_ranked', 'dice_factor_ranked',
                  'c_value_ranked']
    for i in range(2, 7):
        precision = {}
        recall = {}
        f_score = {}
        for rank_type in rank_types:
            precision[rank_type] = []
            recall[rank_type] = []
            f_score[rank_type] = []
            file_name = str(i) + '_word_' + rank_type
            term_dict = FileIOUtil.input_rank_result(
                r'D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Statistic_Result', PROJECT_NAME,
                file_name)
            for percent in range(1, 101):
                percent /= 100
                spliter = int(len(term_dict)*percent)
                index = 0
                winner = {}
                loser = {}
                for term, value in term_dict.items():
                    if index < spliter:
                        winner[term] = value
                    else:
                        loser[term] = value
                    index += 1
                eval_util = EvaluatUtil(winner, loser, i)
                p, r, f = eval_util.precision_recall()
                precision[rank_type].append(p)
                recall[rank_type].append(r)
                f_score[rank_type].append(f)

        output_file_1 = str(i) + '_word_precision'
        output_file_2 = str(i) + '_word_recall'
        output_file_3 = str(i) + '_word_f_score'
        FileIOUtil.output_rank_result(precision,
                                      r'D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Analysis',
                                      PROJECT_NAME, output_file_1)
        FileIOUtil.output_rank_result(recall,
                                      r'D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Analysis',
                                      PROJECT_NAME, output_file_2)
        FileIOUtil.output_rank_result(f_score,
                                      r'D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-1118\Analysis',
                                      PROJECT_NAME, output_file_3)

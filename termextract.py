
# coding: utf-8



from data_processing.data_clean import  DataCleanUtil
from settings import *
from data_processing.data_clean import DataCleanUtil
from linguistictools import LinguisticsUtil, do_linguistic_processing
from statistictools import StatisticsUtil, do_statistic_processing, do_statistic_processing_by_length
from evaluation import EvaluatUtil


if __name__ == '__main__':

    # # project_name = 'Ti'            # 'OSCE', 'Ti', 'WFBS'
    # # init_project(project_name)
    #
    output_file_name = 'good_clean_text'

    clean_util = DataCleanUtil()
    clean_util.clean_source_file(output_file_name)

    # ling_util = LinguisticsUtil()
    do_linguistic_processing(output_file_name)

    # stat_util = StatisticsUtil()
    do_statistic_processing()
    # do_statistic_processing_by_length()

    # for i in list(range(2,8)):
    #     result_file = 'c_value_ranked_'+str(i)+'_word'
    #     eval_util = EvaluatUtil(result_file)
    #     eval_list = eval_util.precision_recall()
    #     print(i, 'words evaluate result:')
    #     print('Precision Rate: ', eval_list[0])
    #     print('Recall Rate: ', eval_list[1])
    #     print('F-Score: ', eval_list[2])
    #     new_rate = eval_util.discover()
    #     print('New Found Rate: ', new_rate)
    #     print(' ')
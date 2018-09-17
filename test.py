
import xlrd
import re
#
# path = r'D:\Files\Projects\python\TermExtractor\data_materials\source_file\WFBS.xlsx'
#
# text_list = []
# with xlrd.open_workbook(path) as file:
#
#     table = file.sheet_by_index(0)
#     rows = table.nrows
#     for index in range(rows):
#         text_list.append(table.row_values(index)[0])

CSS_PATTERN = re.compile(r"""
    (?:[.#]?[\w-]+(?:\[.*?\])?)+
    \s*\{\s*
        (?:[\w-]+\s*:.*?;\s*)+
    \}
""", re.VERBOSE)


CSS_PATTERN = re.compile(r"""
    (?:[.#]?[\w-]+(?:\[.*?\])?)+
    (?:(?:\s+|\s*,\s*)(?:[.#]?[\w-]+(?:\[.*?\])?))*
    \s*\{\s*
        (?:[\w-]+\s*:.*?;\s*)+
    \}
""", re.VERBOSE)


s = 'Trend Micro Titanium Maximum Security Installer'


if __name__ == '__main__':
    # import os
    # import json
    # from settings import TOOL_BASE_FOLDER, PROJECT_ROOT, PROJECT_NAME
    #
    # path = os.path.join(PROJECT_ROOT, PROJECT_NAME+'_MULTI_WORD_TRUE_TERM.txt')
    # terms = {}
    # with open(path, 'r', encoding='utf-8') as f1:
    #     lines = f1.readlines()
    #     for line in lines:
    #         if line.strip():
    #             terms[line.strip()] = ''
    # json_path = os.path.join(TOOL_BASE_FOLDER, 'MULTI_WORD_TRUE_TERMS.json')
    # with open(json_path, 'w', encoding='utf-8') as f2:
    #     json.dump(terms, f2)

    from utility import FileIOUtil
    import pickle
    from nltk.tag import PerceptronTagger

    test_set = FileIOUtil.input_train_text_from_file(r'D:\Files\Projects\python\TermExtraction\data_materials\Ti_train_text', 'Ti_Part_1.txt')

    # score = PerceptronTagger().evaluate(test_set)
    path = r'D:\Files\Projects\python\TermExtraction\tool_base\TAG_PICKLED_PerceptronTagger_Based_Brill_Tagger.txt'
    # tagger = FileIOUtil.input_from_pickled_file(r'D:\Files\Projects\python\TermExtraction\tool_base', 'TAG_PICKLED_PerceptronTagger_Based_Brill_Tagger.txt')
    file = open(path, 'rb')
    tagger = pickle.load(file)
    score = tagger.evaluate(test_set)
    print(score)
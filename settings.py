import os
from datetime import datetime

PROJECT_NAME = "Ti"
PROJECT_NAME_LIST = ["OSCE", "Ti", "WFBS"]

ROOT = os.path.dirname(__file__)

if PROJECT_NAME == 'OSCE':
    SOURCE_FILE = r"OSCE_XG_SP1_cht.tmx"
    SOURCE_TRUE_TERMS = r'OSCE12SP1_TM_Termlist_20170817_2.xlsx'
elif PROJECT_NAME == 'Ti':
    SOURCE_FILE = r"Ti12.0_UI_DE_en-US_de-DE.tmx"
    SOURCE_TRUE_TERMS = r"Ti Term List.csv"
    # SOURCE_FILE = "test.tmx"
elif PROJECT_NAME == 'WFBS':
    SOURCE_FILE = r"WFBS.xlsx"
    SOURCE_TRUE_TERMS = r"WFBS_Terminology_(P1,P2,NewWording)_20180403.xlsx"

OUTPUT_ROOT = os.path.join(ROOT, "data_materials")
DATA_SOURCE_FOLDER = os.path.join(OUTPUT_ROOT, 'source_file')
TOOL_BASE_FOLDER = os.path.join(ROOT, "tool_base")
PICKLED_SINGLE_WORD_TRUE_TERM_FILE = r"PICKLED_SINGLE_WORD_TRUE_TERM_DICT"
MULTI_WORD_TRUE_TERM_FILE = r"MULTI_WORD_TRUE_TERMS"

PROJECT_ROOT = os.path.join(OUTPUT_ROOT, PROJECT_NAME)
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, datetime.now().strftime('%y%m%d-%H%M'))
STAT_FOLDER = os.path.join(OUTPUT_FOLDER, 'Statistic_Result')
LING_FOLDER = os.path.join(OUTPUT_FOLDER, 'Linguistic_Result')
CLEAN_FOLDER = os.path.join(OUTPUT_FOLDER, 'Clean_Result')

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)
if not os.path.exists(CLEAN_FOLDER):
    os.mkdir(CLEAN_FOLDER)
if not os.path.exists(LING_FOLDER):
    os.mkdir(LING_FOLDER)
if not os.path.exists(STAT_FOLDER):
    os.mkdir(STAT_FOLDER)

# environment
java_path = r'D:\Code Environment\Java\jdk1.8.0_141\bin\java.exe'
stanford_tagger_model_path = r'./tool_base/stanford-postagger-full-2018-02-27/models/english-bidirectional-distsim.tagger'
stanford_tagger_jar_path = r'./tool_base/stanford-postagger-full-2018-02-27/stanford-postagger.jar'


# def init_project(project_name):
#
#     global PROJECT_NAME
#
#     if project_name in PROJECT_NAME_LIST:
#         PROJECT_NAME = project_name
#     else:
#         raise Exception('Invalid Project Name.')
#
#     define_source_folder()
#     define_target_folder()
#
#
# def define_source_folder():
#
#     global SOURCE_FILE, SOURCE_TRUE_TERMS
#
#     if PROJECT_NAME == 'OSCE':
#         SOURCE_FILE = r"OSCE_XG_SP1_cht.tmx"
#         SOURCE_TRUE_TERMS = r'OSCE12SP1_TM_Termlist_20170817_2.xlsx'
#     elif PROJECT_NAME == 'Ti':
#         SOURCE_FILE = r"Ti12.0_UI_DE_en-US_de-DE.tmx"
#         SOURCE_TRUE_TERMS = r"Ti Term List.csv"
#     elif PROJECT_NAME == 'WFBS':
#         SOURCE_FILE = r"WFBS.xlsx"
#         SOURCE_TRUE_TERMS = r"WFBS_Terminology_(P1,P2,NewWording)_20180403.xlsx"
#
#
# def define_target_folder():
#
#     global OUTPUT_FOLDER, STAT_FOLDER, LING_FOLDER, CLEAN_FOLDER
#
#     project_root = os.path.join(OUTPUT_ROOT, PROJECT_NAME)
#     timedtamps = datetime.now().strftime('%y%m%d-%H%M')
#     OUTPUT_FOLDER = os.path.join(project_root, timedtamps)
#     STAT_FOLDER = os.path.join(OUTPUT_FOLDER, 'Statistic_Result')
#     LING_FOLDER = os.path.join(OUTPUT_FOLDER, 'Linguistic_Result')
#     CLEAN_FOLDER = os.path.join(OUTPUT_FOLDER, 'Clean_Result')
#     # FILTERED_FOLDER = os.path.join(OUTPUT_FOLDER, 'Filtered_Terms')
#
#     if not os.path.exists(OUTPUT_FOLDER):
#         os.mkdir(OUTPUT_FOLDER)
#     if not os.path.exists(CLEAN_FOLDER):
#         os.mkdir(CLEAN_FOLDER)
#     if not os.path.exists(LING_FOLDER):
#         os.mkdir(LING_FOLDER)
#     if not os.path.exists(STAT_FOLDER):
#         os.mkdir(STAT_FOLDER)
#
#
# def redefine_target_folder(project_name, folder=''):
#
#     # if user wanna start processing from linguistic or statistical part
#     # :param project_name: new PROJECT_NAME
#     # :param folder:
#     # :return: None
#
#
#     global PROJECT_NAME, OUTPUT_FOLDER, STAT_FOLDER, LING_FOLDER, CLEAN_FOLDER
#
#     PROJECT_NAME = project_name
#     project_root = os.path.join(OUTPUT_ROOT, PROJECT_NAME)
#     if folder:
#         timedtamps = folder
#     else:
#         folder_list = []
#         for dir_name in os.listdir(project_root):
#             dir_path = os.path.join(project_root, dir_name)
#             if os.path.isdir(dir_path):
#                 folder_list.append(dir_name)
#
#         folder_list = sorted(folder_list, reverse=True)
#         timedtamps = folder_list[0]
#
#     OUTPUT_FOLDER = os.path.join(project_root, timedtamps)
#     STAT_FOLDER = os.path.join(OUTPUT_FOLDER, 'Statistic_Result')
#     LING_FOLDER = os.path.join(OUTPUT_FOLDER, 'Linguistic_Result')
#     CLEAN_FOLDER = os.pathjoin(OUTPUT_FOLDER, 'Clean_Result')
#     # FILTERED_FOLDER = os.path.join(OUTPUT_FOLDER, 'Filtered_Terms')
#
#     if not os.path.exists(CLEAN_FOLDER):
#         os.mkdir(CLEAN_FOLDER)
#     if not os.path.exists(LING_FOLDER):
#         os.mkdir(LING_FOLDER)
#     if not os.path.exists(STAT_FOLDER):
#         os.mkdir(STAT_FOLDER)
#

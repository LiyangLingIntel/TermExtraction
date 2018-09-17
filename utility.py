
import os
import pickle
import json
import xlwt, xlrd
from datetime import datetime
from settings import TOOL_BASE_FOLDER
from collections import OrderedDict
from nltk.corpus import stopwords


class FileIOUtil(object):

    @staticmethod
    def output_list_to_file(text_list, folder, project_name, target_file_name, time_tag=False):
        """
        :param text_list:  list of text or terms
        :param folder: str, output folder path
        :param project_name: str
        :param target_file_name: str, without postfix
        :param eras: bool, truncate file before writing
        :param time_tag: bool, add timestamp at the end of file name
        :return: none, output list of text to path: folder + project_name_target_file_name.txt
        """
        assert not target_file_name.endswith('.txt')    # target_file_name must be without postfix
        if isinstance(text_list, str):
            text_list = [text_list]

        text_str = ''
        for text_line in text_list:
            text_str += str(text_line) + '\n'
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        if time_tag:
            eras = False
            target_path = os.path.join(folder, project_name + '_' + target_file_name + '_' + timestamp + '.txt')
        else:
            eras = True
            target_path = os.path.join(folder, project_name + '_' + target_file_name + '.txt')
        with open(target_path, 'w', encoding='utf-8') as target_file:
            if eras:
                target_file.seek(0)
                target_file.truncate()
            target_file.write(text_str)

    @staticmethod
    def output_dict_to_file(text_dict, folder, project_name, target_file_name, sort=True, time_tag=False):
        """
        :param text_dict:
        :param folder: output folder path
        :param project_name:
        :param target_file_name: without postfix
        :param eras: bool, truncate file before writing
        :param time_tag: bool, add timestamp at the end of file name
        :param sort: bool, sort dict or not
        :return: none
        """
        assert not target_file_name.endswith('.txt')

        if sort:
            text_dict = sorted(text_dict.items(), key=lambda x: x[1], reverse=True)
        else:
            text_dict = list(text_dict.items())

        text_str = ''
        for item in text_dict:
            text_str += str(item[0]) + ': ' + str(item[1]) + '\n'

        timestamp = datetime.now().strftime('%y%m%d%H%M')
        if time_tag:
            eras = False
            target_path = os.path.join(folder, project_name + '_' + target_file_name + '_' +timestamp + '.txt')
        else:
            eras = True
            target_path = os.path.join(folder, project_name + '_' + target_file_name + '.txt')
        with open(target_path, 'w', encoding='utf-8') as target_file:
            if eras:
                target_file.seek(0)
                target_file.truncate()
            target_file.write(text_str)

    @staticmethod
    def output_to_json(list_or_dict, folder, project_name, target_file_name):

        if project_name:
            path = os.path.join(folder, project_name+'_'+target_file_name+'.json')
        else:
            path = os.path.join(folder, target_file_name+'.json')

        with open(path, 'w') as f:
            json.dump(list_or_dict, f)

    @staticmethod
    def output_to_pickled_file(obj, folder, project_name, target_file_name):

        if project_name:
            path = os.path.join(folder, project_name+'_'+target_file_name+'.txt')
        else:
            path = os.path.join(folder, target_file_name+'.txt')

        with open(path, 'wb') as f:
            pickle.dump(obj, f)

    @staticmethod
    def input_train_text_from_file(folder_name, source_file_name):

        source_path = os.path.join(folder_name, source_file_name)
        with open(source_path, 'r', encoding='utf-8') as source_file:

            lines = source_file.readlines()
            row_num = len(lines)
            index = 0

            tagged_sents = []
            while index < row_num-1:

                sent_str = lines[index+1].strip()
                tag_str = lines[index+2].strip()
                index += 4
                sent_str_pieces = sent_str[1:-1].split(', ')
                tag_str_pieces = tag_str[1:-1].split(', ')

                sent_list = []
                for piece in sent_str_pieces:
                    sent_list.append(piece[1:-1])

                tag_list = []
                for piece in tag_str_pieces:
                    tag_list.append(piece[1:-1])

                tagged_sent = list(zip(sent_list, tag_list))
                tagged_sents.append(tagged_sent)

            return tagged_sents

    @staticmethod
    def input_test_text_from_file(folder_name, source_file_name):

        source_path = os.path.join(folder_name, source_file_name)
        with open(source_path, 'r', encoding='utf-8') as source_file:

            lines = source_file.readlines()
            row_num = len(lines)
            index = 0

            tagged_sents = []
            while index < row_num-1:

                sent = lines[index].strip()
                index += 4
                tagged_sents.append(sent)

            return tagged_sents

    @staticmethod
    def input_from_json(folder, project_name, source_file_name):

        if project_name:
            path = os.path.join(folder, project_name+'_'+source_file_name+'.json')
        else:
            path = os.path.join(folder, source_file_name+'.json')

        if not os.path.exists(path):
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            list_or_dict = json.load(f)
            return list_or_dict

    @staticmethod
    def input_from_pickled_file(folder, project_name, source_file_name):

        if project_name:
            path = os.path.join(folder, project_name+'_'+source_file_name+'.txt')
        else:
            path = os.path.join(folder, source_file_name+'.txt')

        with open(path, 'rb') as f:
            obj = pickle.load(f)
            return obj

    @staticmethod
    def output_bio_tagged_sents(sents, bio_tagged_sents, folder, projec_name, target_file_name):

        output_content = []
        for i in range(len(bio_tagged_sents)):
            output_str = sents[i] + '\n'
            tokens, tags, bios = zip(*bio_tagged_sents[i])
            output_str += str(tokens) + '\n'
            output_str += str(tags) + '\n'
            output_str += str(bios) + '\n'
            output_content.append(output_str)
        FileIOUtil.output_list_to_file(output_content, folder, projec_name, target_file_name, time_tag=False)

    @staticmethod
    def output_rank_result(ranked_result, folder, project_name, target_file_name):

        path = os.path.join(folder, project_name + '_' + target_file_name + '.txt')
        content = ''
        for term,values in ranked_result.items():
            content += term
            if isinstance(values, list):
                for value in values:
                    content += '\t' + str(value)
                content += '\n'
            else:
                content += '\t' + str(values) + '\n'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def input_text_from_file(folder, project_name, source_file_name):

        source_path = os.path.join(folder, project_name+'_'+source_file_name+'.txt')
        source_file = open(source_path, 'r', encoding='utf-8')
        text = source_file.readlines()

        return text

    @staticmethod
    def input_rank_result(folder, project_name, source_file_name):

        path = os.path.join(folder, project_name + '_' + source_file_name + '.txt')
        contents = []
        lines = open(path, 'r', encoding='utf-8').readlines()
        for line in lines:
            contents.append(line.split('\t'))

        checked_candidates = OrderedDict()
        for item in contents:
            checked_candidates[item[0]] = item[1:]

        return checked_candidates

    @staticmethod
    def input_checked_term_from_excel(folder, project_name, source_file_name):

        checked_term = OrderedDict()
        source_path = os.path.join(folder, project_name+'_'+source_file_name+'.xlsx')
        # with open(source_path, 'r', encoding='utf-8') as source_file:
        table = xlrd.open_workbook(source_path).sheet_by_index(0)
        row_number = table.nrows
        for i in range(row_number):
            list = table.row(i)
            checked_term[list[0]] = list[1:]

        return checked_term


class StopWordsUtil(object):
    """
    Actually stoplist is dict of stop word, the words are dict.keys
    """

    def __init__(self):
        self.path = os.path.join(TOOL_BASE_FOLDER, 'STOPWORDS.json')

    def get_stopwords(self):

        if os.path.exists(self.path):
            with open(self.path, 'r') as json_file:
                stopwords = json.load(json_file)
        else:
            stopwords = {}
        return stopwords

    def modify_stopwords(self, append_list=[], delete_list=[]):

        if isinstance(append_list, str):
            append_list = [append_list]
        if isinstance(delete_list, str):
            delete_list = [delete_list]

        stopwords = self.get_stopwords()

        for word in append_list:
            if word not in stopwords:
                stopwords[word] = ''
        for word in delete_list:
            stopwords.pop(word, '')

        with open(self.path, 'w') as json_file:
            json.dump(stopwords, json_file)


class PathUtil(object):

    @staticmethod
    def get_latest_folder(root_path, folder_name, latest_number=0):

        folder_list = []
        for dir_name in os.listdir(root_path):
            if folder_name and not dir_name.startswith(folder_name):
                continue
            dir_path = os.path.join(root_path, dir_name)
            if os.path.isdir(dir_path):
                folder_list.append(dir_name)

        folder_list = sorted(folder_list, reverse=True)
        if latest_number < len(folder_list)-1:
            latest_folder_name = folder_list[latest_number]
        else:
            raise Exception('Invalid latest_number')

        latest_folder_path = os.path.join(root_path, latest_folder_name)

        return latest_folder_path

    @staticmethod
    def get_latest_file_name(root_path, file_name, latest_number=0):

        file_list = []
        for file in os.listdir(root_path):

            if not file.startswith(file_name):
                continue

            file_path = os.path.join(root_path, file)
            if os.path.isfile(file_path):
                file_list.append(file)

        file_list = sorted(file_list, reverse=True)
        if latest_number < len(file_list) - 1:
            latest_folder_name = file_list[0]
        else:
            raise Exception('Invalid latest_number')

        return latest_folder_name


if __name__ == '__main__':

    # folder = r'D:\Files\Projects\python\TermExtraction\data_materials\Ti_train_text'
    # source_file_name = r'Ti_Part_6.txt'
    #
    # tagged_sent = FileIOUtil.input_train_text_from_file(folder, source_file_name)

    # stoplist = stopwords.words('english')
    # additional_list = ['UTC']
    # except_list = ['of']
    # stoplist.extend(additional_list)
    #
    # StopWordsUtil().modify_stopwords(stoplist, except_list)

    path = FileIOUtil.input_checked_term_from_excel(r"D:\Files\Projects\python\TermExtraction\data_materials\Ti\180428-0252\Statistic_Result", 'Ti', 'c_value_ranked_4_word')
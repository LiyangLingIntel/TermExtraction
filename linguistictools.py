
# coding: utf-8

import nltk
import os
import re
import pickle
from datetime import datetime
from settings import PROJECT_NAME, PICKLED_SINGLE_WORD_TRUE_TERM_FILE, TOOL_BASE_FOLDER, CLEAN_FOLDER, LING_FOLDER
from settings import stanford_tagger_jar_path, stanford_tagger_model_path, java_path
from utility import FileIOUtil, PathUtil, StopWordsUtil
from nltk.tag import brill, brill_trainer
from nltk.tag.stanford import CoreNLPPOSTagger, StanfordPOSTagger


class LinguisticsUtil(object):

    regex_grammar = r"""
        NP: {<JJ>?<NNP>+}
            {<NN.?>+<CC|IN><NN.?>+}
            {<JJ>?<NN.?>+<VBG|VBN|VBD|RB>?<NN.?>*(\(<CD|NN.?>\))?}
            {<JJ>}
        VP: {<VBG|VBN|VBD><JJ>?<NN.?>+}
            {<VB|VBN|VBG>}
    """

    # def _is_contained_illegal_dot(self, tokens):
    #     """
    #     check whether word_tokenized sentence has expression like 'out.Select' or not
    #     :param sent: word_tokenized sentence
    #     :return: bool,  True if yes, False if cannot find expression described above
    #     """
    #     tokens = tokens[:-1]
    #     for word in tokens:
    #         if len(word)>1 and '.' in word.rstrip('.'):
    #             return True
    #     return False

    def default_corpus_tagger(self, text):
        """
        :param text: raw corpus
        :return: list of tagged sentence, BIO tagged corpus
        """
        sent_tokens = nltk.tokenize.sent_tokenize(text)
        lines_tokens = []
        for sent in sent_tokens:
            word_tokens = nltk.tokenize.word_tokenize(sent)
            lines_tokens.append(word_tokens)
        tags = []
        for line_tokens in lines_tokens:
            tagged_sentence = nltk.pos_tag(line_tokens)
            tags.append(tagged_sentence)

        regex_parser = nltk.RegexpParser(self.regex_grammar)
        chunked_sent_list = []
        for tagged in tags:
            chunked_tree = regex_parser.parse(tagged)
            chunked_bio_tagged = nltk.chunk.tree2conlltags(chunked_tree)
            chunked_sent_list.append(chunked_bio_tagged)

        return sent_tokens, chunked_sent_list
        # return sent_tokens, tags

    def _get_pos_tagger(self, tagger_name='pos_tagger'):
        """
        :param tagger_name:
        :return: 'pos_tagger', 'stanford_pos_tagger', 'core_nlp_pos_tagger', custom tagger_name, above 4 are supported
        """
        if tagger_name == 'pos_tagger':
            tagger = nltk.tag.PerceptronTagger()
        elif tagger_name == 'stanford_tagger':
            os.environ['JAVAHOME'] = java_path
            tagger = StanfordPOSTagger(stanford_tagger_model_path, stanford_tagger_jar_path)
        else:
            tagger = TaggerUtil.load_tagger_model(tagger_name)

        return tagger

    def _pos_tag(self, tokenized_sents, tagger):

        ret = []
        count = 0
        for sent in tokenized_sents:
            tagged_sent = tagger.tag(sent)
            ret.append(tagged_sent)
            print(count)
            count += 1

        return ret

    def _get_chunk_parser(self, parser_name='regex_parser'):
        """
        :param parser_name: 'regex_parser', custom parser_name
        :return: chunk_parser obj
        """
        if parser_name == 'regex_parser':
            parser = nltk.RegexpParser(self.regex_grammar)
        else:                                                 # custom parser
            assert type(parser_name) is str
            parser = ChunkerUtil.load_chunker_model(parser_name)

        return parser

    def _get_bio_chunk(self, tagged_sents, chunk_parser):

        chunked_set = []
        count = 0
        for tagged in tagged_sents:
            chunked_tree = chunk_parser.parse(tagged)
            chunked_bio_tagged = nltk.chunk.tree2conlltags(chunked_tree)
            chunked_set.append(chunked_bio_tagged)
            print(count)
            count += 1

        return chunked_set
    
    def _split_dot(self, word):
        if word.count('.') == 1:
            left, right = word.split('.')
            if re.match(r'\w*[")]*', left) and re.match(r'[A-Z]\w*', right):
                return [left + '.', right]
        return [word]

    def _sent_post_process(self, sents):
        ret = []
        for sent in sents:
            if re.search(r'\s+\w+\.[A-Z]\w*(?:\s+|$)', sent):
                words = []
                for word in sent.split():
                    words.extend(self._split_dot(word))
                temp = nltk.sent_tokenize(' '.join(words))
                ret.extend(temp)
            else:
                ret.append(sent)
        return ret

    def _sent_tokenize(self, text_line_list):

        ret = []
        count = 0
        for line in text_line_list:
            sents = nltk.tokenize.sent_tokenize(line.strip())
            sents = self._sent_post_process(sents)
            ret.extend(sents)
            print(count)
            count += 1

        return ret

    def _word_tokenize(self, sents):

        ret = []
        for sent in sents:
            words = nltk.tokenize.word_tokenize(sent)
            ret.append(words)

        return ret

    def customized_corpus_tagger(self, text_list, tagger_name='pos_tagger', chunker_name='regex_parser'):

        tagger = self._get_pos_tagger(tagger_name)
        chunker = self._get_chunk_parser(chunker_name)

        sents = self._sent_tokenize(text_list)
        tokenized_sents = self._word_tokenize(sents)
        tagged_sents = self._pos_tag(tokenized_sents, tagger)
        chunked_sents = self._get_bio_chunk(tagged_sents, chunker)

        # return sent_tokens, chunked_sents
        return sents, chunked_sents

    def candidate_term_extractor(self, bio_tagged_sents):

        ret = []
        for bio_tagged_sent in bio_tagged_sents:

            candidate_term = []
            for word, tag, bio in bio_tagged_sent:
                if bio.startswith('B'):
                    if candidate_term:  # B, I, I, B: the second B should be treated as next chunk beginning
                        ret.append(tuple(candidate_term))
                        candidate_term = []
                    candidate_term.append(word)
                    continue
                elif bio.startswith('I'):
                    candidate_term.append(word)
                    continue
                elif bio.startswith('O'):
                    if candidate_term:
                        ret.append(tuple(candidate_term))
                    candidate_term = []

        return ret

    def single_word_filter(self, candidate_list):
        single_word_term = {}
        multi_word_term = {}
        # pickled_single_word_true_term_path = os.path.join(TOOL_BASE_FOLDER, PICKLED_SINGLE_WORD_TRUE_TERM_FILE)
        # with open(pickled_single_word_true_term_path, 'rb+') as pickled_file:
        #     single_word_true_term_dict = pickle.load(pickled_file)
        single_word_true_term_dict = FileIOUtil.input_from_pickled_file(TOOL_BASE_FOLDER, '', PICKLED_SINGLE_WORD_TRUE_TERM_FILE)

        for term_tuple in candidate_list:
            if len(term_tuple) == 1:
                # only single-word candidate can be found in single_word_true_term_dict
                if term_tuple[0] in single_word_true_term_dict:
                    if term_tuple not in single_word_term:
                        single_word_term[term_tuple] = 0
                    single_word_term[term_tuple] += 1
            else:
                if term_tuple not in multi_word_term:
                    multi_word_term[term_tuple] = 0
                multi_word_term[term_tuple] += 1

        return single_word_term, multi_word_term

    def stopwords_filter(self, candidate_dict):

        stopwords = StopWordsUtil().get_stopwords()

        eliminated_candidates = {}
        for candidate in list(candidate_dict.keys()):
            for word in candidate:
                if word in stopwords:
                    eliminated_candidates[candidate] = candidate_dict.pop(candidate)
                    break

        FileIOUtil.output_dict_to_file(eliminated_candidates, LING_FOLDER, PROJECT_NAME, 'StopWords_filter_failures')

        return candidate_dict

    def re_tagger(self, multi_word_candidates, tagger_name='PerceptronTagger_Based_Brill_Tagger', chunker_name='regex_parser'):

        tagger = self._get_pos_tagger(tagger_name)
        chunker = self._get_chunk_parser(chunker_name)

        # tokenized_sents = self._word_tokenize(multi_word_candidates)
        tagged_sents = self._pos_tag(multi_word_candidates, tagger)
        chunked_sents = self._get_bio_chunk(tagged_sents, chunker)

        return chunked_sents

    def output_cadidates(self, single_word_candidates, multi_word_candidates):

        FileIOUtil.output_dict_to_file(single_word_candidates, LING_FOLDER, PROJECT_NAME, 'candidate_single_word', sort=True,
                            time_tag=False)
        FileIOUtil.output_dict_to_file(multi_word_candidates, LING_FOLDER, PROJECT_NAME, 'candidate_multi_word', sort=True,
                            time_tag=False)
        FileIOUtil.output_to_pickled_file(multi_word_candidates, LING_FOLDER, PROJECT_NAME, 'PICKLED_multi_word_candidate')


class TaggerUtil(object):

    @staticmethod
    def persistenize_tagger_model(tagger_model, tagger_name):

        tagger_pickled_path = os.path.join(TOOL_BASE_FOLDER, 'TAG_PICKLED_'+tagger_name+'.txt')
        with open(tagger_pickled_path, 'wb') as pickled_file:
            pickle.dump(tagger_model, pickled_file)

    @staticmethod
    def load_tagger_model(tagger_name='Brill_Tagger'):

        tagger_pickled_path = os.path.join(TOOL_BASE_FOLDER, 'TAG_PICKLED_'+tagger_name+'.txt')
        if not os.path.exists(tagger_pickled_path):
            raise Exception('Pickled tagger does not exist.')

        with open(tagger_pickled_path, 'rb') as pickled_file:
            tagger_model = pickle.load(pickled_file)
            return tagger_model

    @staticmethod
    def customize_tagger(train_sets, test_sets = None, tagger_name='Brill_Tagger', return_tagger=False):
        """
        use train set to train customized tagger
        :param tagger_name:
        :param train_sets:
        :param test_sets:
        :return: trained tagger's score
        """
        tagger = nltk.DefaultTagger('NN')
        tagger = nltk.UnigramTagger(train_sets, backoff=tagger)
        tagger = nltk.BigramTagger(train_sets, backoff=tagger)

        # tagger = nltk.tag.PerceptronTagger()
        #
        # os.environ['JAVAHOME'] = java_path
        # tagger = StanfordPOSTagger(stanford_tagger_model_path, stanford_tagger_jar_path)

        templates = brill.fntbl37()
        brill_tagger = brill_trainer.BrillTaggerTrainer(tagger, templates, trace=3)
        brill_tagger = brill_tagger.train(train_sets, max_rules=300)

        # TaggerUtil.persistenize_tagger_model(tagger, 'Multigram_Tagger')
        TaggerUtil.persistenize_tagger_model(brill_tagger, tagger_name)

        score = -1
        if test_sets:
            score = brill_tagger.evaluate(test_sets)

        if return_tagger:
            return score, brill_tagger
        else:
            return score


class ChunkerUtil(object):

    @staticmethod
    def persistenize_chunker_model(chunker_model, chunker_name):

        tagger_pickled_path = os.path.join(TOOL_BASE_FOLDER, 'CHUNK_PICKLED_'+chunker_name+'.txt')
        with open(tagger_pickled_path, 'wb') as pickled_file:
            pickle.dump(chunker_model, pickled_file)

    @staticmethod
    def load_chunker_model(chunker_name):

        chunker_pickled_path = os.path.join(TOOL_BASE_FOLDER, 'CHUNK_PICKLED_'+chunker_name+'.txt')
        if not os.path.exists(chunker_pickled_path):
            raise Exception('Pickled chunker does not exist.')

        with open(chunker_pickled_path, 'rb') as pickled_file:
            chunker_model = pickle.load(pickled_file)
            return chunker_model

    @staticmethod
    def customize_chunker(train_sets, test_sets = None, chunker_name=''):
        pass


def do_linguistic_processing(source_file_name):

    text = FileIOUtil.input_text_from_file(CLEAN_FOLDER, PROJECT_NAME, source_file_name)
    ling_util = LinguisticsUtil()
    # sents, bio_tagged_sents = ling_util.customized_corpus_tagger(text,
    #                                                              tagger_name='PerceptronTagger_Based_Brill_Tagger')
    sents, bio_tagged_sents = ling_util.customized_corpus_tagger(text, tagger_name='model_a')
    # out
    FileIOUtil.output_bio_tagged_sents(sents, bio_tagged_sents, LING_FOLDER, PROJECT_NAME, 'bio_tagged_sents')
    term_list = ling_util.candidate_term_extractor(bio_tagged_sents)
    single_word_term, multi_word_term = ling_util.single_word_filter(term_list)
    multi_word_term = ling_util.stopwords_filter(multi_word_term)
    ling_util.output_cadidates(single_word_term, multi_word_term)

    # multi_word_candidates = FileIOUtil.input_from_pickled_file(LING_FOLDER, PROJECT_NAME, 'PICKLED_multi_word_candidate')
    # re_chunked_candidates = ling_util.re_tagger(multi_word_candidates.keys())
    # re_extracted_candidates = ling_util.candidate_term_extractor(re_chunked_candidates)
    # re_single_word_candidates, re_multi_word_candidates = ling_util.single_word_filter(re_extracted_candidates)
    #
    # FileIOUtil.output_dict_to_file(multi_word_candidates, LING_FOLDER, PROJECT_NAME, '_last_tagged_set', time_tag=False, sort=True)
    # FileIOUtil.output_dict_to_file(re_multi_word_candidates, LING_FOLDER, PROJECT_NAME, '_curr_tagged_set', time_tag=False,
    #                     sort=True)


if __name__ == '__main__':

    source_file_name = PROJECT_NAME + '_good_cleaned_text.txt'
    # source_file_name = PathUtil.get_latest_file()

    # do_linguistic_processing(source_file_name)

    # text = ['hard drive space available.']
    # lin_util = LinguisticsUtil()
    # lin_util.customized_corpus_tagger(text)

    folder_name = r'D:\Files\Projects\python\TermExtraction\data_materials\Ti_train_text'
    tagger_util = TaggerUtil()
    train_set = FileIOUtil.input_train_text_from_file(folder_name, r'train_text.txt')
    test_set_1 = FileIOUtil.input_train_text_from_file(folder_name, r'Ti_Part_1.txt')
    test_set_2 = FileIOUtil.input_train_text_from_file(folder_name, r'Ti_Part_2_David.txt')
    test_set_3 = FileIOUtil.input_train_text_from_file(folder_name, r'Ti_Part_3.txt')
    test_set_5 = FileIOUtil.input_train_text_from_file(folder_name, r'Ti_Part_5_Vera.txt')
    test_set_6 = FileIOUtil.input_train_text_from_file(folder_name, r'Ti_Part_6.txt')
    import time
    start_time = time.time()
    precise_1, tagger = tagger_util.customize_tagger(train_set, test_set_1, tagger_name='model_a', return_tagger=True)
    precise_2 = tagger.evaluate(test_set_2)
    precise_3 = tagger.evaluate(test_set_3)
    precise_5 = tagger.evaluate(test_set_5)
    precise_6 = tagger.evaluate(test_set_6)
    precise_total = tagger.evaluate(train_set)
    end_time = time.time()

    delta = end_time-start_time
    print("precise 1:", precise_1)
    print("precise 2:", precise_2)
    print("precise 3:", precise_3)
    print("precise 4:", precise_5)
    print("precise 5:", precise_6)
    print("precise t:", precise_total)
    print("time_cost:", delta)


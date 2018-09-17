import re
import os
import xlrd
from lxml import etree
from settings import DATA_SOURCE_FOLDER, PROJECT_NAME, SOURCE_FILE, OUTPUT_FOLDER, CLEAN_FOLDER
from data_processing.stringscan import StringScanner, StringProcessor
from utility import FileIOUtil


ENTITY = re.compile(r"&(lt|gt|nbsp|amp|quot|apos|trade|copy);", re.S)
TAG = re.compile(r'<[^>]+>')
SEG = re.compile(r'^\s*<seg>\)?(.*?)</seg>\s*$')

starttag = re.compile(r"""
      <[a-zA-Z_][-.a-zA-Z0-9:_]*          # tag name
      (?:\s+                             # whitespace before attribute name
         (?:<!--.*?-->|\[%\s+\w+.*?%\]|
            (?:[-:a-zA-Z_%@$!#&*~][-.:a-zA-Z0-9_%@$!#&*~]*     # attribute name
              (?:\s*=                                                # value indicator
                (?:\s*\\?'(?:\[%\s+.*?%\]|[^'])*\\?'                   # LITA-enclosed value
                  |\s*\\?"(?:\[%\s+.*?%\]|[^"])*\\?"                # LIT-enclosed value
                  |(?:\s*<!--.*?-->|[^>\s])+                # bare value
                 )?
               )?
             )
          )
       )*
      \s*/?\s*>                                # trailing whitespace
    """, re.VERBOSE)
endtag = re.compile(r'<\\?/\s*([a-zA-Z_][-.a-zA-Z0-9:_]*)\s*>')

HALF_TAG_PATTERN = re.compile(r"""
    <[a-zA-Z_][-.a-zA-Z0-9:_]*          # tag name
    (?:\s+                             # whitespace before attribute name
        (?:
            [-:a-zA-Z_%@$!#&*~][-.:a-zA-Z0-9_%@$!#&*~]*     # attribute name
            (?:\s*=                     # value indicator
                (?:\s*\\?'(?:\[%\s+.*?%\]|[^'])*(?:\\?'|$)                   # LITA-enclosed value
                |\s*\\?"(?:\[%\s+.*?%\]|[^"])*(?:\\?"|$)                 # LIT-enclosed value
                |(?:\s*<!--.*?-->|[^>\s])+                # bare value
                )?
            )?
        )
    )*
    \s*$                                # trailing whitespace
""", re.VERBOSE)

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?(?:-->|$)")

attr = '{http://www.w3.org/XML/1998/namespace}lang'


class DataCleanUtil(object):

    def _bracket_regex(self, text):
        return r'\[?(' + text + r')\]?'

    def _unescape(self, data):

        data = data.replace("&lt;", "<")
        data = data.replace("&gt;", ">")
        data = data.replace("&nbsp;", "")
        data = data.replace("&quot;", '"')
        data = data.replace("&apos;", "'")
        data = data.replace("&trade;", "™")
        data = data.replace("&copy;", "©")
        return data.replace("&amp;", "&")

    def _strip_seg(self, text):

        match = SEG.match(text)
        if match:
            return match.group(1)

    def _get_seg_text(self, seg):
        """
        There may be sub-nodes inside <seg>, e.g. <ph>
        :param seg: XML Node
        :return:
        """
        text = etree.tostring(seg, encoding='utf-8')
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        text = self._strip_seg(text)
        if isinstance(text, str) and text:
            return text.strip()
        else:
            return

    def _clean_html_tag(self, text):

        clean_text = re.sub(self._bracket_regex(r'<ut[^>]*/\s*>|<ut.*?/ut>'), '', text)
        clean_text = re.sub(self._bracket_regex(r'<bpt[^>]*/\s*>|<bpt.*?/bpt>'), '', clean_text)
        clean_text = re.sub(self._bracket_regex(r'<ept[^>]*/\s*>|<ept.*?/ept>'), '', clean_text)
        clean_text = re.sub(self._bracket_regex(r'<ph[^>]*/\s*>|<ph.*?/ph>'), '', clean_text)
        clean_text = re.sub(self._bracket_regex(r'<it[^>]*/\s*>|<it.*?/it>'), '', clean_text)

        while ENTITY.search(clean_text):
            clean_text = self._unescape(clean_text)

        clean_text = starttag.sub('', clean_text)
        clean_text = endtag.sub('', clean_text)
        clean_text = HALF_TAG_PATTERN.sub('', clean_text)
        clean_text = HTML_COMMENT_PATTERN.sub('', clean_text)

        return clean_text

    def _clean_meaningless_symbol(self, text):

        text = re.sub(r'\\+n?r?', ' ', text)
        text = text.replace('|', ', ')    # use ',' to split phrase block, default chunker cannot recognize '|' as spliter
        text = re.sub(r'{[&\\]{0,2}[A-Za-z0-9_]*?}', '', text)
        text = re.sub(r'[@#\$%\-_~\!\*\^\?]{2,}', '', text)
        text = re.sub(r'={2,}', '', text)
        return text

    def _get_text_from_excel(self, source_path):

        text_list = []
        with xlrd.open_workbook(source_path) as file:
            table = file.sheet_by_index(0)
            text_list.extend(table.col_values(0))

        return text_list

    def _get_text_from_tmx(self, source_path):

        tree = etree.parse(source_path)
        text_list = []

        for tu in tree.iterfind(".//tu"):
            en_text = ''
            l10n_text = ''
            for tuv in tu.iterfind(".//tuv"):
                seg = tuv.find('seg')
                if tuv.get(attr) == 'en-US' or tuv.get(attr) == 'EN-US':
                    en_text = self._get_seg_text(seg)
                    text_list.append(en_text)

        print('result extract text:', len(text_list))
        return text_list

    def filter_valid_text(self, text_list):
        """
        filter url, css, js, file/path, invalid data, date format from text
        :param text_list: text_list
        :return: good_list & bad_list
        """
        str_scanner = StringScanner()

        good_text = []
        bad_text = []
        count = 0
        for cleaned_line in text_list:

            if not isinstance(cleaned_line, str):
                cleaned_line = str(cleaned_line)
            if str_scanner.scan_string(cleaned_line):
                good_text.append(cleaned_line)
            else:
                bad_text.append(cleaned_line)
            count += 1
            print(count)

        scan_func = (
            'is_url', 'is_file_or_path', 'is_date_format', 'is_invalid_data', 'is_CJK', 'is_CSS', 'is_JavaScript',
            'is_locale')
        for func in scan_func:
            print(func, getattr(str_scanner, func+'_num'))
        print('result valid text:', len(good_text))
        print('result invalid text:', len(bad_text))
        return good_text, bad_text

    def clean_html(self, source_text):

        en_str = []

        if isinstance(source_text, str):
            source_text = [source_text]

        count = 0
        for text_line in source_text:
            count += 1
            if text_line:
                text_line = self._clean_html_tag(str(text_line))

                if text_line.strip():
                    text_line = text_line.strip()
                    en_str.append(text_line)
            print(count)

        print('result clean_html:', len(en_str))
        return en_str

    def clean_symbol(self, source_text):

        clean_text = []
        count = 0
        for good_line in source_text:
            text = self._clean_meaningless_symbol(good_line).strip()
            if text:
                clean_text.append(text)
            count += 1
            print(count)

        good_cleaned_text = StringProcessor().replace_var_with_sym(clean_text)  # replace variable and '\\' in text with symbol

        return good_cleaned_text

    def clean_source_file(self, output_file_name='good_cleaned_text'):
        """
        :param output_file_name: target_file_name without postfix
        :return: none
        """
        source_path = os.path.join(DATA_SOURCE_FOLDER, SOURCE_FILE)

        raw_data = []
        if source_path.endswith('.tmx'):
            raw_data = self._get_text_from_tmx(source_path)
        elif source_path.endswith(('.xlsx', 'xls')):
            raw_data = self._get_text_from_excel(source_path)

        # FileIOUtil.output_list_to_file(raw_data, r'D:\Files\Projects\python\TermExtraction\temp', 'OSCE', 'raw_data', time_tag=False)

        cleaned_en_data = self.clean_html(raw_data)      # clean html tag
        print('en data html tags have been cleaned')
        good_text, bad_text = self.filter_valid_text(cleaned_en_data)    # do string scanning and filter
        print('cleaned en data have been scanned')

        FileIOUtil.output_list_to_file(bad_text, CLEAN_FOLDER, PROJECT_NAME, 'bad_cleaned_text', time_tag=False)
        del bad_text

        good_cleaned_text = self.clean_symbol(good_text)        # clean meaningless symbol and replace variable
        print('result good clean text:', len(good_cleaned_text))
        FileIOUtil.output_list_to_file(good_cleaned_text, CLEAN_FOLDER, PROJECT_NAME, output_file_name, time_tag=False)


if __name__ == '__main__':

    data_clean_util = DataCleanUtil()
    data_clean_util.clean_source_file('good_cleaned_text')







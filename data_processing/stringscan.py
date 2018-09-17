# coding:utf-8

import re
from data_processing.langabbr import abbr

scheme_compiler = re.compile(r"(?:http|ftp|https)://")
ip4_compiler = re.compile(
    r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))")

file_compiler = re.compile(r".+\.\w+$")
win_path_compiler = re.compile(r"[a-zA-Z]:[\\/]")
linux_path_compiler = re.compile(r"(?:/[^/]+)+")

CJK_SCOPE = [
    (int('4E00', 16), int('9FA5', 16)),
    (int('2E80', 16), int('A4CF', 16)),
    (int('F900', 16), int('FAFF', 16)),
    (int('FE30', 16), int('FE4F', 16)),
]

CSS_PATTERN = re.compile(r"""
    [.#]?[\w-]+(\[.*?\])?
    \s*\{\s*
        (?:[\w-]+\s*:.*?;\s*)+
    \}
""", re.VERBOSE)

CSS_COMMENT = re.compile(r"/\*(.|\n)*?\*/|//.*?(\n|\\n)")

JS_CORE_PATTERN = re.compile(r"""
    (?:^|\s+)var\s+\w+\s*= |
    (?:^|\s+)(?:if|for|function)\s*\(.*?\)\s*\{ |
    (?:^|\s+)[\w.\[\]"]+\.\w+[\[(] |
    (?:^|\s+)else\s*(?:if)?\s*\{ |
    \btypeof\b
""", re.VERBOSE)

# FP:
# URL, e.g. ?TARGET=Portal&FUNID=MyAccount&LOCALE=&email=
# (Example: subdomain.example.com)
# Error code =

JS_NORMAL_PATTERN = re.compile(r"""
    (?:^|\s+)alert\( |
    && |
    \|\| |
    (?:^|\s+)[\w.\[\]"]+\s*= |
    (?:^|\s+)(?:if|for|function)\s*\( |
    (?:^|\s+)(?:return|break|continue); |
    (?:^|\s+)return\s+(?:true|false|"[^"]*"|'[^']*'); |
    /\*(?:.|\n)*?\*/ |  # comment
    //.*?(?:\n|\\n)   # comment
""", re.VERBOSE)

# Exclude: /, -, ", ', |, :, &, Comma, ., ?, !, %, (, )
NON_WORD_SYMBOL = re.compile(r"[~_\\+=@$#*\[\]{}<>;]")  

basic_locale = [item.lower() for item in abbr.keys()]
variant_locale = [item.replace('-', '_') for item in basic_locale]
simple_locale = [''.join(item.split('-')[0:1]) for item in basic_locale]


class StringScanner(object):

    def __init__(self, variable=None):
        # self.filter_list = [r'<\\?[a-zA-Z_/!?].*?>']
        # self.filter_list = []
        if variable:
            self.var_list = variable.split(u'☆')
        else:
            self.var_list = [r'\$?\{+.+?\}+', r'[$!]+t?\(+.+?\)+', r'%[\w%.]+', r'@@\w+@@']

        self.is_url_num = 0
        self.is_file_or_path_num = 0
        self.is_date_format_num = 0
        self.is_invalid_data_num = 0
        self.is_CJK_num = 0
        self.is_CSS_num = 0
        self.is_JavaScript_num = 0
        self.is_locale_num = 0

    def split_words(self, text):

        temp = text.strip()
        if temp:
            # Pre-processing ...
            temp = re.sub(r"\\+([\"'])", r'\1', temp)  # Unescape "\\ + quot"
            for pattern in self.var_list:
                temp = re.sub(pattern, '~v~', temp)

            word_list = re.split(r"\s+|(?:\\r)?\\n|\\+n", temp)
            return [word for word in word_list if word.strip()]

        else:
            return []

    def calc_word_count(self, text):
        word_list = self.split_words(text)
        return len(word_list)

    def _calc_word_length(self, text):
        word_length = 0
        word_list = text.split()
        for word in word_list:
            word_length += len(word)
        return word_length

    def _merge_word(self, text):
        # Special case
        # e.g. Whitespace in path
        text = re.sub(r"(?i)([\\/])Program Files( \(x86\))?", r"\1ProgramFiles", text)
        return text

    def is_url(self, text):

        text = self._merge_word(text)
        if self.calc_word_count(text) == 1:
            text = text.strip()
            if scheme_compiler.search(text) or ip4_compiler.match(text):
                return True

        return False

    def _determine_splitter(self, text):

        slash = text.count('/')
        backward_slash = text.count('\\')

        if slash > 0 and backward_slash == 0:
            return '/'
        if slash == 0 and backward_slash > 0:
            return '\\'
        return

    def is_file_or_path(self, text):

        text = self._merge_word(text)

        if self.calc_word_count(text) == 1:
            text = text.strip()
            if win_path_compiler.match(text) or linux_path_compiler.match(text) or file_compiler.match(text):
                return True
        else:
            separator = self._determine_splitter(text)
            if separator:
                counter = 0
                word_list = text.split()
                word_num = len(word_list)

                if separator in word_list[0]:
                    for word in word_list:
                        if separator in word:
                            counter += 1

                    threshold = word_num - 1 if word_num > 2 else word_num
                    if counter >= threshold:
                        return True

        return False

    def is_date_format(self, text):

        text = text.strip().strip('()[]{}')

        counter = 0
        if text:
            split_list = re.split(r"[/.\-:\s,]+", text)

            for item in split_list:
                if len(item) == 1:
                    if not item.isalpha():
                        return False
                else:
                    if not re.match(r'^([a-zA-Z0])\1+$', item):
                        return False
                    counter += 1

        if counter > 0:
            return True
        else:
            return False

    def is_abnormal_word(self, word):

        non_word_symbol = NON_WORD_SYMBOL.findall(word)

        if len(non_word_symbol) > 0 and len(word) > 1:
            return True

        # - / | ,   which serve as separator between words
        if (len(word) > 1 and (word.startswith(('-', '/', '|', ',')) or word.endswith(('-', '/', '|')))) \
             or word.count('-') + word.count('/') > 2:
            return True

        # , . : ? !  which only allowed in the tail of single word
        # , is handled above
        tail_allowed_chars = ('.', ':', '?', '!')
        for char in tail_allowed_chars:
            temp = word.rstrip(char)
            if char in temp:
                return True

        en_letter = re.findall('[a-zA-Z]', word)
        if len(en_letter) <= 1 or (len(en_letter) / len(word) <= 0.4):
            return True

        # Camel Style
        if not word.islower() and (en_letter and en_letter[0] >= 'a'):
            return True

    # def is_expression(self, text):
    #     pass

    def is_invalid_data(self, text):

        words = self.split_words(text)
        word_count = len(words)

        if word_count == 0:
            return True

        elif word_count == 1:
            word = words[0]

            if '_' in word:
                return True

            if word.islower():
                return True

            if self.is_abnormal_word(word):
                return True

        else:
            abnormal_word_count = 0
            variable_word_count = 0
            for word in words:
                if not word.strip():
                    continue
                elif '~v~' in word:
                    variable_word_count += 1
                elif self.is_abnormal_word(word):
                    # print(word)
                    abnormal_word_count += 1 if word_count <= 15 else 0.8

            if variable_word_count / word_count >= 0.5:
                return True

            if abnormal_word_count / word_count > 0.55:
                return True

        return False

    def is_CJK(self, text):

        for char in text:
            for CJK_START, CJK_END in CJK_SCOPE:
                if ord(char) >= CJK_START and ord(char) <= CJK_END:
                    return True
        return False

    def is_CSS(self, text):

        text = CSS_COMMENT.sub('', text)
        match = CSS_PATTERN.search(text)
        if match:
            return True
        return False

    def is_JavaScript(self, text):
        """
        Need unescape and clear html tag in advance
        """
        core_match = JS_CORE_PATTERN.findall(text)

        if len(core_match) >= 2:
            return True
        else:
            normal_match = JS_NORMAL_PATTERN.findall(text)
            match_count = len(core_match) + len(normal_match)
            if match_count >= 2:
                return True
            elif match_count > 0:
                match_length = 0
                for match_str in core_match + normal_match:
                    match_length += len(match_str)

                if match_length / self._calc_word_length(text) >= 0.5:
                    return True

        return False

    def is_locale(self, text):

        if text.lower() in basic_locale + variant_locale or text in simple_locale:
            return True
        else:
            return False

    def scan_string(self, text):

        scan_func = (
            'is_url', 'is_file_or_path', 'is_date_format', 'is_invalid_data', 'is_CJK', 'is_CSS', 'is_JavaScript',
            'is_locale')

        for func in scan_func:
            if getattr(self, func)(text):
                num = getattr(self, func+'_num') + 1
                setattr(self, func+'_num', num)
                break
        else:
            return True
        return False


class StringProcessor(StringScanner):

    def __init__(self):

        super(StringProcessor, self).__init__()

    def replace_var_with_sym(self, text):

        ret = []
        for seg in text:
            seg = seg.strip()
            seg = re.sub(r"\\+([\"'])", r'\1', seg)
            for pattern in self.var_list:
                seg = re.sub(pattern, '#', seg)
            ret.append(seg)

        return ret


if __name__ == '__main__':

    import codecs
    import string

    scan_func = (
        'is_url', 'is_file_or_path', 'is_date_format', 'is_invalid_data', 'is_CJK', 'is_CSS', 'is_JavaScript',
        'is_locale')

    string_scanner = StringScanner()

    lines = [
        # '{[ProductName] }Setup failed.',
        # 'Setup cannot get server information. Please contact your vendor for details. Setup aborted.\\nError code =',
        # 'Enable Spyware/Grayware Scan/Clean',
        # 'characters:\ \\ / : * ? \" < > | . ',
        # 'Perform \"Update Now\"',
        # 'Verifying version...(0%)',
        # 'Endpoint Name,OfficeScan Domain,Connection Status,Services',
        # 'Chan&ge...',
        # 'Dear   ,  You have successfully activated , and now have award-winning protection against computer viruses and other security threats.  Please keep the activation information shown below in a safe place for future reference. You will need to provide the Email address when visiting ?TARGET=Portal&FUNID=MyAccount&LOCALE=&email= to renew your subscription or manage where you have installed the software.'
        # 'You could click the Refresh button to try again with different credentials or read                     <a href="http://esupport.trendmicro.com/solution/en-us/1054516.aspx?location=hotissues&seg=smb&utm_source=p...'
    ]

    for line in lines:

        for func in scan_func:
            if getattr(string_scanner, func)(line):
                # print(line)
                print("True")
                # break
            else:
                print("False")
        # else:
        # print(line)















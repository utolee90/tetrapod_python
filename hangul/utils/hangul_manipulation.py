from .operation import *
from .hangul_objects import *
from hangul_utils.unicode import *
import re


# 메시지에서 단어의 위치를 찾아주는 함수
def get_position_all(message, search, is_string=True):
    # 우선 !, ? 기호 드롭시키기
    search = search.replace("!", "").replace("?", "")

    i = 0
    indexes = []
    while search in message[i:]:
        i = message.index(search)
        indexes.append(i)

    # is_string이 false면 첫 위치만 출력
    if not is_string:
        return indexes
    # is_string이 true이면 (첫위치, 끝위치) 형식으로 출력
    else:
        string_positions = [tuple(range(x, len(search))) for x in indexes]
        return string_positions


# manyarray => [[many_array[0], many_array[1]], [many_array[1], many_array[2]],....]
def grab_couple(args):
    return [[args[i], args[i + 1]] for i in range(len(args) - 1)] if len(args) >= 2 else []


# 단어 -> 낱자로 분리하는 함수
# . 이스케이프 문자.
# 바! -> [바, 뱌, 빠,... ].
# 바? -> 한글 ? 개수까지 완전 무시...
# 바+ -> [바, 박, 밖,...]. 받침 포함.

def word_to_array(word):
    word_array = []
    for i in range(len(word)):
        # . 처리
        if word[i - 1] == "." and (i == 1 or i > 1 and word[i - 2] != "."):
            word_array = word_array[:-1] + [word[i]]

        elif word[i] == '?':
            word_array = word_array[:-1] + [word_array[-1] + word[i]]

        elif i > 0 and ord(word[i - 1]) >= ord('가') and ord(word[i - 1]) <= ord('힣') and (
                word[i] == "!" or word[i] == "+"):
            word_array = word_array[:-1] + [word_array[-1] + word[i]]

        else:
            word_array.append(word[i])

    return word_array


# 메시지를 limit 길이로 분리하기
def length_split(msg, limit):
    if len(msg) <= limit: return [msg]

    fixed_msg = []
    full_msg_len = len(msg)
    cur = 0
    half = limit // 2

    split_list, split_list_2 = [], []

    while True:
        if cur == full_msg_len:
            if cur != 0:
                if len(split_list) > len(split_list_2):
                    fixed_msg.append("".join(split_list))
                    if len(split_list_2) > 0: fixed_msg.append("".join(split_list_2))
                    split_list, split_list_2 = [], []

                else:
                    fixed_msg.append("".join(split_list_2))
                    if len(split_list) > 0: fixed_msg.append("".join(split_list))
                    split_list, split_list_2 = [], []

            break

        if cur != 0 and cur % limit == 0 and len(split_list) != 0:
            fixed_msg.append("".join(split_list))
            split_list = []
        if cur != 0 and cur % limit == half and len(split_list_2) != 0:
            fixed_msg.append("".join(split_list_2))
            split_list_2 = []
        split_list.append(msg[cur])
        if cur >= half:
            split_list_2.append(msg[cur])
        cur += 1

    return fixed_msg


# 단어 정렬 기준 가나다순이 아닌 단어 길이 역순으로 정렬하기.

def sort_map(input_map):
    sorted_map = []

    if str(type(input_map)) == "<class 'list'>":
        sorted_map = sorted(input_map, key=lambda x: len(x), reverse=True)
        return sorted_map

    else:
        sorted_map = sorted(list(input_map.keys()), key=lambda x: len(x), reverse=True)
        return {key: input_map[key] for key in sorted_map}


# a, b의 원소가 서로소인지 판단하기
def is_disjoint(a, b):
    for x in a:
        if x in b: return False
    else:
        return True


# 리스트에서 특정 타입만 필터
def filter_list(arg, t):
    if str(type(arg)) == "<class 'list'>":
        return list(filter(lambda x: str(type(x)) == f"<class '{t}'>", arg))
    elif str(type(arg)) == "<class 'dict'>":
        return {x: arg[x] for x in arg.keys() if str(type(x)) == f"<class '{t}'>"}


#  각 원소를 map으로 바꿔주는 함수
def list_map(elem, callback):
    if str(type(elem)) in [f"<class '{t}'>" for t in ['str', 'int', 'float', 'boolean']]:
        return callback(elem)
    # dict일 때는
    elif str(type(elem)) == "<class 'dict'>":
        return {key: list_map(elem[key], callback) for key in elem.keys()}
    # 나머지 iterable일 때
    elif elem.__iter__:
        return [list_map(x, callback) for x in elem]


# 2차원 배열 형태로 정의된 것을 풀어쓰기
def recursive_component(data):
    # iterable하지 않으면 그대로 출력
    if not data.__iter__:
        return data

    else:
        # 데이터에 대해서 출력하기...
        for i in range(len(data)):

            # data[i]에 대해 순회하기
            for j in range(len(data[i])):
                item = data[i][j]

                # item이 배열일 경우 다시 재귀적으로 접근하기
                if item.__iter__:
                    solved_data = recursive_component(item)
                    # solved data에 풀어서 접근하기
                    data[i][j] = None
                    data[i] = data[i] + solved_data

        # None 원소 제거하기
        for i in range(len(data)):
            data[i] = list(filter(lambda x: x != None, data[i]))

        # 우선 product_list을 이용해서 확보하기
        presolved_data = product_list(data)
        # 예시 : [['가','나','다'], ['가','격']] => [['가','가'], ['가','격'], ['나','가'], ['나','격'], ['다','가'], ['다','격']]
        # => ['가가', '가격', '나가', '나격', '다가', '다격']

        solved_data = list(map(lambda x: "".join(x), presolved_data))
        return solved_data


# 겹자모 판단하기. [var1, var2]가 compare_list 안에 있는지 확인. 기본은 DOUBLE_CONSONANT+DOUBLE_VOWEL 안에 있는지 확인함.

def is_double(var1, var2, allow_sim=False):
    compare_list = []
    # iterable할 때
    if allow_sim.__iter__:
        compare_list = allow_sim if allow_sim.__iter__ else list(map(lambda x: [x[0], x[1]], allow_sim))
    else:
        compare_list.extend(DOUBLE_CONSONANTS + DOUBLE_VOWELS)
        if allow_sim:
            res1 = product_list([["ㅗ", "ㅜ", "t", "T", "ㅡ", "_"], ["ㅣ", "!", "I", "1", "l", "|"]])
            compare_list.extend(
                [
                    ["ㄱ", "7"], ["7", "7"], ["ㄱ", "^"], ["7", "ㅅ"], ["7", "^"], ["ㄹ", "^"], ["#", "ㅅ"], ["ㅂ", "^"],
                    ["#", "ㅅ"],
                    ["ㅗ", "H"], ["ㅜ", "y"], ["t", "y"], ["T", "y"], *res1
                ]
            )

        return [var1, var2] in compare_list


# 맵 파싱하기
# 맵 형식 {"바":{value:"바", index:[1]}, "ㅂ오":{value:"보", index:[2]}} =>
# {"message_list": ["바","ㅂ오"], "message_index":[1,2], parsed_message: ["바","보"]}
def parse_map(input_map):
    original_message_list = []
    original_message_index = []
    parsed_message = []
    search = 0
    # index에 존재하는 최댓값.
    MAX_VALUE = max(list(map(lambda x: max(x["index"]), input_map.values())))

    while search <= MAX_VALUE:
        for val, obj in input_map.items():
            if search in obj["index"]:
                original_message_index.append(search)
                original_message_list.append(val)
                parsed_message.append(obj["value"])

                if re.match(r"[ㄱ-ㅎ][가-힣]+$", val):
                    search += len(val) - 1
                else:
                    search += len(val)

    return {
        "message_list": original_message_list,
        "message_index": original_message_index,
        "parsed_message": parsed_message
    }


# 한글 낱자를 초성/중성/종성으로 분리하기
def cho_jung_jong(c):
    try:
        split_res = split_syllable_char(c)
        # 중성이 복모음일 때엔 분리해서 표현하기
        list_jung = []
        if split_res[1]!= None:
            list_jung = list(DICT_DOUBLE_JAMOS[split_res[1]]) if split_res[1] in DICT_DOUBLE_JAMOS.keys() else [split_res[1]]
        # 종성이 복자음일 경우 분리해서 표현하기
        list_jong = []
        if split_res[1] != None:
            list_jong = list(DICT_DOUBLE_JAMOS[split_res[2]]) if split_res[2] in DICT_DOUBLE_JAMOS.keys() else [split_res[2]]
        return {
                "cho": [split_res[0]] if split_res[0] != None else [],
                # javascript  버전과 맞추기 위해 자모분리후 처리
                "jung": list_jung,
                "jong": list_jong
            }
    except:
        return {'cho': [], "jung": [], "jong": []}


# 메시지를 단순히 파싱 입력용 맵으로 바꾸어주는 함수
# 예시 : "간지" => {"간": {"value":"간", "index":[1]}, "지":{"value":"지", "index":[2]}}
def msg_to_map(msg):
    res = {}
    for ind, val in enumerate(msg):
        if res.get(val):
            res[val]["index"].append(ind)
        else:
            res[val] = {"value": val, "index": [ind]}
    return res

# 영자/두벌식 혼합된 내용을 한글로 바꾸어주기
# 예시 : qkqh -> 바보
def qwerty_to_dubeol(msg, is_map=False):
    MAP = QWERTY_DUBEOL_MAPPING

    qtd_macro = lambda letter: MAP[letter] if letter in MAP.values() else letter

    if not is_map:
        new_msg = str(map(qtd_macro, msg))
        return join_jamos(split_syllables(new_msg))
    # 맵을 만들어야 할 때
    else:
        msg_res = []
        res = {}
        tmp = ""  # 글자값 저장.
        for ind, letter in enumerate(msg):
            consonants = CHAR_INITIALS + ["q", "w", "e", "r", "t", "a", "s", "d", "f", "g", "z", "x", "c", "v"]
            vowels = CHAR_MEDIALS + ["q", "w", "e", "r", "t", "a", "s", "d", "f", "g", "z", "x", "c", "v"]

            def res_macro(sep, val=tmp):
                if val != "":
                    msg_res.append(val)
                    if not res.get(val):
                        res[val] = {"value": qwerty_to_dubeol(val), "index": [ind - len(val)]}
                    else:
                        res[val]["index"].append(ind - len(val))
                    tmp = sep

            # 첫 글자는 무조건 추가
            if ind == 0:
                tmp += letter

            # 자음 - 뒤에 모음이 아닌 문자가 올 때에만 앞글자에 붙인다.
            elif letter.lower() in consonants and (ind == len(msg) - 1 or msg[ind + 1].lower() not in vowels):
                # 앞에 모음이 오거나
                if msg[ind - 1].lower() in vowels:
                    tmp += letter
                # 앞앞에 모음 & 앞자음이 쌍자음 형성 가능.
                elif ind > 1 and msg[ind - 2].lower() in vowels and msg[ind - 1].lower() in consonants:

                    double_test = [
                        MAP[msg[ind - 1]] if msg[ind - 1] in MAP else msg[ind - 1],
                        MAP[letter] if letter in MAP else letter,
                    ]

                    if double_test not in DOUBLE_CONSONANTS:
                        res_macro(letter)
                    else:
                        tmp += letter

                else:
                    res_macro(letter)

            # 모음의 경우 자음이 앞에 오면 무조건 앞글자에 붙이기
            elif letter.lower() in vowels and msg[ind - 1].lower() in consonants:
                tmp += letter

            elif ind > 1 and letter.lower() in vowels and msg[ind - 1].lower() in vowels and msg[
                ind - 2].lower() in consonants:
                tmp_list = [qtd_macro(msg[ind - 1]), qtd_macro(letter)];
                if tmp_list in DOUBLE_VOWELS:
                    tmp += letter
                else:
                    res_macro(letter)

            else:
                res_macro(letter)

        # 마지막 글자 붙이기
        if tmp != "":
            msg_res.append(tmp)
            if not res.get(tmp):
                res[tmp] = {"value": qwerty_to_dubeol(tmp), "index": [len(msg) - len(tmp)]}
            else:
                res[tmp]["index"].append(len(msg) - len(tmp))

            tmp = ""

        return res


# 복자모->단자모로 분리해서 나누기.
def split_simple_syllables(msg):
    # 우선 메시지를 초중종으로 나누어주기
    split_msg = split_syllables(msg)
    return str(map(lambda x: (DICT_DOUBLE_JAMOS[x] if x in DICT_DOUBLE_JAMOS.keys() else x), split_msg))

# 단자모로 구성된 문자열을 한글로 결합하는 함수
def join_simple_jamos(msg):
    # 겹자음/겹모음 결합시키기.
    jamo_list = []
    for idx, letter in enumerate(msg):
        if idx == 0: jamo_list.append(letter)
        else:
            # 앞의 모음과 복모음 형성가능 -> 앞글자와 붙이기
            if [msg[idx-1], letter] in DOUBLE_VOWELS:
                jamo_list[-1] += letter
            # 앞의 자음과 복자음 형성가능 + 뒤에 모음 오지 않음. -> 앞글자와 붙이기
            elif [msg[idx-1], letter] in DOUBLE_CONSONANTS and idx<len(msg)-1 and msg[idx+1] not in CHAR_MEDIALS:
                jamo_list[-1] += letter
            # 나머지는 jamo_list 추가
            else:
                jamo_list.append(letter)

    jamo_str = str(map(lambda x: (DICT_JOIN_DOUBLE_JAMOS[x] if x in DICT_JOIN_DOUBLE_JAMOS.keys() else x), jamo_list))
    return join_jamos(jamo_str)

# 자모조합을 악용한 비속어 걸러내기. ㄱH^H77| 검출 가능. is_map 사용시에 딕셔너리 형태로 검출.
# class로 바꾸어보자.
class Antispoof:

    """
    Antispoof 클래스.
    사용방법 : val = Antispooof("7ㅓㅈ1") => 메시지 "7ㅓㅈ1"에 대해 antisloofing 시행
    메시지 추출시 val_msg = val.result() 사용
    """


    def __init__(self, msg):
        self.__msg = msg

        # 타입 리스트 지정.
        msg_alphabet_type = []
        for letter in msg:
            msg_alphabet_type.append(self.__type_check(letter))

        self.__list_type = msg_alphabet_type


    # 타입에 따라 문자 출력하는 함수
    @staticmethod
    def __type_check(letter):
        """타입에 따라 출력하기"""
        # 한글 낱자
        if 0xac00 <= ord(letter) <= 0xd7a3:
            return 'h'
        # 한글 자음,
        elif letter in CHAR_INITIALS:
            return 'c'
        # 한글 모음
        elif letter in CHAR_MEDIALS:
            return 'm'
        # 한글 종성전용
        elif letter in CHAR_FINALS:
            return 'f'
        # 유사자음
        elif letter in PSEUDO_CONSONANTS.keys():
            return 'd'
        # 유사모음
        elif letter in PSEUDO_VOWELS.keys():
            return 'w'
        # 공백
        elif letter in [" ", '\t']:
            return 's'
        else:
            return 'e'

    # 원문 출력
    def source(self):
        "원문 출력"
        return self.__msg

    # 유사자음/유사모음으로 된 낱자 모음을 한글로 바꾸기. 혼동 방지를 위해 음절 단위로만 입력값 받기
    # 예시 : "7ㅓㅈ1" => "거지"
    @classmethod
    def unravel(cls, syllable_letters):
        # 우선 유사자음, 유사모음-> 한글자음, 한글모음으로 바꾸기
        pseudo = {**PSEUDO_VOWELS, **PSEUDO_CONSONANTS}

        join_double = {"ㄱㄱ":"ㄲ", "ㄷㄷ": "ㄸ", "ㅂㅂ":'ㅃ', "ㅅㅅ":'ㅆ', "ㅈㅈ":'ㅉ'}
        res = []
        for letter in syllable_letters:
            res.append(pseudo[letter] if letter in pseudo.keys() else letter)

        # 동일자음 표시 -> 쌍자음 처리
        if res[0]+res[1] in join_double.keys():
            res = [join_double[res[0]+res[1]]] + res[2:]

        # 복모음 -> 합치기
        if len(res)>=3 and  res[1]+res[2] in DICT_JOIN_DOUBLE_JAMOS.keys():
            res = res[0]+ [DICT_JOIN_DOUBLE_JAMOS[res[1]+res[2]]] + res[3:]

        # 받침 복자음 -> 합치기
        if len(res)>=4 and res[2]+res[3] in DICT_JOIN_DOUBLE_JAMOS.keys():
            res = res[:2] + [DICT_JOIN_DOUBLE_JAMOS[res[2]+res[3]]]

        return join_jamos_char(str(res))



    # 음절 단위로 끊어주는 함수. is_original이 있으면 유사모음 변환하지 않고 그대로 출력.
    # 예시 :
    def join_by_syllable(self, is_original = False):
        msg = self.__msg
        list_type = self.__list_type
        # 결과값.
        res = []
        for idx, letter in enumerate(msg):
            # 첫글자는 새 음절에 넣기
            if idx ==0:
                res.append(letter)

            # 낱자 한글/공백/기타면 무조건 새 음절에 넣기.
            elif list_type[idx] in ["h", "s", "e"]:
                res.append(letter)

            #
            # 일반적 자음일 때
            elif list_type[idx] == "c":
                # 바로 뒤에 모음이 오면 무조건 모음에 붙어야 하기에 음절 나누기
                if idx<len(msg)-1  and list_type[idx+1] in ["v", "w"]:
                    res.append(letter)
                else:
                    # 바로 앞에 모음이 올 때 앞 음절에 붙이기
                    if list_type[idx-1] in ["v", "w"] and letter in CHAR_FINALS:
                        res[-1] = res[-1]+letter
                    # 앞알 모음, 바로 앞 자음과 겹자음 형성 가능하면 앞 음절에 붙이기
                    elif idx>1 and  msg[idx-2] in ["v", "w"] and [msg[idx-1], letter] in DOUBLE_CONSONANTS:
                        res[-1] = res[-1] + letter
                    else:
                        res.append(letter)

            #받침에만 오는 자음일 때
            elif list_type[idx] == "f":
                # 앞에 모음이 있으면 무조건 앞 음절에 붙이기
                if list_type[idx - 1] in ["v", "w"]:
                    res[-1] = res[-1] + letter
                else:
                    res.append(letter)

            # 모음/유사모음인 경우
            elif list_type[idx] in ['v', 'w']:
                # 앞에 자음이 있을 때 붙이기
                if list_type[idx-1] in ["c", "d"]:
                    res[-1] = res[-1]+letter
                # 복모음 형성 가능 - 붙이기.
                elif idx>1 and list_type[idx-2] in ["c", "d"] and [msg[idx-1], letter] in DOUBLE_VOWELS:
                    res[-1] = res[-1] + letter
                else:
                    res.append(letter)


            # 유사 자음인 경우
            elif list_type[idx] == "d":
                #  첫자음으로 복모음 형성할 수 있는 조합들.
                PSEUDO_CONSONANTS_DOUBLE= ["77", 'cc', '##', '^^', 'nn']

                # 바로 앞의 유사자음과 묶어서 생각할 수 있는 경우도 고려해야 할 것. 이 경우는 묶어서 생각하기.
                # '이^^ㅣ' -> 잇시가 아닌 이씨로 받아들인다.

                # 앞글자
                if letter in ['7','c','#','^','n'] and idx<len(msg)-1 and letter == msg[idx+1]:
                    if idx<len(msg)-2 and list_type[idx + 2] in ["v", "w"]:
                        res.append(letter)
                    elif list_type[idx-1] in ['v','w'] and letter in ['7','^','n']:
                        res[-1] = res[-1]+letter
                    else:
                        res.append(letter)
                # 같이 나오는 뒷글자 -> 무조건 앞글자에 따라서 붙여준다.
                elif letter in ['7','c','#','^','n'] and idx>1 and letter == msg[idx-1]:
                    res[-1] = res[-1]+letter

                # 아니면 자음와 똑같은 기준으로 음절 나누기
                else:
                    # 바로 뒤에 모음이 오면 무조건 모음에 붙어야 하기에 음절 나누기
                    if idx < len(msg) - 1 and list_type[idx + 1] in ["v", "w"]:
                        res.append(letter)
                    else:
                        # 바로 앞에 모음이 올 때 앞 음절에 붙이기
                        if list_type[idx - 1] in ["v", "w"] and letter in CHAR_FINALS:
                            res[-1] = res[-1] + letter
                        # 앞알 모음, 바로 앞 자음과 겹자음 형성 가능하면 앞 음절에 붙이기
                        elif idx > 1 and msg[idx - 2] in ["v", "w"] and [msg[idx - 1], letter] in DOUBLE_CONSONANTS:
                            res[-1] = res[-1] + letter
                        else:
                            res.append(letter)

        # is_original이 False이면 강제로 한글로 변환해주기

        if not is_original:
            res = list(map(self.unravel, res))
            
        return res








def antispoof(msg, is_map = False):

    """메시지 타입: c: 자음, v: 모음, h: 한글 낱자, d: 유사자음, w: 유사모음, s:공백, e:나머지 문자"""
    msg_alphabet_type = []
    # 낱자별로 확인
    for letter in msg:
        if 0xac00 <= ord(letter) <= 0xd7a3:
            msg_alphabet_type.append('h')
        elif letter in CHAR_INITIALS+CHAR_FINALS:
            msg_alphabet_type.append('c')
        elif letter in CHAR_MEDIALS:
            msg_alphabet_type.append('v')
        elif letter in PSEUDO_CONSONANTS.keys():
            msg_alphabet_type.append('d')
        elif letter in PSEUDO_VOWELS.keys():
            msg_alphabet_type.append('w')
        elif letter in [" ", "\t"]:
            msg_alphabet_type.append('s')
        else:
            msg_alphabet_type.append('e')

    pre_syllable = [] # 음절단위 분리하는 리스트
    pre_syllable_origin = [] #is_map 사용시 음절의 원본 메시지 저장.
    pre_index = [] # is_map 사용시

    ind = -1
    # 캐릭터 타입별 음절 분리
    for idx, letter in enumerate(msg):

        # pre_syllable에 음절 첫 글자 집어넣는 함수. msg1 사용한 이유는 letter 대신 다른 것을 사용할 수도 있을 때 대비하기
        def split_syllable(msg1=letter):
            nonlocal ind
            pre_syllable.append(msg1)
            if is_map:
                pre_syllable_origin.append(letter)
                ind += len(msg[idx])
                pre_index.append(ind)

        # 앞 음절에 붙이는 함수
        def join_jamo_to_prev_syllable(include_pseudo = False, msg1 = letter):

            pass


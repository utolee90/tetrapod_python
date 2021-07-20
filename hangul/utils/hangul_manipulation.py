from .operation import *
from .hangul_objects import *
from hangul_utils.unicode import *
import re


# 메시지에서 단어의 위치를 찾아주는 함수
def get_position_all(message, search, is_string = True):

    # 우선 !, ? 기호 드롭시키기
    search = search.replace("!","").replace("?","")

    i = 0
    indexes = []
    while search in message[i:]:
        i = message.index(search)
        indexes.append(i)

    # is_string이 false면 첫 위치만 출력
    if not is_string: return indexes
    # is_string이 true이면 (첫위치, 끝위치) 형식으로 출력
    else:
        string_positions = [tuple(range(x, len(search))) for x in indexes]
        return string_positions


# manyarray => [[many_array[0], many_array[1]], [many_array[1], many_array[2]],....]
def grab_couple(args):
    return [[args[i], args[i+1]] for i in range(len(args)-1)] if len(args)>=2 else []

# 단어 -> 낱자로 분리하는 함수
# . 이스케이프 문자.
# 바! -> [바, 뱌, 빠,... ].
# 바? -> 한글 ? 개수까지 완전 무시...
# 바+ -> [바, 박, 밖,...]. 받침 포함.

def word_to_array(word):
    word_array = []
    for i in range(len(word)):
        # . 처리
        if word[i-1] == "." and (i == 1 or i > 1 and word[i-2] != "."):
            word_array = word_array[:-1]+[word[i]]

        elif word[i] == '?':
            word_array = word_array[:-1]+[word_array[-1]+word[i]]

        elif i>0 and ord(word[i-1])>=ord('가') and ord(word[i-1])<= ord('힣') and (word[i] == "!" or word[i] == "+"):
            word_array = word_array[:-1] + [word_array[-1]+word[i]]

        else:
            word_array.append(word[i])

    return word_array

# 메시지를 limit 길이로 분리하기
def length_split(msg, limit):

    if len(msg)<= limit: return [msg]

    fixed_msg = []
    full_msg_len = len(msg)
    cur = 0
    half = limit//2

    split_list, split_list_2 = [], []

    while True:
        if cur == full_msg_len:
            if cur != 0:
                if len(split_list) > len(split_list_2):
                    fixed_msg.append("".join(split_list))
                    if len(split_list_2)>0: fixed_msg.append("".join(split_list_2))
                    split_list, split_list_2 = [], []

                else:
                    fixed_msg.append("".join(split_list_2))
                    if len(split_list)>0: fixed_msg.append("".join(split_list))
                    split_list, split_list_2 = [], []

            break

        if cur !=0 and cur%limit == 0 and len(split_list)!=0:
            fixed_msg.append("".join(split_list))
            split_list = []
        if cur !=0 and cur%limit == half and len(split_list_2) !=0:
            fixed_msg.append("".join(split_list_2))
            split_list_2 = []
        split_list.append(msg[cur])
        if cur>= half:
            split_list_2.append(msg[cur])
        cur +=1

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
def is_disjoint(a,b):
    for x in a:
        if x in b: return False
    else: return True

# 리스트에서 특정 타입만 필터
def filter_list(arg, t):
    if str(type(arg)) == "<class 'list'>":
        return list(filter(lambda x: str(type(x)) == f"<class '{t}'>", arg ))
    elif str(type(arg)) == "<class 'dict'>":
        return {x: arg[x] for x in arg.keys() if str(type(x)) == f"<class '{t}'>"}

#  각 원소를 map으로 바꿔주는 함수
def list_map(elem, callback):
    if str(type(elem)) in [f"<class '{t}'>" for t in ['str', 'int', 'float', 'boolean']]:
        return callback(elem)
    # dict일 때는
    elif str(type(elem)) == "<class 'dict'>":
        return {key : list_map(elem[key], callback) for key in elem.keys() }
    # 나머지 iterable일 때
    elif elem.__iter__:
        return [list_map(x, callback) for x in elem]


# 2차원 배열 형태로 정의된 것을 풀어쓰기
def recursive_component(data):

    # iterable하지 않으면 그대로 출력
    if not data.__iter__: return data

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
                    data[i] = data[i]+ solved_data

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

def is_double(var1, var2, allow_sim = False):
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
                    ["ㄱ", "7"], ["7","7"], ["ㄱ","^"], ["7","ㅅ"], ["7","^"], ["ㄹ","^"], ["#","ㅅ"], ["ㅂ","^"], ["#","ㅅ"],
                    ["ㅗ","H"], ["ㅜ", "y"], ["t", "y"], ["T", "y"], *res1
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
                    search += len(val)-1
                else: search += len(val)

    return {
        "message_list": original_message_list,
        "message_index": original_message_index,
        "parsed_message": parsed_message
    }


# 한글 낱자를 초성/중성/종성으로 분리하기
def cho_jung_jong(c):
    try:
        split_res = split_syllable_char(c)
        return {
            "cho": [split_res[0]] if split_res[0] != None else [],
            "jung": [split_res[1]] if split_res[1] != None else [],
            "jong": [split_res[2]] if split_res[2] != None else [],
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


# 영문 -> 한글변환 조합 만들기
def qwerty_to_dubeol(msg, is_map = False):
    MAP = QWERTY_DUBEOL_MAPPING

    qtd_macro = lambda letter: MAP[letter] if letter in MAP.values() else letter

    if not is_map:
        new_msg = str(map(qtd_macro, msg))
        return join_jamos(split_syllables(new_msg))
    # 맵을 만들어야 할 때
    else:
        msg_res = []
        res = {}
        tmp = "" # 글자값 저장.
        for ind, letter in enumerate(msg):
            consonants = CHAR_INITIALS + ["q", "w", "e", "r", "t", "a", "s", "d", "f", "g", "z", "x", "c", "v"]
            vowels = CHAR_MEDIALS + ["q", "w", "e", "r", "t", "a", "s", "d", "f", "g", "z", "x", "c", "v"]

            def res_macro(sep, val=tmp):
                if val != "":
                    msg_res.append(val)
                    if not res.get(val):
                        res[val] = {"value": qwerty_to_dubeol(val), "index": [ind - len(val)]}
                    else: res[val]["index"].append(ind - len(val))
                    tmp = sep

            # 첫 글자는 무조건 추가
            if ind ==0: tmp += letter

            #자음 - 뒤에 모음이 아닌 문자가 올 때에만 앞글자에 붙인다.
            elif letter.lower() in consonants and (ind == len(msg)-1 or msg[ind+1].lower() not in vowels):
                # 앞에 모음이 오거나
                if msg[ind-1].lower() in vowels: tmp += letter
                # 앞앞에 모음 & 앞자음이 쌍자음 형성 가능.
                elif ind>1 and msg[ind-2].lower() in vowels and msg[ind-1].lower() in consonants:

                    double_test = [
                        MAP[msg[ind-1]] if msg[ind-1] in MAP else msg[ind-1],
                        MAP[letter] if letter in MAP else letter,
                    ]

                    if double_test not in DOUBLE_CONSONANTS: res_macro(letter)
                    else: tmp +=letter

                else: res_macro(letter)

            # 모음의 경우 자음이 앞에 오면 무조건 앞글자에 붙이기
            elif letter.lower() in vowels and  msg[ind-1].lower() in consonants:
                tmp += letter

            elif ind>1 and letter.lower() in vowels and msg[ind-1].lower() in vowels and  msg[ind -2].lower() in consonants:
                tmp_list = [ qtd_macro(msg[ind-1]), qtd_macro(letter)];
                if tmp_list in DOUBLE_VOWELS:
                    tmp += letter
                else: res_macro(letter)

            else: res_macro(letter)

        #마지막 글자 붙이기
        if tmp != "":
            msg_res.append(tmp)
            if not res.get(tmp):
                res[tmp] = {"value": qwerty_to_dubeol(tmp), "index": [len(msg) - len(tmp)]}
            else:
                res[tmp]["index"].append(len(msg) - len(tmp))

            tmp = ""

        return res




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
                    split_list, split_list_2 = []. []

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

# 겹자모 판단하기기
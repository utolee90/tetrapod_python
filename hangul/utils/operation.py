# iterable 형태의 object를 배열로 만들어주기
def to_dict(obj):
    return obj if str(type(obj)) == "<class 'dict'>" else {idx: val for idx, val in enumerate(obj)}


# 포함관계
def include(inc, exc, order=False):
    # 타입이 다를 때는 거짓 출력
    if type(inc) != type(exc):
        return False
    else:
        # 집합일 때는 내장함수 사용 가능.
        if str(type(inc)) == "<class 'set'>":
            return inc.issubset(exc)
        # 딕셔너리일 때
        elif str(type(inc)) == "<class 'dict'>":
            for idx in inc.keys():
                if inc[idx] != exc[idx]:
                    return False
            else:
                return True
        # 나머지 iterable
        elif inc.__iter__:
            # 순서가 있을 때는 exc를 점점 좁혀서 찾기

            for val in inc:

                if val not in exc:
                    return False
                else:
                    tmp = inc.index(val)
                    # order가 있으면 tmp를 통해서 좁혀나가기. order가 없으면 그 원소만 제거.
                    exc = exc[tmp+1:] if order else exc[0:tmp] + exc[tmp+1:]

            return True

        else: return False

# iterable에서 중복 원소 제거 리스트 추출
def remove_multiple(iterable):
    res = []
    for idx, val in enumerate(iterable):
        if val not in iterable[0:idx]: res.append(val)
    return res

#함수 합성 등
def join_map(obj, func):

    res = {}

    #func가 object일 때
    if str(type(func)) == "<class 'dict'>":
        if func.get(obj):
            return func.get(obj)
        # obj가 딕셔너리면
        elif str(type(obj)) == "<class 'dict'>":
            for keyo in obj.keys():
                res[keyo] = join_map(obj[keyo], func)
                return res
        # obj가 iterable이면서 함수값 형식으로 표현 가능할 때
        elif obj.__iter__:
            for val in obj:
                try:
                    res[val] = func[val]
                except:
                    raise Exception("Invalid input type")
        else:
            raise Exception("Cannot calculate!")


    # func가 함수
    elif str(type(func)) == "<class 'function'>":

        #iterable이 아니면 그냥 함수 값 출력
        if not obj.__iter__ and func(obj):
            return func(obj)

        # dictionary면 키값: 함수값 형식으로 출력
        elif str(type(obj)) == "<class 'dict'>":
            for keyo in obj.keys():
                res[keyo] = join_map(obj[keyo], func)
                return res

        # obj가 iterable이면서 함수값 형식으로 표현 가능할 때
        elif obj.__iter__:
            for val in obj:
                try:
                    res[val] = func(val)
                except:
                    raise Exception("Invalid input type")

# 리스트 곱하기, 예시  [[1,2,3],[4,5,6]] => [[1,4], [1,5], [1,6], [2,4], [2,5], [2,6], [3,4], [3,5], [3,6]]
def product_list(args):
    if len(args) == 0: return []
    elif len(args) == 1:
        return list(map(lambda x: [x], args[0]))
    elif len(args) ==2:
        return [ [x, y] for x in args[0] for y in args[1]]
    else:
        sub_result = product_list(args[:-1])
        return [ [*x, y] for x in sub_result for y in args[-1]]

def object_in(elem, obj):
    return elem in obj

# 합칩합 구하는 함수
def list_union(*args):
    res = []
    for x in args:
        # iterable할 때는 풀어서...
        if x.__iter__:
            for y in x:
                if y not in res: res.append(y)
        else:
            if x not in res: res.append(x)

#교집합 구하는 함수
def list_intersection(*args):
    # 초기값 설정
    res = []
    for x in args[0]:
        tmp = True
        for y in args:
            tmp = tmp and (x in y)
        if tmp: res.append(x)

    return res










from hangul.hangul_utils import *
# 사용가능함수 :
# __all__ = ["split_syllable_char", "split_syllables",
#            "join_jamos", "join_jamos_char",
#            "CHAR_INITIALS", "CHAR_MEDIALS", "CHAR_FINALS"]

print(hex(ord("ㄱ")), hex(ord("ㄳ")), hex(ord("ㅎ")), hex(ord("ㅏ")))

from hangul.utils import hangul_manipulation

X = hangul_manipulation.Antispoof("ㅂㅏ#ㅗ")

print(X.join_by_syllable())
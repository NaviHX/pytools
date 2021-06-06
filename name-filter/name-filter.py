from xpinyin import Pinyin
import argparse

target_initials = ''
line_count = 1

pinyin = Pinyin()
parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', required=True, help='Target Initials')

args = parser.parse_args()
target_initials = args.target
target_initials = target_initials.upper()

while True:
    try:
        name = input()
        initials = pinyin.get_initials(name, '')
        if initials == target_initials:
            print(line_count, ':', name)
        line_count += 1
    except Exception as e:
        break

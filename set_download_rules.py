import re


def set_download_rules():
    rules = []
    stop = False
    grading = {'A': '仙草', 'B': '糧草', 'C': '乾草', 'D': '枯草', 'E': '毒草'}
    intro = ('分級標準如下:\n'
             'A:仙草\n'
             'B:糧草\n'
             'C:乾草\n'
             'D:枯草\n'
             'E:毒草\n'
             '請選擇要制定規則的分級'
             '輸入完後請按Enter，輸入esc則結束\n')
    while not stop:
        print(intro)
        in1 = input().upper()
        if in1 not in 'ABCDE':
            print('請重新輸入')
            continue
        else:
            print('ok')
            


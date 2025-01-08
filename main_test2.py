import time


index = 1
while index < 10:
    file = open('data.txt', 'a')
    file.write(f'hello{index}')
    file.write('\n')
    print(index)
    file.close()
    # 睡眠10s
    time.sleep(10)
    index = index + 1

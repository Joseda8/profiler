import time

i = 0
my_list = [0] * (10**7)
while i < 2:
    my_list += my_list
    my_list = [x ** 2 for x in my_list]
    time.sleep(0.5)
    i += 1
    print(f"i: {i}")

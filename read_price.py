from time import sleep

while True:
    f_a = open('BTCUSDT.txt', 'r')
    f_b = open('ETHUSDT.txt', 'r')
    print(f_a.read())
    print(f_b.read())
    f_a.close()
    f_b.close()
    sleep(0.5)

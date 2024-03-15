import time
START = time.time()
def _start():
    global _START
    START = time.time()

AVG = 0
def end():
    global AVG
    t = time.time() - START
    AVG += .1 * (t - AVG)
    print(f'{AVG:.2f}, {t:.2f}')
    _start()
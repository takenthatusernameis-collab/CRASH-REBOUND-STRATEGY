import multiprocessing as mp
import os

def worker_init(a, b, c):
    import builtins
    builtins._W = (a, b, c)

def worker(x):
    import builtins
    return sum(builtins._W) + x

if __name__ == "__main__":
    print("start methods:", mp.get_all_start_methods())
    try:
        ctx = mp.get_context("fork")
        with ctx.Pool(processes=2, initializer=worker_init, initargs=(1, 2, 3)) as pool:
            r = pool.map(worker, [10, 20, 30], chunksize=8)
        print("POOL OK:", r)
    except Exception as e:
        print("POOL FAILED:", type(e).__name__, e)
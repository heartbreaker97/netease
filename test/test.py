import threadpool
def hello(m, n, o):
    print("m = %s, n = %s, o = %s" % (m, n, o))


if __name__ == '__main__':
    # 方法1
    lst_vars_1 = ['1', '2', '3']
    lst_vars_2 = ['4', '5', '6']
    func_var = [(lst_vars_1, None), (lst_vars_2, None)]
    pool = threadpool.ThreadPool(2)
    requests = threadpool.makeRequests(hello, func_var)
    [pool.putRequest(req) for req in requests]
    pool.wait()
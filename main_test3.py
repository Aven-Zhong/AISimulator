import datetime
from scipy.optimize import differential_evolution

# end_time = datetime.datetime.now()
# milliseconds = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
# print("结束时间:", milliseconds)
# data = [[1, 2, 3],
#         [2,3,4]]
# fit = [2.2 , 3.3]
# # 将pid参数和适应度值写入文件
# file_name = end_time.strftime("%Y-%m-%d-%H-%M-%S")
# file = open(f'./PINN_roll/file/log/{file_name}.txt', 'a')
#
# for i in range(len(data)):
#     file.write(str(data[i]))
#     file.write(' ')
#     file.write(str(fit[i]))
#     file.write('\n')
# file.close()


def fitness_func(x):
    return x**2


def callback(x, convergence):
    print(x, convergence)


if __name__ == '__main__':
    bounds = [(0.0, 9.0)]
    # 运行差分进化算法
    start_time = datetime.datetime.now()
    milliseconds = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("开始时间:", milliseconds)
    result = differential_evolution(fitness_func,
                                    bounds,
                                    callback=callback,
                                    strategy='best1bin',
                                    # workers=4,
                                    maxiter=1000,
                                    popsize=15,
                                    disp=False)  # 打印内置的收敛信息
    print(f"Optimal parameters: {result.x}")
    print(f"最优值: {result.fun}")
    print(f"是否成功退出：{result.success}")
    print(f"迭代次数：{result.nit}")

    print(f"终止原因：{result.message}")

    end_time = datetime.datetime.now()
    milliseconds = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("结束时间:", milliseconds)
    print("总时间", end_time - start_time)
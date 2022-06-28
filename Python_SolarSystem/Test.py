import numpy as np
import time
import random
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar

from VerletPython import PythonSolver
from VerletMP import MPSolver
from VerletCython import CythonSolver
from VerletOpenCL import OpenCLSolver
from VerletOdeint import OdeintSolver


def generateParticle(N):
    m = np.random.rand(N) * random.randint(1, 10000)
    r0 = np.random.rand(N, 2) * random.randint(1, 10000)
    v0 = np.random.rand(N, 2) * random.randint(1, 10000)
    return m, r0, v0


if __name__ == "__main__":
    i_bar = [1, 2, 3, 4, 5, 6, 7, 8]
    bar = IncrementalBar('Countdown', max = len(i_bar))
    bar.next()

    T = 1
    k = T * 10
    
    N = np.array([50, 100, 200])
    
    n_experiments = 3    
    
    time_res = np.zeros((N.shape[0], 4))

    for i in range(N.shape[0]):
        
        m, r0, v0 = generateParticle(N[i])
        
        for j in range(n_experiments):
            start_time = time.time()
            PythonSolver(m, r0, v0, T, k)
            end_time = time.time()
            time_res[i, 0] += end_time - start_time
            
            start_time = time.time()
            CythonSolver(m, r0, v0, T, k)
            end_time = time.time()
            time_res[i, 1] += end_time - start_time
            
            start_time = time.time()
            MPSolver(m, r0, v0, T, k)
            end_time = time.time()
            time_res[i, 2] += end_time - start_time
            
            start_time = time.time()
            OpenCLSolver(m, r0, v0, T, k)
            end_time = time.time()
            time_res[i, 3] += end_time - start_time

        bar.next()    

    time_res /= n_experiments

    bar.next() #1

    weight = np.array([1989000, 0.33, 4.9, 0.6, 6, 1900, 570, 87, 103]) * 1e24
    distance = np.array([0, 58, 108, 152, 228, 778, 1433, 2877, 4437]) * 1e9
    speed = np.array([0, 48, 35, 30, 24, 13, 10, 7, 5]) * 1e3

    M = weight.shape[0]

    r0 = np.zeros((M, 2), np.double)
    r0[:, 0] = distance

    v0 = np.zeros((M, 2), np.double)
    v0[:, 1] = speed
    
    r, v = OdeintSolver(weight, r0, v0, T, k)
    r1, v1 = PythonSolver(weight, r0, v0, T, k)
    r2, v2 = CythonSolver(weight, r0, v0, T, k)
    r3, v3 = MPSolver(weight, r0, v0, T, k)
    r4, v4 = OpenCLSolver(weight, r0, v0, T, k)
    
    error1 = ((r - r1) ** 2).mean()
    error2 = ((r - r2) ** 2).mean()
    error3 = ((r - r3) ** 2).mean()
    error4 = ((r - r4) ** 2).mean()
    
    fig, ax = plt.subplots()
    ax.bar(['Python', 'Cython', 'MP', 'OpenCL'], [error1, error2, error3, error4])
    plt.title("Погрешность относительно odeint")
    plt.savefig('TestResults/errors.png')
    plt.clf()
    plt.cla()

    bar.next() #2
    
    plt.plot(N, time_res[:, 0], color = "green", label = 'Python')
    plt.plot(N, time_res[:, 1], color = 'orange', label = 'Cython')
    plt.plot(N, time_res[:, 2], color = 'blue', label = 'MP')
    plt.plot(N, time_res[:, 3], color = 'black', label = 'OpenCL')
    plt.xlabel('Кол-во частиц, N')
    plt.ylabel('Время, t')
    plt.title("Время работы")
    plt.legend()
    plt.savefig('TestResults/runtime.png')
    plt.clf()
    plt.cla()
    
    bar.next() #3
    
    plt.plot(N, time_res[:, 0] / time_res[:, 0], color = 'green', label = 'Python')
    plt.plot(N, time_res[:, 0] / time_res[:, 1], color = 'orange', label = 'Cython')
    plt.plot(N, time_res[:, 0] / time_res[:, 2], color = 'blue', label = 'MP')
    plt.plot(N, time_res[:, 0] / time_res[:, 3], color = 'black', label = 'OpenCL')
    plt.xlabel('Кол-во частиц, N')
    plt.title("Ускорение")
    plt.legend()
    plt.savefig('TestResults/accelerations.png')
    plt.clf()
    plt.cla()

    bar.next() #4
    bar.finish()
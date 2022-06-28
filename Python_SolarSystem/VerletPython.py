import numpy as np
from numpy.linalg import norm

G = float(6.6743e-11)

def acceleration(m, r):
    N = m.shape[0]
    a = np.zeros((N, 2), np.double)
    for i in range(N):
        for j in range(N):
            if i != j and i != 0:
                a[i] += G * m[j] * (r[j] - r[i]) / (norm(r[j] - r[i]) ** 3)
    return a

def PythonSolver(m, r, v, T, k):
    N = m.shape[0]
    res_r = np.zeros((N, 2, k))
    res_v = np.zeros((N, 2, k))
    dt = T / (k - 1)
    cur_a = acceleration(m, r)
    res_r[:, : , 0] = r
    res_v[:, : , 0] = v
    for i in range(1, k):
        r = r + v * dt + 0.5 * cur_a * (dt ** 2)
        next_a = acceleration(m, r)
        v = v + 0.5 * (cur_a + next_a) * dt
        cur_a = next_a
        res_r[:, : , i] = r
        res_v[:, : , i] = v
    return res_r, res_v
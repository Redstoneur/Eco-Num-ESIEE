# cython: language_level=3
import numpy as np
cimport numpy as cnp

cdef double d_tc_dt(double tc, double t, double ta, double ws, double i):
    a = ((ws ** 2) / 1600) * 0.4 + 0.1
    b = ((i ** 1.4) / 73785) * 130
    return -(1 / 60) * a * (tc - ta - b)

def simulate_cython(double tc0, cnp.ndarray[cnp.double_t, ndim=1] t, double ta, double ws, double i):
    cdef double tc = tc0
    cdef int n = t.shape[0]
    cdef cnp.ndarray[cnp.double_t, ndim=1] tc_list = np.empty(n, dtype=np.float64)
    tc_list[0] = tc
    cdef double dt_local
    cdef int idx
    for idx in range(1, n):
        dt_local = t[idx] - t[idx - 1]
        tc += d_tc_dt(tc, t[idx - 1], ta, ws, i) * dt_local
        tc_list[idx] = tc
    return tc_list
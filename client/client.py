import socket

from scipy.stats import qmc
import math
import numpy as np

def print_out(bytes_str):
    if bytes_str.startswith(b'[matlab]'):
        print(bytes_str.decode("utf-8"))

def random_x_array(N, d):
    sampler = qmc.LatinHypercube(d=d)
    sample = sampler.random(n=N)
    return sample

def run_monster(X):
    N, d = X.shape
    coefs = np.random.randn(d)
    res = np.zeros((N,))
    for i in range(d):
        if i % 7 == 0:
            res[:] += coefs[i] * X[:, i]
        elif i % 7 == 1:
            res[:] += coefs[i] * X[:, i] ** 2
        elif i % 7 == 2:
            res[:] += coefs[i] * X[:, i] ** 3
        elif i % 7 == 3:
            res[:] += coefs[i] * (2.71828 ** X[:, i])/1.71828
        elif i % 7 == 4:
            res[:] += coefs[i] * np.sin(2*np.pi*X[:, i])/2
        elif i % 7 == 5:
            continue
            # res[:] += 0
        elif i % 7 == 6:
            res[:] += coefs[i] * 4*(X[:, i]-0.5) ** 2
    return res

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('localhost', 9889))
    print("Connection to server established!")
    print_out(sock.recv(1024)) # handshake (request method type)
    method_no = 1
    socket.sendall(method_no.to_bytes(4, 'little')) # send method type
    
    print_out(sock.recv(1024)) # request X dimensions
    N, d = 1, 89
    dimensions = N.to_bytes(4, 'little')
    dimensions += d.to_bytes(4, 'little')
    socket.sendall(dimensions) # send X dimensions

    print_out(sock.recv(1024)) # request X
    X = random_x_array(N, d)
    socket.sendall()

    print_out(sock.recv(1024)) # request y
    y = run_monster(X)
    socket.sendall(y)

    print_out(sock.recv(1024)) # recv params or error

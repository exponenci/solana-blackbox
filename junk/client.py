# import socket
# import array
# from scipy.stats import qmc
# import math
# import numpy as np

# def print_out(bytes_str):
#     if bytes_str.startswith(b'[matlab]'):
#         print(bytes_str.decode("utf-8"))

# def random_x_array(N, d):
#     sampler = qmc.LatinHypercube(d=d)
#     sample = sampler.random(n=N)
#     return sample

# def run_monster(X):
#     N, d = X.shape
#     coefs = np.random.randn(d)
#     res = np.zeros((N,))
#     for i in range(d):
#         if i % 11 == 0:
#             res[:] += coefs[i] * X[:, i]
#         # elif i % 7 == 1:
#         #     res[:] += coefs[i] * X[:, i] ** 2
#         # elif i % 7 == 2:
#         #     res[:] += coefs[i] * X[:, i] ** 3
#         # elif i % 7 == 3:
#         #     res[:] += coefs[i] * (2.71828 ** X[:, i])/1.71828
#         # elif i % 7 == 4:
#         #     res[:] += coefs[i] * np.sin(2*np.pi*X[:, i])/2
#         # elif i % 7 == 5:
#         #     continue
#         #     # res[:] += 0
#         # elif i % 7 == 6:
#         #     res[:] += coefs[i] * 4*(X[:, i]-0.5) ** 2
#     return res

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#     hostname = socket.gethostname()
#     print(hostname)
#     sock.connect(('192.168.96.3', 9889))
#     print("Connection to server established!")
#     print_out(sock.recv(1024)) # handshake (request method type)
#     method_no = 3
#     sock.sendall(method_no.to_bytes(4, 'little')) # send method type
    
#     print_out(sock.recv(1024)) # request X dimensions
#     N, d = 1, 89
#     dimensions = N.to_bytes(4, 'little')
#     dimensions += d.to_bytes(4, 'little')
#     sock.sendall(dimensions) # send X dimensions

#     print_out(sock.recv(1024)) # request X
#     X = random_x_array(N, d)
#     print("X.shape", X.shape)
#     sock.sendall(X)

#     print_out(sock.recv(1024)) # request y
#     y = run_monster(X)
#     print("y", y.shape, y, type(y[0]))
#     sock.sendall(y)

#     print_out(sock.recv(1024)) # request target_count
#     target_count = 6
#     sock.sendall(target_count.to_bytes(4, 'little')) # send target_count

#     print_out(sock.recv(1024)) # all data is sent

#     print('waiting for results...')
#     for i in range(6):
#         tmp = sock.recv(1024)
#         doubles_sequence = array.array('d', tmp)
#         print(i, doubles_sequence)

import socket
import array
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
        if i % 11 == 0:
            res[:] += coefs[i] * X[:, i]
        # elif i % 7 == 1:
        #     res[:] += coefs[i] * X[:, i] ** 2
        # elif i % 7 == 2:
        #     res[:] += coefs[i] * X[:, i] ** 3
        # elif i % 7 == 3:
        #     res[:] += coefs[i] * (2.71828 ** X[:, i])/1.71828
        # elif i % 7 == 4:
        #     res[:] += coefs[i] * np.sin(2*np.pi*X[:, i])/2
        # elif i % 7 == 5:
        #     continue
        #     # res[:] += 0
        # elif i % 7 == 6:
        #     res[:] += coefs[i] * 4*(X[:, i]-0.5) ** 2
    return res

def get_xy(test_id):
    x = np.loadtxt('client/tests/data/Xmatrix' + str(test_id) + '.txt', dtype=np.float64, delimiter=',')
    y = np.loadtxt('client/tests/data/ymatrix' + str(test_id) + '.txt', dtype=np.float64, delimiter=',')
    return x, y

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    hostname = socket.gethostname()
    print(socket.gethostbyname(hostname))
    sock.connect(('10.193.88.211', 9889))
    print("Connection to server established!")
    for i in range(1, 6):
        x, y = get_xy(i)
        for i in range(1, 4):
            method_no = i
            sock.sendall(method_no.to_bytes(4, 'little')) 
            N, d = x.shape
            dimensions = N.to_bytes(4, 'little')
            dimensions += d.to_bytes(4, 'little')
            sock.sendall(dimensions)

            print("X.shape", x.shape)
            sock.sendall(x)

            print("y", y.shape, type(y[0]))
            sock.sendall(y)

            target_count = 1
            sock.sendall(target_count.to_bytes(4, 'little')) # send target_count

            tmp = sock.recv(1024)
            print(tmp)
            print(array.array('I', tmp))
            if array.array('I', tmp)[0] == 0:                
                print('waiting for results...')
                for i in range(1):
                    tmp = sock.recv(1024)
                    doubles_sequence = array.array('d', tmp)
                    print(i, doubles_sequence)
                print('exp done\n')
            else:
                print('error occured!')
                tmp = sock.recv(1024)
                print(tmp.decode())
                print('exp done\n')

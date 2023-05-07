import os
import socket

from sensitivity_analysis import SensitivityAnalysisMAbstract
from utils import Serializer


class MatlabSensitivityAnalysisM(SensitivityAnalysisMAbstract):
    SOCKET_FRAME_SIZE = os.getenv('MATLAB_DEFAULT_BUFFER_SIZE')

    server_hostname = os.getenv('MATLAB_SERVER_HOSTNAME')
    server_address = os.getenv('MATLAB_SERVER_ADDRESS')
    server_port = os.getenv('MATLAB_SERVER_PORT')
    serializer = Serializer() # one (static) serializer for all connections 

    def __init__(self, method_id, *args, **kwargs) -> None:
        # run in other process? multi connection?
        super().__init__(*args, **kwargs)
        self.method_id = method_id
        self.sock = None
        self.addr = kwargs.get('addr', self.server_address)
        self.port = kwargs.get('port', self.server_port)
        return self

    def __del__(self):
        self.close_connection()

    def connect_to_server(self, addr=None, port=None, **kwargs) -> bool:
        """ connects to matlab server
            returns False if already connected
        """
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if addr is not None and port is not None:
                self.addr = addr
                self.port = port
            self.sock.connect((self.addr, self.port))
            return True
        return False
    
    def close_connection(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def run(self, x=None, y=None, **kwargs):
        if x is not None and y is not None:
            self.accept_run_data(x, y, **kwargs) # parent method
        self.connect_to_server(**kwargs)
        self.send_chunk([
            [[self.method_id], 'INT32'],
            [[*self.x.shape, self.target_params_count], 'INT32'],
            [self.x],
            [self.y],
        ])
        most_valuable_params = self.expect_data('DOUBLE') # target_count indeces of most valuable params
        return most_valuable_params

    def send_chunk(self, args_chunk):
        for args_data in args_chunk:
            self.send_to_server(*args_data)

    def send_to_server(self, data, dtype: str = 'pass'):
        if dtype != 'pass':
            bytes_to_send = self.serializer.serialize(data, dtype)
            self.sock.sendall(bytes_to_send)
        else:
            self.sock.sendall(data)

    def expect_data(self, dtype: str = 'pass'):
        raw_bytes = self.sock.recv(self.SOCKET_FRAME_SIZE)
        if dtype == 'pass':
            return raw_bytes
        received_data = self.serializer.deserialize(raw_bytes, dtype)
        return received_data


class PCEMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(1, *args, **kwargs)
        return self


class GPMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(2, *args, **kwargs)
        return self


class PCGPMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(3, *args, **kwargs)
        return self

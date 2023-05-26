import os
import socket
from typing import Any, List, Tuple

from .sensitivity_analysis import SensitivityAnalysisMAbstract
from utils.serializer import Serializer
from .experiment_container import SARunnerContainer


class MatlabSensitivityAnalysisM(SensitivityAnalysisMAbstract):
    SOCKET_FRAME_SIZE = int(os.getenv('MATLAB_DEFAULT_BUFFER_SIZE', 1024))

    server_hostname = os.getenv('MATLAB_SERVER_HOSTNAME')
    server_address = os.getenv('MATLAB_SERVER_ADDRESS')
    server_port = os.getenv('MATLAB_SERVER_PORT')
    serializer = Serializer() # one (static) serializer for all connections 

    def __init__(self, method_id, *args, **kwargs) -> None:
        # run in other process? multi connection?
        super().__init__(*args, **kwargs)
        self.method_id = method_id
        self._sock = None
        self.addr = kwargs.get('addr', self.server_address)
        self.port = kwargs.get('port', self.server_port)

    def __del__(self):
        self.close_connection()

    def connect_to_server(self, addr=None, port=None, **kwargs) -> bool:
        """ connects to matlab server
            returns False if already connected
        """
        if self._sock is None:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if addr is not None and port is not None:
                self.addr = addr
                self.port = port
            self._sock.connect((self.addr, self.port))
            return True
        return False
    
    def close_connection(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def run(self, exp_container: SARunnerContainer, **kwargs) -> SARunnerContainer:
        # connect to matlab server
        self.connect_to_server(**kwargs)
        
        # sending data to run SA method
        self._send_chunk([
            [[self.method_id], 'INT32'],
            [[*exp_container.x_mat.shape, exp_container.target_params_count], 'INT32'],
            [exp_container.x_mat],
            [exp_container.y_vec],
        ])

        # getting info wether error occured
        exp_container.is_error = self._expect_data('INT32')[0] != 0
        if not exp_container.is_error:
            # if there is no error then get result - best params to be optimized
            exp_container.result = self._expect_data('DOUBLE')
        else:
            # otherwise get error message
            error_info = self._expect_data('STRING')
            exp_container.result = ''.join(list(map(chr, error_info)))

        # close connection
        self.close_connection()
        
        # return experiment container
        return exp_container

    def _send_chunk(self, args_chunk: List[Tuple[Any, str]]) -> None:
        for args_data in args_chunk:
            self._send_data(*args_data)

    def _send_data(self, data: Any, dtype: str = 'pass') -> None:
        if dtype != 'pass':
            bytes_to_send = self.serializer.serialize(data, dtype)
            self._sock.sendall(bytes_to_send)
        else:
            self._sock.sendall(data)

    def _expect_chunk(self, args_chunk: List[str]) -> Any:
        result = list()
        for args_data in args_chunk:
            result.append(self._expect_data(*args_data))
        return result

    def _expect_data(self, dtype: str = 'pass') -> Any:
        raw_bytes = self._sock.recv(self.SOCKET_FRAME_SIZE)
        if dtype == 'pass':
            return raw_bytes
        received_data = self.serializer.deserialize(raw_bytes, dtype)
        return received_data


class PCEMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(1, *args, **kwargs)


class GPMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(2, *args, **kwargs)


class PCGPMatlabM(MatlabSensitivityAnalysisM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(3, *args, **kwargs)

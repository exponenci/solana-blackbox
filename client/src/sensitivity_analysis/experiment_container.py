import os
from dataclasses import dataclass
from typing import Any

import numpy as np
from io import StringIO

@dataclass
class ExperimentContainer:
    x_mat: np.array = None
    y_vec: np.array = None
    target_params_count: int = 6
    sa_method_id: int = -1
    is_error: bool = False
    result: Any = None # can be error message or params

    def read_from_files(self, x_filename: str, y_filename: str) -> bool:
        if not os.path.isfile(x_filename) or not os.path.isfile(y_filename):
            return False
        self.x_mat = np.loadtxt(x_filename, ndmin=2, dtype=np.float64, delimiter=',')
        self.y_vec = np.loadtxt(y_filename, ndmin=1, dtype=np.float64, delimiter=',')
        return self

    def set(self, x_mat: np.array, y_vec: np.array, **kwargs):
        self.x_mat = x_mat
        self.y_vec = y_vec
        for k, v in kwargs.items():
            setattr(self, k, v)

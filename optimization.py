
# chosed params to optimize: 31, 63, 51, 8, 44
# var2: 63.0, 37.0, 48.0, 42.0, 53.0, 32.0
# var3: 4.0, 11.0, 13.0, 28.0, 20.0, 14.0

from blackbox import blackbox, limit_params, TARGET_CONFIG, SingleContainerMultiNode, TomlConfig


from pySOT.experimental_design import SymmetricLatinHypercube
from pySOT.strategy import DYCORSStrategy
from pySOT.surrogate import RBFInterpolant, CubicKernel, LinearTail
from pySOT.optimization_problems import Ackley, Levy, OptimizationProblem
from pySOT.utils import progress_plot
from poap.controller import ThreadController, SerialController, BasicWorkerThread
import numpy as np
import os


os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"

cluster = SingleContainerMultiNode(TARGET_CONFIG)    
params_ids = list(sorted([31, 63, 51, 8, 44]))
func_to_opt = limit_params(blackbox, cluster, params_ids)
# [-22965.805 -22632.594 -22229.965 -22323.924 -22882.127 -22568.36 ]
# RESULT X: [7.20000000e+04 1.92000000e+02 6.30303062e-01 9.45454545e+02
#  2.63636364e+02] -> Y = 22965.805


# [-22810.18  -24261.154 -23617.502 -23150.574 -22228.352]
# [<poap.strategy.EvalRecord object at 0x7fcf8c5abc70>, <poap.strategy.EvalRecord object at 0x7fcf8c5abc10>, <poap.strategy.EvalRecord object at 0x7fcf8c5abcd0>, <poap.strategy.EvalRecord object at 0x7fcf8c5abb20>, <poap.strategy.EvalRecord object at 0x7fcf8c5cda30>]
# RESULT X: [1.16363636e+03 5.23636364e+04 2.27272727e+02 7.27272764e-01
#  1.57090909e+02]
max_evals = 5
input_dimensionality = len(params_ids)
default_values = np.array(TomlConfig().get_values_list())[params_ids]
lower_bounds = default_values * 0.8
upper_bounds = default_values * 1.2

print(default_values)
print(lower_bounds)
print(upper_bounds)

rbf = RBFInterpolant(
    dim=input_dimensionality, lb=lower_bounds, ub=upper_bounds, kernel=CubicKernel(), tail=LinearTail(input_dimensionality))
slhd = SymmetricLatinHypercube(dim=input_dimensionality, num_pts=2*(input_dimensionality+1))

class BlackBox(OptimizationProblem):
    def __init__(self, dim=input_dimensionality):
        self.dim = dim
        self.lb = lower_bounds
        self.ub = upper_bounds
        self.int_var = np.array([])
        self.cont_var = np.arange(0, dim)
        self.info = str(dim) + "-dimensional black box"
        
    def eval(self, x):
        return -func_to_opt(x)[1][0]

black_box = BlackBox()

results_serial = np.zeros((max_evals, ))

controller = SerialController(objective=black_box.eval)
controller.strategy = DYCORSStrategy(
    max_evals=max_evals, opt_prob=black_box, asynchronous=False, 
    exp_design=slhd, surrogate=rbf, num_cand=100*input_dimensionality,
    batch_size=1)

result = controller.run()
results_serial = np.array([o.value for o in controller.fevals if o.value is not None])

index = np.argmin(results_serial)
print(results_serial)
print(controller.fevals)
x = controller.fevals[index].params[0]
print("RESULT X:", x)

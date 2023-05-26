import numpy as np
from pySOT.experimental_design import SymmetricLatinHypercube
from pySOT.strategy import DYCORSStrategy
from pySOT.surrogate import RBFInterpolant, CubicKernel, LinearTail
from pySOT.optimization_problems import OptimizationProblem
from poap.controller import SerialController

from blackbox import blackbox, limit_params, TomlConfig
import consts


def run_optimization_experiment(cluster=None,
                                narrowed_blackbox=None, 
                                params_ids: list = consts.EXPERIMENT_PARAM_IDS, 
                                max_evals: int = consts.OPTIMIZATION_MAX_EVALS, 
                                bounds_coefs: tuple = consts.OPTIMIZATION_BOUNDS_COEFS):
    if len(bounds_coefs) != 2:
        raise AttributeError("bound_coefs must contain 2 values, for lower and upper bounds")
    if cluster is not None:
        narrowed_blackbox = limit_params(blackbox, cluster, params_ids)
    elif narrowed_blackbox is None:
        raise AttributeError("either cluster or narrowed_blackbox must be given in arguments")

    default_values = np.array(TomlConfig(base_filename=consts.BASE_CONFIG).get_values_list())[params_ids]
    lower_bounds = default_values * bounds_coefs[0]
    upper_bounds = default_values * bounds_coefs[1]
    dimensionality = len(params_ids)
    
    rbf = RBFInterpolant(dim=dimensionality, 
                         lb=lower_bounds, 
                         ub=upper_bounds, 
                         kernel=CubicKernel(), 
                         tail=LinearTail(dimensionality))
    slhd = SymmetricLatinHypercube(dim=dimensionality, 
                                   num_pts=2 * (dimensionality + 1))


    class BlackBox(OptimizationProblem):
        def __init__(self, dim, lb, ub):
            self.dim = dim
            self.lb = lb
            self.ub = ub
            self.int_var = np.array([])
            self.cont_var = np.arange(0, dim)
            self.info = str(dim) + "-dimensional black box"
            
        def eval(self, x):
            return -narrowed_blackbox(x)[1][0] # opt problem finds minimum, whereas we want to maximize tps


    black_box = BlackBox(dimensionality, 
                         lower_bounds, 
                         upper_bounds)

    results_serial = np.zeros((max_evals,))

    controller = SerialController(objective=black_box.eval)
    controller.strategy = DYCORSStrategy(max_evals=max_evals, 
                                         opt_prob=black_box, 
                                         asynchronous=False, 
                                         exp_design=slhd,
                                         surrogate=rbf,
                                         num_cand=100 * dimensionality,
                                         batch_size=1)

    result = controller.run()
    results_serial = np.array([o.value for o in controller.fevals if o.value is not None])

    index = np.argmin(results_serial)
    print(f"TPS values: {-results_serial}")
    x = controller.fevals[index].params[0]
    print(f"X-params (for given params_ids): {x}")
    return x, -result

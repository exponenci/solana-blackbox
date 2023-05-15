### VARIANT 1

class Pipeline():
    def __init__(self) -> None:
        self.act_list = list()
    def add_node(self, node):
        # node (params from prev node) -> params for next node
        self.act_list.append(node)
    def run(self, first_params):
        params = first_params
        for n in self.act_list:
            params = n.run(*params)
        # results are saved in some nodes
        return params

for config in configs:
    Pipeline().Run()
    

## ////
config = ConfigSetting('filename').SomeSetting()

blockchain = ChainRunner(configs_params, runntimes=5, saveresult='somefile')
exp = ExperimentContainer(blockchain.get_run_results())

methods[exp.method].run(exp)
    # sa_method = PCEMatlabM(label='kek')
    # target_params = sa_method.run(x, y)

so_method = Surrogate(save_result=True, label='kek')
res_config = so_method.Optimize(target_params)

blockchain = ChainRunner(res_config)


"""after all so_methods runs"""
chose_best_label(all_so_results)
    

# blockchain runs on given params and returns tps -> 
#    -> SAmethod finds 6 target params on given data -> 
#    -> SOmethod runs on this 6 target params ->
#    -> one more run on new params of SO ->
#    -> compare with other SAmethods

# 1 - we want to determine best sa_method 
# 2 - we want to define most valuable params
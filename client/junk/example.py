### VARIANT 1
blockchain = ChainRunner(configs_params)
blockchain.RunNTimes(5)
sa_method = PCEMatlabM(label='kek')
x, y = blockchain.get_data()
target_params = sa_method.run(x, y)
so_method = Surrogate(save_result=True, label='kek')
so_method.OptimizeAndRun(blockchain, target_params)

"""after all so_methods runs"""
chose_best_label(all_so_results)
    

# blockchain runs on given params and returns tps -> 
#    -> SAmethod finds 6 target params on given data -> 
#    -> SOmethod runs on this 6 target params ->
#    -> one more run on new params of SO ->
#    -> compare with other SAmethods

# 1 - we want to determine best sa_method 
# 2 - we want to define most valuable params
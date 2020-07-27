import numpy as np
from scipy.optimize import minimize


class HyperparameterOptimizer:
    def __init__(self,model,bounds,hyperparameters = None):
        self.model = model
        self.bounds = bounds
        
        #if hyperparameters == None then optimize all of them
        if hyperparameters is None:
            self.hypers = self.model
        else:
            self.hypers = hyperparameters
        
        
    def optimize(self):
        ''' 
        manually optimize log margnial likelihood using 
        GPy.kern hyperparameters

        '''
        #get old hyperparameters as starting location
        x0 = self.model[:]
        #x0 = np.random.uniform(self.bounds[:,0],self.bounds[:,1],len(self.bounds))
        res = minimize(self.objective,x0, bounds = self.bounds)

        print(res)
        
    def objective(self,x):
        '''objective function for optimization

        '''
        self.model[:] = x
        

        return -float(
            self.model.log_likelihood()) - self.model.log_prior()


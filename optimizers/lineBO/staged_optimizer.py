import numpy as np
import matplotlib.pyplot as plt
import logging

from . import optimizer as lineOpt
from ..stageopt import optimizer as stageOpt


class StageLineOpt(lineOpt.LineOpt):
    def __init__(self, bounds, acq, stageInput, **kwargs):
        '''
        Combines line optimizer and StageOpt, a safe optimizer
        
        Arguments
        ---------
        bounds             independant variable bounds
        acq                function to be safely minimized of the form f(x,*args)
        stageInput         dictionary containing settings for safe optimization
            - 'gprf'       - GaussianProcessRegressor objects to model the objective function
            - 'ofun'       - objective functions
            - 'gprc'       - GaussianProcessRegressor(s) object to model the constraint functions
            - 'cfun'       - constraint function(s) of the form f_i(x,*args) >= h_i
            - 'h'          - list of constraint values h_i
            - 'beta'       - beta function for UCB (default: 1)
            - 'epsilon_max - max epsilon to stop safe expansion (default: 0.1)
            - 'T0'         - steps budget for expansion step (default: 5)
            - 'n_grid'     - # of 1D grid points along line (default: 100)

        Optional Arguments
        ------------------
        args                  arguments for optimization function (default: [])
        oracle                direction choosing oracle (default: random)
        x0                    initial point to start optimization (default: np.random.uniform)
        verbose               display diagnostic plotting (default: False)
        T                     LineOpt step budget (default:10)
        tol                   convergence tolerance (default: 1e-6)

 
        '''
        super().__init__(bounds,acq,**kwargs)
        self.stageInput = stageInput


    def optimize(self):
        #rewrite optimizer while using StageOpt to optimize along the subdomain
        self.t = 0
        #while self.t < self.T:
        logging.info(f'doing LineOpt step {self.t}')
        #generate direction from oracle
        self.l = np.vstack((self.l,self.oracle(self.dim)))

        #find subspace bounds
        self._get_subdomain_bounds()
        
        self._find_safe_subspace()


    def _find_safe_subspace(self):
        #create a custom 1D domain for StageOpt
        D = np.array([self._map_subdomain(s) for s in np.linspace(self.lower[self.t],
                                                                  self.upper[self.t],
                                                                  self.stageInput['n_grid'])])

        #add info from LineOpt
        self.stageInput['X0'] = self.x[self.t].reshape(-1,self.dim)
        logging.info(D)
        self.stageInput['D']  = D
        
        #do observations
        self.stageInput['Y0'] = self.stageInput['ofun'](self.stageInput['X0']).reshape(-1,1)

        C0 = np.empty(len(self.stageInput['cfun']))
        for i in range(len(C0)): 
            C0[i] = self.stageInput['cfun'][i](self.stageInput['X0'])
        self.stageInput['C0'] = C0.reshape(-1,1)
            
        safeOptimizer = stageOpt.StageOpt(self.stageInput) 

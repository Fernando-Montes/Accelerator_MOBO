import numpy as np

import logging
import multiprocessing

from .lineBO import lineOpt

class Result:
    def __init__(self,x,f):
        self.x = x
        self.f = f


class BlackBoxOptimizer:
    def __init__(self):
        pass

    def minimize(self, bounds, func, args = [], x0 = None):
        pass

class LineOpt(BlackBoxOptimizer):
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    def minimize(self, bounds, func, args = [], x0 = None):
        opt = lineOpt.LineOpt(bounds,
                              func, args = args, x0 = x0,
                              **self.kwargs)
        opt.optimize()
        res = Result(opt.x[-1], opt.f[-1])

        return res

class ParallelLineOpt(BlackBoxOptimizer):
    '''ParallelLineOpt - parallelized version of lineopt

    Uses multiprocessing to simultaniously try to find
    localized maxima using a collection of different initial
    starting locations.

    Attributes
    ----------
    
    n_cpus : int
        Number of cpus used in parallelization
    
    kwargs : dict
        Optional argmuents for LineOpt instance

    '''
    def __init__(self,**kwargs):
        self.n_cpus = kwargs.get('n_cpus',
                                 multiprocessing.cpu_count())
        self.kwargs = kwargs

    def minimize(self, bounds, f, args = [], x0 = None):
        '''minimize - performs parallelized minimization

        Parameters
        ----------
        bounds : ndarray, shape (n,2)
            Upper and lower bounds for each input variable

        f : callable
            Function of the form f(x, *args) to be minimized

        args : list, optional
            Optional arguments for f, Default: []

        x0 : ndarray, shape (m,n), optional
            Set of initial guesses, if not given, 10 points are
            randomly selected inside input space
        '''
        
        n_points = 10
        dim = bounds.shape[-1]
        
        if x0 is None:
            x0 = np.random.uniform(bounds[:,0],
                                   bounds[:,1],
                                   (n_points,dim))

        else:
            if len(x0) < self.n_cpus:
                #add in random points to efficiently use resources
                additional_points = np.random.uniform(bounds[:,0],
                                                      bounds[:,1],
                                                      (self.n_cpus - len(x0) -1,dim))
                x0 = np.vstack((x0,additional_points))
            
        #create list of parameters
        l = [[bounds,f,args,x0[i]] for i in range(len(x0))]

        logging.info(f'Using parallel LineOptimization with {len(x0)} initial points')
        p = multiprocessing.Pool(self.n_cpus)
        result = p.starmap(self._parallel_minimize,l)
        p.close()
        p.join()

        #return the point that most minimizes the function
        i = np.argmax(np.array(result).T[1])
        return Result(*result[i])
        
    def _parallel_minimize(self, bounds, func, args, x0):
        '''function called in multiprocessing Pool class'''
        opt = lineOpt.LineOpt(bounds,func,args = args, x0 = x0, **self.kwargs)
        opt.optimize()
        return [opt.x[-1],opt.f[-1]]
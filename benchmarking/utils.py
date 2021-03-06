import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


from GaussianProcessTools.multi_objective import pareto

class HVTracker:
    def __init__(self,problem,r):
        self.max_HV = self._get_max_hypervolume(problem,r)
        self.r = r
        
    def get_PF_error(self,pf):
        return (self.max_HV - \
                pareto.get_hypervolume(pf,self.r)) / self.max_HV

    def _get_max_hypervolume(self,problem,r):
        #calculates the max hypervolume for a given problem and
        # r

        F = problem.pareto_front()
        
        return pareto.get_hypervolume(F,r)

def plot_problem(problem,bounds):
    fig,ax = plt.subplots(2,1)

    n = 20
    x = np.linspace(*bounds[0],n)
    y = np.linspace(*bounds[1],n)
    xx,yy = np.meshgrid(x,y)
    pts = np.vstack((xx.ravel(),yy.ravel())).T

    v = problem.evaluate(pts)
    
    for i in [0,1]:
        ax[i].pcolor(xx,yy,v.T[i].reshape(n,n))
    

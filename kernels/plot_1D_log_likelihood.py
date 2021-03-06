import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import gpflow
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from gpflow.utilities import print_summary, set_trainable
import tensorflow_probability as tfp
from scipy.stats import multivariate_normal
import numdifftools as nd
from scipy.optimize import minimize

def f(X):
    return multivariate_normal.pdf(X,mean=0.0,cov=1)

def get_mll(l,model):
    n = 10**l[0]
    model.kernel.lengthscales.assign(n)
    return -model.log_marginal_likelihood().numpy()


def main():
    #specify bounds
    bounds = (-10,10)

    #specify cov
#    cov = np.diag(np.arange(1,3)**2)
#    print(cov)
    #cov = 1
    #create training points
    n_train = 250
    X = np.linspace(*bounds,n_train).reshape(-1,1)
    Y = f(X).reshape(-1,1)
    print(np.max(Y))
    print(-nd.Hessian(f)(0.0)/(2*f(0.0)))

    #    print(X)
#    print(Y)
    
    model = gpflow.models.GPR(data = (X,Y),
                              kernel = gpflow.kernels.RBF(variance=1e-5,
                                                          lengthscales=2.0))

    model.likelihood.variance.assign(1e-5)
    set_trainable(model.likelihood.variance,False)
    set_trainable(model.kernel.variance,False)
    
    lengthscale_bounds = (-3, 3)
    n_samples = 150
    l = np.linspace(*lengthscale_bounds,n_samples).reshape(-1,1)
    #lpts = np.meshgrid(l,l)
    #L = np.vstack((lpts[0].ravel(),lpts[1].ravel())).T

    lml = []
    for pt in l:
        lml.append(-get_mll(pt,model))
    
    lml = np.array(lml)

    res = minimize(get_mll,x0=1.0,args = (model))
    print(res)
    print(10**res.x)
    print(10**res.x / f(0.0))
    fig,ax = plt.subplots()
    ax.semilogx(10**l.ravel(),lml)
    
    #do optimization
    model.kernel.lengthscales.assign(1.0)
    opt = gpflow.optimizers.Scipy()
    opt.minimize(model.training_loss,model.trainable_variables)

    print_summary(model)
    print(model.log_marginal_likelihood())
main()
plt.show()

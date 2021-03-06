#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  example of the Metropolis algorithm single walker chain
#  a difficult distribution: the Rosenbrock “banana” pdf
#

import math
import numpy as np
from numpy import random as rnd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn


def modelpdf(x1,x2):
    "the Rosenbrock “banana” pdf"
    return np.exp(-(100.*(x2-x1**2)**2+(1.0-x1)**2)/20.0)

# define chain parameters: N of chain entries, N of first entries to discard, step size
n = 100000; nburn=1000; nsel=1; step = 1.0
# set initial walker position
x = 0.; y = 0.
chain = []
chain.append([x,y])

# precompute a set of random numbers
nrand = n
delta = zip(rnd.uniform(-step,step,nrand),rnd.uniform(-step,step,nrand)) #random inovation, uniform proposal distribution

naccept = 0; i = 0; ntry = 0
for nd in range(n):
    if not i%nrand:  # if ran out of random numbers generate some more
       delta = zip(rnd.uniform(-step,step,nrand),rnd.uniform(-step,step,nrand)) #random inovation, uniform proposal distribution
       i = 0
    xtry = x + delta[i][0] # trial step
    ytry = y + delta[i][1]
    gxtry = modelpdf(xtry,ytry)
    gx = modelpdf(x,y)
    #
    # now accept the step with probability min(1.0,gxtry/gx);
    # if not accepted walker coordinate remains the same and is also added to the chain
    #
    if gxtry > gx:
        x = xtry; y=ytry
        naccept += 1
    else:
        aprob = gxtry/gx # acceptance probability
        u = rnd.uniform(0,1)
        if u < aprob:
            x = xtry; y= ytry
            naccept += 1
    #
    # whatever the outcome, add current walker coordinates to the chain
    #
    chain.append([x,y])
    i += 1; ntry += 1

print "Generated n ",n," samples with a single walker"
print "with acceptance ratio", 1.0*naccept/ntry

#
# plot results:
#
x = np.arange(-10.0,10.0,0.05); y = np.arange(-1.0,100,0.05)

# build grid for countours of the actual target pdf
X, Y = np.meshgrid(x,y)
# compute target pdf values at the grid points
Z = modelpdf(X,Y)

plt.rc('font', family='sans-serif', size=16)
fig=plt.figure(figsize=(10,15))
plt.subplot(211)
plt.title('Metropolis')
plt.plot(chain)

#
# plot the chain
#
ax = plt.subplot(212)
xh = zip(*chain)[0]; yh = zip(*chain)[1]
xh = xh[nburn::nsel]; yh=yh[nburn::nsel]
plt.hist2d(xh,yh, bins=100, norm=LogNorm(), normed=1)
plt.colorbar()

#
# plot theoretical contours of the target pdf
#
dlnL2= np.array([2.30, 9.21]) # contours enclosing 68.27 and 99% of the probability density
Lmax = modelpdf(0.0,0.0)
lvls = sorted(Lmax/np.exp(0.5*dlnL2))
cs=plt.contour(X,Y,Z, linewidths=(1.0,2.0), colors='black', norm = LogNorm(), levels = lvls, legend='target pdf' )

plt.title('MCMC samples vs target distribution')

labels = ['68.27%', '99%']
for i in range(len(labels)):
    cs.collections[i].set_label(labels[i])

plt.legend(loc='upper center')
plt.ylabel('y')
plt.xlabel('x')

plt.show()

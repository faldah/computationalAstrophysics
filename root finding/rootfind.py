#
# l07: numerical root finding: scipy vs simple bisect
#
import math
import numpy as np
from scipy.optimize import fsolve
from scipy.optimize import brentq
from scipy.optimize import brenth
from scipy.optimize import ridder
from scipy.optimize import newton
from scipy.optimize import bisect as bsect
from matplotlib import pylab as plt
import socket
import time

def rootsearch(f,a,b,dx):
    x1 = a; f1 = f(a)
    x2 = a + dx; f2 = f(x2)
    while f1*f2 > 0.0:
        if x1 >= b:
            return None,None
        x1 = x2; f1 = f2
        x2 = x1 + dx; f2 = f(x2)
    return x1,x2

def bisect(f,x1,x2,switch=0,epsilon=1.0e-9):
    f1 = f(x1)
    if f1 == 0.0:
        return x1
    f2 = f(x2)
    if f2 == 0.0:
        return x2
    if f1*f2 > 0.0:
        print('Root is not bracketed')
        return None
    n = math.ceil(math.log(abs(x2 - x1)/epsilon)/math.log(2.0))
    for i in range(int(n)):
        x3 = 0.5*(x1 + x2); f3 = f(x3)
        if (switch == 1) and (abs(f3) >abs(f1)) and (abs(f3) > abs(f2)):
            return None
        if f3 == 0.0:
            return x3
        if f2*f3 < 0.0:
            x1 = x3
            f1 = f3
        else:
            x2 =x3
            f2 = f3
    return 0.5*(x1 + x2)

def roots(f, a, b, eps=1e-6):
    print ('The roots on the interval [%f, %f] are:' % (a,b))
    xroots = []
    while 1:
        x1,x2 = rootsearch(f,a,b,eps)
        if x1 != None:
            a = x2
            root = bisect(f,x1,x2,1,eps)
            if root != None:
                pass
                xroots.append(round(root,-int(math.log(eps, 10))))      
                print (round(root,-int(math.log(eps, 10))))
        else:
            print ('\nDone')
            return xroots
            break
            
def rootsscipy(f, a, b, eps=1e-6):
    print ('The roots on the interval [%f, %f] are:' % (a,b))
    while 1:
        x1,x2 = rootsearch(f,a,b,eps)
        if x1 != None:
            a = x2
            #root = fsolve(f,x1,xtol=eps)
            #root = ridder(f,x1,x2,xtol=eps)
            #root = newton(f,0.5*(x1+x2),fprime=fprime,fprime2=fprime2,tol=eps)
            root = newton(f,0.5*(x1+x2),fprime=fprime,tol=eps)
            if root != None:
                pass
                print (round(root,-int(math.log(eps, 10))))
        else:
            print ('\nDone')
            break

f=lambda x: x**4*np.sin(x) #x*math.cos(x-4)
fprime = lambda x: x**4*np.cos(x)+4.0*x**3*np.sin(x)
#fprime2 = lambda x: -np.sin(x)

a = -5.0; b = 5.0; eps = 1.0e-6

t1 = time.time()
rootsscipy(f,a,b,eps)

t2 = time.time()
print "scipy routine finished in ",t2-t1," seconds"

t1 =time.time()
xroots = roots(f, a, b, eps)

t2 = time.time()
print "bisection finished in ",t2-t1," seconds"

#            
# plot results:
#

x = np.linspace(a,b,100)
plt.plot(x,f(x),xroots,f(np.array(xroots)),'ro')
plt.grid(b=1)
plt.show()

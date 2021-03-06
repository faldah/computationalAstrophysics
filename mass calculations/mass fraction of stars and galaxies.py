
#  calculate mass fraction of stars and total mass in galaxies of mass >M* and halos of mass >M
#  it uses Sheth et al. halo mass function to calculate mass fraction of total mass
#

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import interpolate as intp
from scipy import integrate
import math


#
# prepare stellar mass function fit
#

lms = np.arange(3.0,13.5,0.1) # grid of stellar masses
ms  = 10.0**lms
#
# Baldry et al. 2012 stellar mass function for small M*
#
lmstar = 10.66
phi1s = 3.96e-3; alpha1=-0.35; phi2s = 6.9e-4; alpha2=-1.57;

mstar = 10.**lmstar; mus =  ms/mstar
dnms1 = np.exp(-mus)*(phi1s*mus**alpha1 + phi2s*mus**alpha2)/mstar

#
# using Bernardi et al. 2013 double Schechter fit for large M*
#

mstarb = 0.0094e9; phisb = 1.040e-2; alphab = 1.665; betab = 0.255
phisg = 0.675e-2; mstarg = 2.7031e9; gammag = 0.296

gammanorm = math.gamma(alphab/betab)

musb = ms/mstarb; musg = ms/mstarg
dnms2 = (phisb*np.exp(-musb**betab)*musb**(alphab-1)/(mstarb)*betab/gammanorm +
         phisg*musg**(gammag-1)*np.exp(-musg)/mstarg)

#
# multiply by M* to get dn/dlnM and take maximum 
# of Baldry et al. and Bernardi et al stellar mass functions to construct the composite
#
dnms1 = dnms1*ms; dnms2 = dnms2*ms
dnms = np.maximum(dnms1,dnms2)

ldnms = np.log10(dnms) + lms # multiply one more time by M* to integrate in log10(M)

sdnms = intp.UnivariateSpline(lms, ldnms, s=0.0)

def sifunc(logms):
    return 10.0**(sdnms(logms))

si1 = integrate.quadrature(sifunc,lms[0],lms[-1])[0]

sfrac = np.zeros_like(lms); si2 = np.zeros_like(lms)

for i, lmsd in enumerate(lms):
    si2[i] = integrate.quadrature(sifunc,lmsd,lms[-1])[0]
    sfrac[i]=si2[i]/si1
    #print lmsd, sfrac[i]


#
nmspl = intp.UnivariateSpline(lms,10.**(np.log10(dnms)+lms), s=0.0)
nmstot = nmspl.integral(lms[0],np.inf)
for lmsd in lms:
    nmsm = nmspl.integral(lmsd,np.inf)
    #print "log10 M* = %.2f"%lmsd, "frac(>M*)=%.5f"%(nmsm/nmstot)
   
#
#  now mass functions
#

#
#  read power spectrum
#
fname = 'matter_power_kmax10000.dat'
k, Pk = np.loadtxt(fname,usecols=(0,1),unpack=True)

#
# set relevant cosmological parameters
#
h = 0.7; Omega_m = 0.276; rho_mean = 2.77e11*h*h*Omega_m # in Msun/Mpc^3

#
# set a desired grid of masses and corresponding radii
#
lM = np.arange(1.0,16,0.1)
M = 10.0**lM; R = (3.0*M/(4.0*math.pi*rho_mean))**(1.0/3.0)
# check if the mass limits and k limits are appropriate (see e.g. Murray et al. arxiv/1306.6721)
if not ((k[0]*R[-1]<0.1) and (k[-1]*R[0]>3.0)):
    raise ValueError("***WARNING! limits on k and R(M) will result in accurate sigma!***")

def W2(k,R):
    kR = k*R
    return (3.0*(np.sin(kR)-kR*np.cos(kR))/(kR**3))**2

def dW2dM(k,R):
    kR = k*R
    return (np.sin(kR)-kR*np.cos(kR))*(np.sin(kR)*(1.0-3.0/(kR**2))+3.0*np.cos(kR)/kR)

sig = np.zeros_like(M)
factor1 = 0.5/math.pi**2

for i, md in enumerate(M):
    sfunc = Pk*W2(k,R[i])*k*k
    sig[i] = np.sqrt(factor1*integrate.simps(sfunc,k))

#
# now compute dln(sigma)/dlnM 
#
dsdm = np.zeros_like(M)
factor2 = 1.5/math.pi**2

for i, md in enumerate(M):
    sfunc = Pk*dW2dM(k,R[i])/(k**2)
    spl = intp.UnivariateSpline(k, sfunc, s=0.0)
    dsdm[i] = factor2*spl.integral(k[0],np.inf)/sig[i]**2/R[i]**4

lsig = np.log(sig); logm = np.log(M);

#
# renormalize sigma(M) to a desired sigma8
#
#
sR = intp.UnivariateSpline(R, sig, s=0.0)
R8 = 8.0/h; sig8 = sR(R8)
sig8new = 0.8
print "sigratio =", sig8new/sig8
sig = sig*sig8new/sig8

#
# mass function
#
def f_PS(nu):
    return np.sqrt(2.0/math.pi)*np.exp(-0.5*nu**2)

def f_SMT(nu):
    nup2 = (0.840833*nu)**2       
    return 0.644*(1.0+1.0/nup2**0.3)*np.sqrt(nup2*0.5/math.pi)*np.exp(-0.5*nup2)      

# define peak height 
delc = 1.69; nu = delc/sig
#
# compute mass-functions in the Press-Schechter 1974 and Sheth et al. 2001 approximations
#
dndlnM_PS = rho_mean/M*abs(dsdm)*nu*f_PS(nu)
dndlnM_SMT = rho_mean/M*abs(dsdm)*nu*f_SMT(nu)

# function to integrate for mass fractions in ln(nu)
dni = f_SMT(nu)
lnu = np.log(nu)

slmf = intp.UnivariateSpline(lnu,np.log10(dni),s=0.0)

def mfunci(lnud):
    return 10.0**slmf(lnud)
    
hi1 = integrate.quadrature(mfunci,lnu[0],lnu[-1])[0]

hfrac = np.zeros_like(logm); hi2 = np.zeros_like(logm)

for i, lnud in enumerate(lnu):
    hi2[i] = integrate.quadrature(mfunci,lnud,lnu[-1])[0]
    hfrac[i]=hi2[i]/hi1
    #print lM[i], hfrac[i], hi1, hi2[i]
 
#
#  plot 
#

fig1 = plt.figure()
plt.rc('text', usetex=True)
plt.rc('font',size=16,**{'family':'sans-serif','sans-serif':['Helvetica']})
plt.rc('xtick.major',pad=10); plt.rc('xtick.minor',pad=10)
plt.rc('ytick.major',pad=10); plt.rc('ytick.minor',pad=10)
plt.xscale('log'); #plt.yscale('log')

plt.plot(ms,si2/si1,linewidth=1.5,c='b',label='stellar mass frac. $>M_*$')
plt.plot(M,hfrac,linewidth=1.5,c='magenta',label='total mass frac. $>M_{\\rm tot}$')

plt.xlabel('$\\log_{10} M_*, M_{\\rm tot}$')
plt.ylabel('fraction of mass at $>M$')
plt.title('fraction of mass')
plt.legend(loc='lower left')

plt.show()


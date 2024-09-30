import numpy as np
from scipy.integrate import quad,quad_vec
import matplotlib.pyplot as plt
import warnings
from numba import jit 
from scipy import linalg
from tqdm.notebook import tqdm
import qutip as qt
from qutip.nonmarkov.heom import HEOMSolver, DrudeLorentzPadeBath, BathExponent

lam=input()
@jit(nopython=True)
def bose(ν,T):
    if T==0:
        return 0
    return 1/(np.exp(ν/T)-1)
@jit(nopython=True)
def spectral_density(w,lam,gamma):
    return 2*w*lam*gamma/(gamma**2 + w**2)
@jit(nopython=True)
def γ(ν,w,w1,T,t,gamma,lam=lam):
    var=t*t*np.exp(1j*(w-w1)/2 *t)*spectral_density(ν,lam,gamma)*(np.sinc((w-ν)/2 * t)*np.sinc((w1-ν)/2 * t))*(bose(ν,T)+np.exp(-abs(ν)/5e8))
    var+=t*t*np.exp(1j*(w-w1)/2 *t)*spectral_density(ν,lam,gamma)*(np.sinc((w+ν)/2 * t)*np.sinc((w1+ν)/2 * t))*bose(ν,T)
    return var

x=input()
ϵ=1e-x
Γplus=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,w,w,T,t,wc), 0, np.Inf,epsabs=ϵ,epsrel=ϵ,quadrature="gk21")[0];
Γminus=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,-w,-w,T,t,wc), 0, np.Inf,quadrature="gk21",epsabs=ϵ,epsrel=ϵ)[0];
Γplusminus=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,w,-w,T,t,wc), 0, np.Inf,quadrature="gk21",epsabs=ϵ,epsrel=ϵ)[0];
Γzplus=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,0,w,T,t,wc), 0, np.Inf,quadrature="gk21",epsabs=ϵ,epsrel=ϵ)[0];
Γzminus=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,0,-w,T,t,wc), 0, np.Inf,quadrature="gk21",epsabs=ϵ,epsrel=ϵ)[0];
Γzz=lambda w,T,t,wc :quad_vec(lambda ν: γ(ν,0,0,T,t,wc), 0, np.Inf,quadrature="gk21",epsabs=ϵ,epsrel=ϵ)[0];
def ξ1(ν,w,T,t,wc,lam=lam):
    if ν==w:
        return 0
    if ν==-w:
        return 0
    return (t*t*(1/2j)*(np.sinc((w-ν)*t/2)**2 -np.sinc((w+ν)*t/2)**2)*\
    spectral_density(ν,lam,wc)*((bose(ν,T)+1)/(w-ν) + (bose(ν,T))/(w+ν) ))
def ξ2(ν,w,T,t,wc,lam=lam):
    if ν==w:
        return 0
    if ν==-w:
        return 0
    return (t*t*(1/2j)*np.sinc((ν)*t/2)*spectral_density(ν,lam,wc)*\
    (np.sinc((w+ν)*t/2)-np.sinc((w-ν)*t/2))*ν*((bose(ν,T)+1)/(w-ν) + (bose(ν,T))/(w+ν) ))

ξ=lambda w,T,t,wc :quad_vec(lambda ν: ξ1(ν,w,T,t,wc), 0, np.Inf,epsabs=ϵ,epsrel=ϵ)[0];
ξz=lambda w,T,t,wc :quad_vec(lambda ν: ξ2(ν,w,T,t,wc), 0, np.Inf,epsabs=ϵ,epsrel=ϵ)[0];

def M(w,T,t,f1,f2,f3,wc,ls=False):
    f=f1-1j*f2
    gplus=Γplus(w,T,t,wc);
    gminus=np.conj(Γminus(w,T,t,wc));
    gzplus=Γzplus(w,T,t,wc);
    gzminus=Γzminus(w,T,t,wc);
    gamma=np.abs(f)**2 * (gplus+gminus);
    gammazmas=f3*(np.conj(f)*gzplus+f*gzminus);
    gammazmenos=f3*(np.conj(f)*gzplus+f*gzminus);
    plusminus=f**2 *Γplusminus(w,T,t,wc);
    gammazz=2*f3**2 *Γzz(w,T,t,wc);
    xiz=0#2*f3*ξz(w,T,t,wc)[1];
    xi=0#abs(f)^2 *ξ(w,T,t,wc)[1];
    if ls:
        xiz=2*f3*ξz(w,T,t,wc);
        xi=np.abs(f)**2 *ξ(w,T,t,wc);
        #return xi
    #matriz=np.array([[-gamma,xiz*f2+np.real(gammazmas),xiz*f1+np.imag(gammazmas)],[ 
     #   np.real(gammazmenos)-f2*xiz,np.real(plusminus)-(gamma/2)-gammazz,-xi-np.imag(plusminus)],[
      #  np.imag(gammazmas)-f1*xiz ,xi-np.imag(plusminus),-np.real(plusminus)-(gamma/2)-gammazz]])
    #r=[np.abs(f)**2 *(gplus-gminus)/2,f3*np.real((-f*gzminus+np.conj(f)*gzplus)),f3*np.imag(((f*gzminus+np.conj(f)*gzplus)))]
    matriz=np.array([[-gamma,xiz*f2+np.real(gammazmas),-xiz*f1-np.imag(gammazmas)],[ 
        -np.imag(gammazmas)+f1*xiz,-np.real(plusminus)-(gamma/2)- gammazz,xi-np.imag(plusminus)],[
        np.real(gammazmas)-f2*xiz, -xi-np.imag(plusminus),np.real(plusminus)-(gamma/2)-gammazz]])
    r=[np.abs(f)**2 *(gplus-gminus)/2,f3*np.real(f*(np.conj(gzplus)-gzminus)),-f3*np.imag(f*(np.conj(gzplus)-gzminus))]
    return matriz,r


def dynamics(w,T,t,f1,f2,f3,wc,a,ls=False):
    s1=np.array([[0,1],[1,0]])
    s2=np.array([[0,-1j],[1j,0]])
    s3=np.array([[1,0],[0,-1]])
    if t==0:
        return (np.eye(2)/2)+a[0]*s3+a[2]*s2+a[1]*s1
    m,r=M(w,T,t,f1,f2,f3,wc,ls)
    if (f1==f2)&(f2==0):
        m=m[1:,1:]
        exponential=linalg.expm(m)
        pauli_coeff=(exponential-np.eye(2))@np.linalg.inv(m)@r[1:]
        with_pauli=pauli_coeff[0]*s1+pauli_coeff[1]*s2
        transient=exponential@a[1:]
        transient_base=transient[0]*s1+transient[1]*s2
        total=(np.eye(2)/2)+transient_base+with_pauli+a[0]*s3
        return total
    exponential=linalg.expm(m)
    pauli_coeff=(exponential-np.eye(3))@np.linalg.inv(m)@r
    with_pauli=pauli_coeff[0]*s3+pauli_coeff[1]*s1+pauli_coeff[2]*s2
    transient=exponential@a
    transient_base=transient[0]*s3+transient[1]*s1+transient[2]*s2
    total=(np.eye(2)/2)+transient_base+with_pauli
    return total

def rotation(data,diagonal=True):
    rotated= [linalg.expm(-(1j*sz/2)*t[i])@np.array(data)[i]@linalg.expm((1j*sz/2)*t[i]) for i in tqdm(range(len(t)), desc=f"Computing for all t, currently on ")]
    if diagonal:
        return np.array([rotated[i][0,0] for i in range(len(data))])
    else:
        return np.array([rotated[i][0,1] for i in range(len(data))])


def rc_correction(Hsys,gamma,Q,T):
    dot_energy, dot_state = Hsys.eigenstates()
    deltaE = dot_energy[1] - dot_energy[0]
    gamma2 = deltaE / (2 * np.pi * gamma)
    wa = 2 * np.pi * gamma2 *   gamma # reaction coordinate frequency
    g = np.sqrt(np.pi * wa * lam / 2.0)  # reaction coordinate coupling
    g = np.sqrt(np.pi * wa * lam / 4.0)  # reaction coordinate coupling Factor over 2 because of diff in J(w) (I have 2 lam now)
    #nb = (1 / (np.exp(wa/w_th) - 1))

    NRC = 200

    Hsys_exp = qt.tensor(qt.qeye(NRC), Hsys)
    Q_exp = qt.tensor(qt.qeye(NRC), Q)
    a = qt.tensor(qt.destroy(NRC), qt.qeye(2))

    H0 = wa * a.dag() * a + Hsys_exp
    # interaction
    H1 = (g * (a.dag() + a) * Q_exp)

    H = H0 + H1

    #print(H.eigenstates())
    energies, states = H.eigenstates()
    rhoss = 0*states[0]*states[0].dag()
    for kk, energ in enumerate(energies):
        rhoss += (states[kk]*states[kk].dag()*np.exp(-energies[kk]/T)) 

    #rhoss = (states[0]*states[0].dag()*exp(-beta*energies[0]) + states[1]*states[1].dag()*exp(-beta*energies[1]))

    rhoss = rhoss/rhoss.norm()
    P12RC = qt.tensor(qt.qeye(NRC), qt.basis(2,0) * qt.basis(2,1).dag())

    P12RC = qt.expect(rhoss,P12RC)


    P11RC = qt.tensor(qt.qeye(NRC), qt.basis(2,0) * qt.basis(2,0).dag())

    P11RC = qt.expect(rhoss,P11RC)
    return np.array([[P11RC,P12RC],[np.conjugate(P12RC),1-P11RC]])

def fidelity(ρ,σ):
    return [linalg.sqrtm(ρ[i]@σ[i]).trace()**2 for i in range(len(ρ))]
def change_base(data):
    ρ11=np.array([data[i][0,0] for i in range(len(data))])
    ρ12=np.array([data[i][0,1] for i in range(len(data))])
    ρ21=np.array([data[i][1,0] for i in range(len(data))])
    ρ22=np.array([data[i][1,1] for i in range(len(data))])
    return np.array([np.array([[ρ22[i],ρ21[i]],[ρ12[i],ρ11[i]]]) for i in range(len(data))] )




def cumulant(w,T,t,f1,f2,f3,gamma,a,b,c,ls):
    data_xx=[dynamics(w,T,i,f1,f2,f3,gamma,[a,b,c],ls) for i in tqdm(t, desc=f"Computing for all t, currently on ")]
    ρ11=np.array([data_xx[i][0,0] for i in range(len(data_xx))])
    ρ12=np.array([data_xx[i][0,1] for i in range(len(data_xx))])
    ρ21=np.array([data_xx[i][1,0] for i in range(len(data_xx))])
    ρ22=np.array([data_xx[i][1,1] for i in range(len(data_xx))])
    sz=np.array([[1,0],[0,-1]])
    return data_xx_rotated=[linalg.expm(-(1j*(sz/2)) *t[i])@data_xx[i]@linalg.expm((1j*(sz/2)) *t[i]) for i in tqdm(range(len(t)), desc=f"Computing for all t, currently on ")]
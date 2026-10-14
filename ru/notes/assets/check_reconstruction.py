"""Axisymmetric joint moment reconstruction; units ell*=tau*=v_g=1.
Global (not local angular) moments. HG phase. No absorption: shape factors out.
Independent photon trajectories are used only for validation.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.special import logsumexp, i0e
from scipy.optimize import minimize
from pathlib import Path
OUT=Path(__file__).parent

def moments(t,g):
    b=1+g
    m=-np.expm1(-t)
    ss=np.array([(1-np.exp(-b*t))/3,(1+2*np.exp(-b*t))/3])
    # transverse and longitudinal tensor eigenvalues; gamma1=1.
    aa=t+np.expm1(-t)
    bb=quad(lambda u: (1-np.exp(-(t-u)))*np.exp(-b*u),0,t,epsabs=1e-12)[0]
    rr=2*np.array([(aa-bb)/3,(aa+2*bb)/3])
    cross=quad(lambda u: np.exp(-(t-u))*np.exp(-b*u),0,t,epsabs=1e-12)[0]
    xs=np.array([(m-cross)/3,(m+2*cross)/3])
    return np.array([m/t,np.exp(-t),rr[1]/t**2,2*rr[0]/t**2,ss[1],xs[1]/t,2*xs[0]/t])

def single(g):
    ss_z=(1+2*g*g)/3; ss_p=2*(1-g*g)/3
    return np.array([(1+g)/2,g,(1+ss_z+g)/3,ss_p/3,ss_z,(g+ss_z)/2,ss_p/2])

def tail_target(t,g):
    lam=t/(1-g); p0=np.exp(-lam); p1=lam*p0; w=1-p0-p1
    z=np.array([1,1,1,0,1,1,0])
    return (moments(t,g)-p0*z-p1*single(g))/w, (p0,p1,w)

def nodes(n):
    # z and transverse area inside unit ball; relative azimuth integrated.
    z,wz=leggauss(n); a,wa=leggauss(n); u,wu=leggauss(n)
    a=(a+1)/2; wa=wa/2
    phi=2*np.pi*np.arange(2*n)/(2*n)
    zz,aa,uu,pp=np.meshgrid(z,a,u,phi,indexing='ij')
    perp=(1-zz*zz)*aa
    cross=np.sqrt(perp*(1-uu*uu))*np.cos(pp)
    F=np.stack([zz,uu,zz*zz,perp,uu*uu,zz*uu,cross],axis=-1).reshape(-1,7)
    # dV dOmega, after integrating absolute azimuth of x: pi(1-z²) da dz *2pi du dphi.
    w=(wz[:,None,None,None]*(1-z[:,None,None,None]**2)*wa[None,:,None,None]*wu[None,None,:,None]*np.ones((1,1,1,2*n)))
    w=w.reshape(-1); w=w/w.sum()
    return F,np.log(w)

def fit(target,F,lw,start=None,indices=None):
    inds=np.arange(7) if indices is None else np.asarray(indices)
    Fs=F[:,inds]; tar=target[inds]
    scale=np.maximum(np.sqrt(np.average((Fs-tar)**2,axis=0,weights=np.exp(lw))),.02)
    X=(Fs-tar)/scale
    def fun(a):
        logw=lw+X@a; lz=logsumexp(logw); w=np.exp(logw-lz)
        return lz,w@X
    r=minimize(fun,np.zeros(len(inds)) if start is None else start*scale,jac=True,method='BFGS',options={'gtol':2e-9,'maxiter':400})
    lam=r.x/scale
    l=lw+Fs@lam; w=np.exp(l-logsumexp(l))
    return lam,w,float(np.max(np.abs(w@F-target))),r.nit

def mc(t,g,n,seed):
    rng=np.random.default_rng(seed)
    r=np.zeros((n,3)); s=np.zeros_like(r);s[:,2]=1
    clock=np.zeros(n);counts=np.zeros(n,dtype=int)
    active=np.arange(n)
    while len(active):
        dt=rng.exponential(1-g,len(active))
        remaining=t-clock[active]; ds=np.minimum(dt,remaining)
        r[active]+=ds[:,None]*s[active];clock[active]+=ds
        active=active[dt<remaining]
        if not len(active):break
        counts[active]+=1
        h=rng.random(len(active))
        mu=2*h-1 if g==0 else (1+g*g-((1-g*g)/(1-g+2*g*h))**2)/(2*g)
        phi=2*np.pi*rng.random(len(active))
        old=s[active]; ref=np.zeros_like(old);ref[:,2]=1
        ref[np.abs(old[:,2])>.9]=[1,0,0]
        e=np.cross(ref,old);e/=np.linalg.norm(e,axis=1)[:,None]
        b=np.cross(old,e)
        s[active]=mu[:,None]*old+np.sqrt(np.maximum(0,1-mu*mu))[:,None]*(np.cos(phi)[:,None]*e+np.sin(phi)[:,None]*b)
    y=r/t
    F=np.column_stack([y[:,2],s[:,2],y[:,2]**2,(y[:,:2]**2).sum(1),s[:,2]**2,y[:,2]*s[:,2],(y[:,:2]*s[:,:2]).sum(1)])
    return y,s,F,counts

def binned_joint(lam,bins,logZ):
    # Integrate inside each bin. Avoid assigning sparse quadrature nodes to bins.
    q,w=leggauss(6); aa,wa=leggauss(20);aa=(aa+1)/2;wa=wa/2
    out=np.zeros((len(bins)-1,len(bins)-1))
    for i,(lo,hi) in enumerate(zip(bins[:-1],bins[1:])):
        z=(lo+hi)/2+(hi-lo)*q/2;wz=w*(hi-lo)/2
        for j,(ulo,uhi) in enumerate(zip(bins[:-1],bins[1:])):
            u=(ulo+uhi)/2+(uhi-ulo)*q/2;wu=w*(uhi-ulo)/2
            zz,a,uu=np.meshgrid(z,aa,u,indexing='ij')
            rp=(1-zz**2)*a;k=lam[6]*np.sqrt(rp*(1-uu**2))
            exponent=lam[0]*zz+lam[1]*uu+lam[2]*zz**2+lam[3]*rp+lam[4]*uu**2+lam[5]*zz*uu
            exponent+=np.log(i0e(k))+np.abs(k)-logZ
            weights=3/8*wz[:,None,None]*wa[None,:,None]*wu[None,None,:]*(1-zz**2)
            out[i,j]=(weights*np.exp(exponent)).sum()
    return out

def main():
    F,lw=nodes(18); results=[]
    for g,t in [(0.,1.),(.9,1.),(.9,3.),(.9,10.)]:
        target,weights=tail_target(t,g)
        lam,w,err,nit=fit(target,F,lw)
        Ffine,lwf=nodes(26)
        ff=lwf+Ffine@lam;wf=np.exp(ff-logsumexp(ff));refinement=float(np.max(abs(wf@Ffine-target)))
        # Refit separately to ensure constraints hold on refined quadrature.
        lam,wf,err,nit2=fit(target,Ffine,lwf,start=lam)
        y,s,mcF,counts=mc(t,g,120000,20261008+int(10*t)+int(100*g))
        all_res=float(np.max(abs(mcF.mean(0)-moments(t,g))))
        tail=mcF[counts>=2];se=tail.std(0,ddof=1)/np.sqrt(len(tail))
        zscore=float(np.max(abs(tail.mean(0)-target)/se))
        bins=np.linspace(-1,1,17)
        empirical=np.histogram2d(tail[:,0],tail[:,1],bins=[bins,bins])[0];empirical/=empirical.sum()
        approx=binned_joint(lam,bins,logsumexp(lwf+Ffine@lam))
        assert abs(approx.sum()-1)<1e-6
        # Compare joint maxent with product of its own marginals: missing correlation only.
        independent=approx.sum(1)[:,None]*approx.sum(0)[None,:]
        l1=float(abs(empirical-approx).sum());l1product=float(abs(empirical-independent).sum())
        entry={'g':g,'T':t,'tail_mass':weights[2],'moment_residual':err,'coarse_to_fine_residual':refinement,'max_MC_moment_zscore':zscore,'MC_size':len(tail),'joint_z_mu_L1':l1,'product_marginals_z_mu_L1':l1product,'lambda':lam.tolist(),'target':target.tolist()}
        results.append(entry);print(json.dumps(entry),flush=True)
        np.savez_compressed(OUT/f'case_g{g}_T{t}.npz',bins=bins,mc=empirical,joint=approx,product=independent,target=target,lam=lam)
    (OUT/'checks.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()

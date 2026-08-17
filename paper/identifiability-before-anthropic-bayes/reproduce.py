#!/usr/bin/env python3
"""Reproduce the paper's finite examples using exact rational arithmetic only."""
from fractions import Fraction as F
from itertools import product
import hashlib, json
from pathlib import Path

def matmul_row(v, M):
    return tuple(sum((v[i]*M[i][j] for i in range(len(v))), F(0)) for j in range(len(M[0])))

def matmul(A,B):
    return tuple(tuple(sum((A[i][k]*B[k][j] for k in range(len(B))),F(0)) for j in range(len(B[0]))) for i in range(len(A)))

def transpose(A): return tuple(zip(*A))
def diag(v): return tuple(tuple(v[i] if i==j else F(0) for j in range(len(v))) for i in range(len(v)))
def fstr(x): return f"{x.numerator}/{x.denominator}"

def clone_example(r=20):
    return {"initial": fstr(F(1,2)), "clone_sim": fstr(F(r,r+1)), "clone_base": fstr(F(1,r+1)), "weighted": fstr(F(1,2))}

def persistent_example(T=100):
    a,b=F(3,4),F(1,4)
    persistent=a/b
    redraw=(a/b)**T
    return {"T":T,"persistent_bayes_factor":fstr(persistent),"redraw_bayes_factor":fstr(redraw)}

def gauge_example():
    K=((F(1),F(0)),(F(0),F(1)))
    pi=(F(1,2),F(1,2))
    A=((F(3,4),F(1,4)),(F(1,4),F(3,4)))
    # pi is fixed by this doubly-stochastic A, so pi'=pi and q is unchanged.
    Kp=matmul(A,K); pip=pi
    q=matmul_row(pi,K); qp=matmul_row(pip,Kp)
    assert q==qp and Kp!=K
    T=matmul(matmul(transpose(K),diag(pi)),K)
    Tp=matmul(matmul(transpose(Kp),diag(pip)),Kp)
    assert T!=Tp
    return {"one_view":list(map(fstr,q)),"transformed_one_view":list(map(fstr,qp)),"two_view_equal":T==Tp}

def permutation_audit():
    # Exhaust all 2x2 row-stochastic A on a denominator-4 grid for K=I, pi=(1/2,1/2).
    K=((F(1),F(0)),(F(0),F(1))); pi=(F(1,2),F(1,2)); T=diag(pi)
    preserving=[]
    for a,b in product(range(5),repeat=2):
        A=((F(a,4),F(4-a,4)),(F(b,4),F(4-b,4)))
        det=A[0][0]*A[1][1]-A[0][1]*A[1][0]
        if det==0: continue
        # inverse and transformed prior
        Ai=((A[1][1]/det,-A[0][1]/det),(-A[1][0]/det,A[0][0]/det))
        pip=matmul_row(pi,Ai)
        if any(x<=0 for x in pip): continue
        Kp=A
        Tp=matmul(matmul(transpose(Kp),diag(pip)),Kp)
        if Tp==T: preserving.append(A)
    assert preserving==[((F(0),F(1)),(F(1),F(0))),((F(1),F(0)),(F(0),F(1)))]
    return {"denominator":4,"preserving_count":len(preserving),"only_permutations":True}

def main():
    receipt={"clone":clone_example(),"persistent":persistent_example(),"gauge":gauge_example(),"two_view_grid_audit":permutation_audit()}
    canonical=json.dumps(receipt,sort_keys=True,separators=(",",":"))
    receipt["sha256_without_hash"]=hashlib.sha256(canonical.encode()).hexdigest()
    out=Path(__file__).with_name("receipt.json"); out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=="__main__": main()

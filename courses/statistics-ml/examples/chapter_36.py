import numpy as np
from scipy.optimize import linprog, linear_sum_assignment

def resource_allocation():
    objective=np.array([-3.,-2.])
    a=np.array([[1.,1.],[1.,0.],[0.,1.]])
    b=np.array([4.,2.,3.])
    result=linprog(objective,A_ub=a,b_ub=b,bounds=(0,None),method="highs")
    assert result.success and np.all(a@result.x<=b+1e-9)
    assert np.allclose(result.x,[2.,2.]) and np.isclose(-result.fun,10.)
    print("Allocation:",result.x,"profit:",-result.fun,"slack:",b-a@result.x)

def kkt_trace():
    x=2.;multiplier=2.
    stationarity=2*(x-3)+multiplier
    constraint=x-2
    assert stationarity==0 and constraint<=0 and multiplier>=0 and multiplier*constraint==0
    print("Constrained quadratic optimum, multiplier:",x,multiplier)

def assignment_and_queue():
    cost=np.array([[4.,1.],[2.,3.]])
    rows,cols=linear_sum_assignment(cost)
    assert cols.tolist()==[1,0] and cost[rows,cols].sum()==3.
    arrival,service=8.,10.
    waiting_system=1/(service-arrival);number_system=arrival*waiting_system
    assert waiting_system==.5 and number_system==4.
    print("Assignment cost:",cost[rows,cols].sum(),"M/M/1 time and count:",waiting_system,number_system)

def main():
    resource_allocation();kkt_trace();assignment_and_queue()

if __name__ == "__main__":
    main()

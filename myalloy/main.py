
import numpy as np
import sys 
from myalloy import calc_elastic_constant as cec




class alloy_class:
    def __init__(self, name, cn, brav_latt = 'fcc'):
        self.name = name
        self.cn = cn / cn.sum()
        self.brav_latt = brav_latt

        self.nelem = self.cn.shape[0]



    # print
    def print_alloy(self):
        print(self.name, self.cn)



    def dump(self):
        for attr in dir(self):
            if hasattr(self, attr):
                print('self.%s = %s' % (attr, getattr(self, attr)))



    # volume
    def calc_V0_from_a(self):
        if hasattr(self, 'V0'):
            sys.exit('ABORT: V0 exists. Double check!')
        else:
            if self.brav_latt is 'fcc':
                self.V0 = self.a **3/4 
            elif self.brav_latt is 'bcc':
                self.V0 = self.a **3/2 



    def calc_from_Velem(self):
        self.V0 = self.cn @ self.Velem
        self.dV = self.Velem - self.V0



    def calc_delta(self):
        if not hasattr(self, 'V0'):
            self.calc_V0_from_a()
        self.delta = np.sqrt( self.cn @ np.square(self.dV) ) /self.V0/3



    # elasticity
    def calc_Cijavg_from_Cij(self):      
        self.Cijavg = cec.calc_Cijavg_from_Cij(self.brav_latt, self.Cij)



    def calc_from_polyelem(self):
        
        Belem = np.array([]) 
        Eelem = np.array([])   

        for i in np.arange(self.nelem):
            Belem = np.append(Belem, \
                cec.calc_B_from_mu_nu(self.polyelem[i,0], self.polyelem[i,1]) )

            Eelem = np.append(Eelem, \
                cec.calc_E_from_mu_nu(self.polyelem[i,0], self.polyelem[i,1]) )

        mu = self.cn @ self.polyelem[:,0]

        # B  = self.cn @ Belem
        # nu = self.calc_nu_from_B_mu(B, mu)

        E  = self.cn @ Eelem
        nu = cec.calc_nu_from_E_mu(E, mu)

        self.poly = {'mu':mu, 'nu':nu}



    def calc_from_Cijelem(self):
        self.Cij = self.cn @ self.Cijelem
        









    # get EPI
    def get_EPI_from_file(self, filename='y_post_EPI.beta2_4.txt'):
        data = np.loadtxt(filename)
        self.EPI = EPI_reshape(self, data)
    
    
    # get SRO
    def get_SRO_from_file(self, filename='y_post_WC_SRO_shell_avg.txt'):
        data = np.loadtxt(filename)
        self.SRO = EPI_reshape(self, data)



    





    # solute strengthening theory
    def calc_yield_strength(self, param={}):
        from myalloy import solute_strengthening_theory as sst 
        sst.calc_yield_strength(self, param=param)







    # Stroh's formalism
    def calc_stroh(self, slip_system='basal_a_edge', param={}):
        from myalloy import stroh_dislocations as stroh 
        stroh.calc_stroh(self, \
            slip_system=slip_system, param=param)







def EPI_reshape(self, A):
    nelem = self.nelem 
    shellmax = len(A)/ (nelem*(nelem-1)/2) 
    temp = int(len(A)/shellmax)        
    A2 = A.reshape(shellmax, temp)

    A3 = np.zeros(shellmax, nelem, nelem)
    for i in np.arange(shellmax):
        m = -1
        for j in np.arange(nelem-1):
            for k in np.arange(j+1, nelem):
                m = m+1  
                A3[i, j, k] = A2[i, m]
    return A3 



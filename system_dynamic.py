# Libraries
import numpy as np
import matplotlib
# USEFULL FUNCTIONs

def dot3(a,B,c):
  # INPUTs: 
  #   a : row vector 1xN
  #   B : matrix NxN
  #   c : column vector Nx1

  return np.matmul(np.matmul(a,B),c) # Returns the matrix product a*B*c
#SYSTEM DYNAMICS DYNAMICS (Ball and Beam)

# SYSTEM DYNAMIC FUNCTION 

def BB_Dynamics(xx, uu, p_tens, params):
  # INPUTs:
  #   - xx  : system state at current time t 
  #   - uu  : input at current time t
  #   - p_tens: tensor product term
  #   - params: list of parameters

  # PARAMETERs EXTRACTION:
  dt = params['dt']; # Step size - Forward Euler method 
  gg = params['gg']; # gravitational acceleration [m/s^2]
  mm = params['mm']; # ball mass [kg]
  rr = params['rr']; # ball radius [m]
  ii = params['ii']; # ball inertia [kg*m^2]
  II = params['II']; # beam inertia [kg*m^2]
  LL = params['LL']; # beam lenght [m]
  
  # USEFUL VARIABLEs
  nx = 4; # nmumber of states 
  nu = 1; # number of inputs


  # SYSTEM DYNAMICS
  xx_next = np.zeros((nx,1)); # initialization
  
  xx_dot = np.array([[xx[1], 
                     ( mm*xx[0]*(xx[3]**2) - mm*gg*np.sin(xx[2]) )/( mm + II/(rr**2) ),
                     xx[3],
                     -( 2*mm*xx[0]*xx[1]*xx[3] + mm*xx[0]*np.cos(xx[2]) - uu )/d22  ]]);

  xx_next[0] = xx[0] + xx_dot[0]*dt;
  xx_next[1] = xx[1] + xx_dot[1]*dt;
  xx_next[2] = xx[2] + xx_dot[2]*dt;
  xx_next[3] = xx[3] + xx_dot[3]*dt;


  # GRADIENTs

  # useful notations
  d1  = ( mm + ii/(rr**2) )**(-1);
  d2  = ( II + mm*(xx[0]**2))**(-1);
  d22 = ( II + mm*(xx[0]**2));
  

  fx1_4_num = ( -( 2*mm*xx[1]*xx[3] + mm*gg*np.cos(xx[2]) )*d22 
                +( 2*mm*xx[0]*xx[1]*xx[3] + mm*gg*xx[0]*np.cos(xx[2]) - uu )*(2*mm*xx[0]) );
  fx1_4_den = d22**(2); 

  # partial derivative w.r.t. xx[1]:
  fx1 = np.array([[1, 
                  dt * ( mm*(xx[3]**2)*d1 ),
                  0,
                  dt * (fx1_4_num / fx1_4_den) ]]); 

  # partial derivative w.r.t. xx[2]:
  fx2 = np.array([[dt,
                  1,
                  0,
                  dt * ( -2*mm*xx[0]*xx[3]*d2 )]]);
      
  # partial derivative w.r.t. xx[3]:
  fx3 = np.array([[0,
                  dt * ( -mm*gg*np.cos(xx[2])*d1 ),
                  1,
                  dt * ( mm*gg*xx[0]*np.sin(xx[2])*d2 ) ]]);
  
  # partial derivative w.r.t. xx[4]:
  fx4 = np.array([[0,
                  dt * ( 2*xx[0]*xx[3]*d1 ),
                  dt,
                  1 - dt * ( 2*mm*xx[0]*xx[1]*d2 )]]);
  
  # Jacobian of the system dynamics:
  fx = np.concatenate((fx1.T,fx2.T,fx3.T,fx4.T), axis=1);

  # partial derivative w.r.t. the input:
  fu = np.array([[0,
                  0,
                  0,
                  dt*d2]]);


  # SECOND ORDER GRADIENTs
  pfxx = np.zeros((nx,nx));
  pfux = np.zeros((nu,nx));
  pfuu = np.zeros((nu,nu));
  
  # useful notations
  fx1x1_4_num   = (2*mm*( 2*mm*xx[0]*xx[1]*xx[3] + mm*gg*np.cos(xx[3]) - uu )*fx1_4_den)-(fx1_4_num *(4*d22*mm*xx[0]));
  fx1x1_4_den = d22**(4);
  

  # 1st row of the second derivative matrix nx*nx
  pfxx[0,0] = pp[3] * (( -2*mm*xx[3]*d22 + 4*xx[3]*(mm*xx[0])**2 ) / fx1_4_den) * dt;
  pfxx[0,1] = pp[3] * (( mm*gg*np.sin(xx[2])*d22 - 2*gg*np.sin(xx[2])*(mm*xx[0])**2)  / fx1_4_den) * dt;
  pfxx[0,2] = pp[3] * (( -2*mm*xx[1]*d22 + 4*xx[1]*(mm*xx[0])**2) / fx1_4_den) * dt;
  pfxx[0,3] = ( pp[1] * d1* (2*mm*xx[3]) * dt +
                pp[3] * (fx1x1_4_num  / fx1x1_4_den) * dt );
  
  # 2nd row of the second derivative matrix nx*nx
  pfxx[1,0] = pp[3] * (-2*mm*xx[3]*d2) * dt;
  pfxx[1,1] = 0;
  pfxx[1,2] = 0;
  pfxx[1,3] = pp[3] * (-2*mm*xx[0]*d2) * dt;

  # 3rd row of the second derivative matrix nx*nx
  pfxx[2,0] = pp[3] * (mm*gg*np.cos(xx[2])*d2) * dt;
  pfxx[2,1] = 0;
  pfxx[2,2] =( pp[1] * (mm*gg*np.sin(xx[2])*d1) * dt +
               pp[3] * (-mm*gg*xx[0]*np.sin(xx[2])*d2) * dt );
  pfxx[2,3] = 0;

  # 4th row of the second derivative matrix nx*nx
  pfxx[3,0] =( pp[1] * (2*mm*xx[3]*d1) * dt +
               pp[3] * (-2*mm*xx[1]*d2) * dt );
  pfxx[3,1] = pp[3] * (-2*mm*xx[0]*d2) * dt;
  pfxx[3,2] = 0;
  pfxx[3,3] = pp[1] * (2*mm*xx[0]*d1) * dt;

  # pfuu has all null elements

  # pfux has only one non-null element
  pfux[3,1] = pp[3] * (2*mm*x[0]*(d2**2)) * dt;


  # OUTPUTs: (the fucnction returns an output dictionary with the follows entries)
  #   - xx_next : system state at state (t+1)
  #   - fx     : gradient of the system dynamics w.r.t. the system state at time t
  #   - fu     : gradient of the system dynamics w.r.t. the input at time t
  #   - pfxx   : tensor product within the dynamics function seconnd order derivative w.r.t. the state, given vector pp
  #   - pfux   : tensor product within the dynamics function seconnd order derivative w.r.t. input and state, given vector pp 
  #   - pfuu   : tensor product within the dynamics function seconnd order derivative w.r.t. input, given vector pp 
  out = {
         'xx_next':xx_next,
         'fx':fx,
         'fu':fu,
         'pfxx':pfxx,
         'pfux':pfux,
         'pfuu':pfuu 
        };

  return out;
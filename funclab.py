from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

import numpy as np
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt

import sympy as sym
from sympy import *
init_printing()

#!!!!!!!!!!!!!!!!IMPORT DATA !!!!!!!!!!!!!!!!!!1
def importData(fileName, sheetName, numCol, delHead = False):
  if 'gc' in globals():
    ss = gc.open(fileName)
    ws = ss.worksheet(sheetName)
    if isinstance(numCol,list):
        dataCol=[]
        for nc in numCol:
          dataCol.append(ws.col_values(nc))
          if delHead:
            dataCol[numCol.index(nc)].remove(dataCol[numCol.index(nc)][0])
    
        dataColMod= []
    
        for i in dataCol:
            dataColMod.append([])
            for d in i:
              dataColMod[dataCol.index(i)].append(eval(d.replace(',','.')))
        return dataColMod
    
    else:
        dataCol= ws.col_values(numCol)
        if delHead:
          dataCol.remove(dataCol[0])
        dataColMod= []
        for d in dataCol:
          dataColMod.append(eval(d.replace(',','.')))
        return dataColMod
  else:
    a= """
    ¡¡¡ Before using this function please run this code !!!

    from google.colab import auth
    auth.authenticate_user()

    import gspread
    from google.auth import default
    creds, _ = default()

    gc = gspread.authorize(creds)
    """
    print(a)


#!!!!!!!!!!!!!!! CURVE FIT !!!!!!!!!!!!!!!!!!!
def curveFit(func, x, y, graf=False):

  if isinstance(x, list): 
    X = np.array(x)
  else:
    X = x
  if isinstance(y, list): 
    Y = np.array(y)
  else :
    Y = y

  popt, pcov = curve_fit(func, X, Y)

  perr = np.sqrt(np.diag(pcov))# Incertesa standard dels parametres

  residuals = Y- func(X, *popt)
  ss_res = np.sum(residuals**2)
  ss_tot = np.sum((Y-np.mean(Y))**2)
  r_squared = 1 - (ss_res / ss_tot) #R^2

  if graf:
    results = [popt, perr, r_squared]
    return results
  else:
    for i in range(len(popt)):
      print(f'a_{i} = {popt[i]} \pm {perr[i]}')

    print(f'R^2 = {r_squared}')
    
#!!!!!!!!!!!!!!!!! REGRESSIO LINIAL !!!!!!!!!!!!!!!!!!!!!
def regressio(x,y, graf=False, table = False):

  def func(x, A, B):
    return A*x +B
  
  curve = curveFit(func, x, y, graf= True)
  A = Variable('A', curve[0][0], curve[1][0])
  B = Variable('B', curve[0][1], curve[1][1])
  R2 = curve[2]

  if graf:
    return A, B, R2
  elif table:
    print('\\begin{tabular}{ccc}')
    print('$A$  & $B$ & $r^2$ \\ \\ \hline')
    print(f'${A.val} \pm {A.inc}$ & ${B.val} \pm {B.inc}$ & {R2}\\ \\ \hline')
    print('\end{tabular}')
  else:
    print(f'A = {A.val} \pm {A.inc}')
    print(f'B = {B.val} \pm {B.inc}')
    print(f'$R^2$ = {R2}')

    
  

  #!!!!!!!!!!!!! PROPAGACIÓ D'INCERTESES !!!!!!!!!!!!!!!!!!!!!!!
class Variable:
  def __init__(self, simbol, valor, incertesa):
     self.sim = sym.Symbol(simbol)
     self.val = valor
     self.inc = incertesa
        
def propIncertesa(fun, variables, val=True):

  incerteses = []
  valors = []
  errfun = 0

  # calcul simbolic de la incertesa
  for s in range(len(variables)):

    sigma_s = sym.Symbol('sigma_' + variables[s].sim.name)
    errfun += (sym.diff(fun, variables[s].sim)*sigma_s)**2

  errfun = errfun**sym.Rational(1/2)
  errfunev = errfun

  valor = fun
  
  # variables i/o incerteses amb un sol valor
  for s in range(len(variables)):

    # si la variable es un sol valor es substitueix el simbol pel valor
    if isinstance(variables[s].val, (float, int, sym.core.numbers.Float)): 
        errfunev = errfunev.subs(variables[s].sim, variables[s].val)
        valor = valor.subs(variables[s].sim, variables[s].val)

    # si la incertesa es un sol valor es substitueix el simbol pel valor
    if isinstance(variables[s].inc, (float, int, sym.core.numbers.Float)):
        errfunev = errfunev.subs(sym.Symbol('sigma_' + variables[s].sim.name), variables[s].inc)

  # llistes de variables i/o incerteses
  for s in range(len(variables)):

    # si el valor de la Variable és una llista...
    if isinstance(variables[s].val, (list, np.ndarray)):
        
        # si es la primera variable que es una llista
        if len(incerteses) == 0:
            
            # per cada valor de la llista
            for i in variables[s].val:
                
                xmod = errfunev
                xomd1 = valor
                # afegim a la llista tot el lexpressio de la incertesa intercambiant la variable pel seu valor
                incerteses.append(xmod.subs(variables[s].sim, i))
                valors.append(valor.subs(variables[s].sim, i))

        # si no es la primera variable que es una llista i.e. ja hi ha expresio de la incertesa per cada valor
        elif len(incerteses) !=0:
            
            for i in range(len(incerteses)):
                
                incerteses[i] = incerteses[i].subs(variables[s].sim, variables[s].val[i])
                valors[i] = valors[i].subs(variables[s].sim, variables[s].val[i])


    #Si la incertesa de la Variable és una llista...
    if isinstance(variables[s].inc, (list, np.ndarray)):
        
        if len(incerteses) == 0:
            
            for i in variables[s].inc:
                
                incerteses.append(errfunev.subs(sym.Symbol('sigma_'+variables[s].sim.name), i))

        elif len(incerteses) !=0:
            
            for i in range(len(incerteses)):
                
                incerteses[i] = incerteses[i].subs(sym.Symbol('sigma_'+variables[s].sim.name),variables[s].inc[i])

  if len(incerteses) == 0:
    errfunev = errfunev.evalf()
    if val == True:
      return valor, errfunev
    else:
      return errfun, errfunev
  elif len(incerteses) != 0:
    for i in incerteses:
      i = i.evalf()
    if val == True:
      return valors, incerteses
    else:
      return errfun, incerteses
  

#!!!!!!!!!!!!! GRAFICAR DADES !!!!!!!!!!!!!!!!!

def plotDades(ax, x, y, label = False, color = 'b', marker = 'o', markersize = 3):

  ax.tick_params(direction = 'in', right = True, top = True)
  ax.grid(color = '#eeeeee', linestyle = '--')
  
  if label:
    ax.errorbar(x.val, 
                y.val, 
                xerr = x.inc,
                yerr = y.inc,
                capsize = 0,
                elinewidth = 0.5,
                linewidth = 0,
                marker = marker,
                markersize = markersize,
                markerfacecolor = color,
                markeredgecolor = color,
                ecolor = color,
                label = label
                )
  else:
    ax.errorbar(x.val, 
                y.val, 
                xerr = x.inc,
                yerr = y.inc,
                capsize = 0,
                elinewidth = 0.5,
                linewidth = 0,
                marker = marker,
                markersize = markersize,
                markerfacecolor = color,
                markeredgecolor = color,
                ecolor = color
                )

  
    
  
    

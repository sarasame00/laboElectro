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
  popt, pcov = curve_fit(func, x, y)

  perr = np.sqrt(np.diag(pcov))# Incertesa standard dels parametres

  residuals = y- func(x, *popt)
  ss_res = np.sum(residuals**2)
  ss_tot = np.sum((y-np.mean(y))**2)
  r_squared = 1 - (ss_res / ss_tot) #R^2

  if graf:
    results = [popt, perr, r_squared]
    return results
  else:
    for i in range(len(popt)):
      print(f'a_{i} = {popt[i]} \pm {perr[i]}')

    print(f'R^2 = {r_squared}')
    
# !!!!!!!!!!!!! GRAFICA !!!!!!!!!!!!!!!
def grafica(x,y,errx,erry,xlabel,ylabel, titol='títol', xlimits=False, ylimits=False, func=False, rang=False, label=['curve fit'], 
            plot=False, plot1=False, plot2=False, plot3=False, plot4=False, 
            plot5=False, plot6=False, posLegend='upper right'):
  fig = plt.figure()
  ax1= fig.add_subplot()
  plt.title(titol)
  colors= ['c','m','y','b','r','g','k']
  if isinstance(y[0], list):
      for li in y:
          ax1.errorbar(x,
                       li,
                       xerr= errx,
                       yerr=erry[y.index(li)],
                       capsize=3,
                       elinewidth=0.5,
                       linewidth=0,
                       marker='o',
                       markersize=3,
                       markerfacecolor='0.5',
                       markeredgecolor=colors[y.index(li)],
                       ecolor=colors[y.index(li)],
                       label=ylabel[y.index(li)+1])
          ax1.set_ylabel(ylabel[0])
          ax1.legend(loc='upper right')
  else:
    ax1.errorbar(x,
                 y,
                 xerr= errx,
                 yerr=erry,
                 capsize=3,
                 elinewidth=0.5,
                 linewidth=0,
                 marker='o',
                 markersize=3,
                 markerfacecolor='0.5',
                 markeredgecolor='k',
                 ecolor='k',
                 label='mesures')
    if xlimits !=False:
      ax1.set_xlim(xlimits[0],xlimits[1])
    if ylimits !=False:
      ax1.set_ylim(ylimits[0],ylimits[1])
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)  
  if plot !=False:
      ax1.plot(plot[0],plot[1],label=plot[2], color=colors[0])
  if plot1 !=False:
      ax1.plot(plot1[0],plot1[1],label=plot1[2], color=colors[0])
  if plot2 !=False:
      ax1.plot(plot2[0],plot2[1],label=plot2[2], color=colors[1])
  if plot3 !=False:
      ax1.plot(plot3[0],plot3[1],label=plot3[2], color=colors[1])
  if plot4 !=False:
      ax1.plot(plot4[0],plot4[1],label=plot4[2],color=colors[2])
  if plot5 !=False:
      ax1.plot(plot5[0],plot5[1],label=plot5[2],color=colors[2])
  if plot6 !=False:
       ax1.plot(plot6[0],plot6[1],label=plot6[2],color=colors[6])
  if func!=False:
      if rang!=False:
          u= np.arange(rang[0],rang[1],0.001)
      else:
        u= np.arange(min(x)-2,max(x)+2,0.001)
      plt.plot(u, func(u),label=label)
      
  ax1.legend(loc=posLegend)

  #posem nom als eixos
  ax1.set_xlabel(xlabel)

  
  #!!!!!!!!!!!!! PROPAGACIÓ D'INCERTESES !!!!!!!!!!!!!!!!!!!!!!!
class Variable:
  def __init__(self,simbol, valor, incertesa):
     self.sim = sym.Symbol(simbol)
     self.val = valor
     self.inc = incertesa
        
def propIncertesa(fun, variables, val=False):
  tot=[]
  errfun=0
  
  #Càlcul simbòlic de la incertesa
  for s in range(len(variables)):
    sigma_s=sym.Symbol('sigma_'+variables[s].sim.name)
    errfun += (sym.diff(fun,variables[s].sim)*sigma_s)**2

  errfun=errfun**sym.Rational(1/2)
  errfunev = errfun
  
  #Variables i/o incerteses amb un sol valor
  for s in range(len(variables)):
    if isinstance(variables[s].val, (float,int,sym.core.numbers.Float)): 
        errfunev = errfunev.subs(variables[s].sim,variables[s].val)
    if isinstance(variables[s].inc, (float,int,sym.core.numbers.Float)):
        errfunev = errfunev.subs(sym.Symbol('sigma_'+variables[s].sim.name),variables[s].inc)

  #Llistes de variables i/o incerteses
  for s in range(len(variables)):
    #Si el valor de la Variable és una llista...
    if isinstance(variables[s].val, list):
        if len(tot) ==0:
            for i in variables[s].val:
                xmod = errfunev
                tot.append(xmod.subs(variables[s].sim,i))
        elif len(tot) !=0:
            for i in range(len(tot)):
                tot[i] = tot[i].subs(variables[s].sim,variables[s].val[i])
    #Si la incertesa de la Variable és una llista...
    if isinstance(variables[s].inc, list):
        if len(tot) ==0:
            for i in variables[s].inc:
                tot.append(errfunev.subs(sym.Symbol('sigma_'+variables[s].sim.name),i))
        elif len(tot) !=0:
            for i in range(len(tot)):
                tot[i] = tot[i].subs(sym.Symbol('sigma_'+variables[s].sim.name),variables[s].inc[i])

  if len(tot) ==0:
    errfunev=errfunev.evalf()
    if val==True:
      return errfunev
    else:
      return errfun,errfunev
  elif len(tot) !=0:
    for i in tot:
      i = i.evalf()
    if val==True:
      return tot
    else:
      return errfun,tot
  
#!!!!!!!!!!!!! INCERTESA MITJANA !!!!!!!!!!!!!!!!!
    
  
    
  
    

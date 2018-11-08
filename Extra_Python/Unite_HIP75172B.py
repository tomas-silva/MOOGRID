

import numpy as np
import matplotlib.pyplot as plt

ficheiros=("HIP75172B_wlen1.asc","HIP75172B_wlen2.asc",
"HIP75172B_wlen3.asc","HIP75172B_wlen4.asc","HIP75172B_wlen5.asc",
"HIP75172B_wlen6.asc", "HIP75172B_wlen7.asc","HIP75172B_wlen8.asc")


def list_asc(files):
    lista=[None]*(len(ficheiros))
    tamanhos=[None]*(len(ficheiros))

    for i in range(len(files)):
        ascii_grid = np.loadtxt(files[i], skiprows=0)
        lista[i]=(ascii_grid[:,0],ascii_grid[:,1])
        tamanhos[i]=len(ascii_grid[:,0])
    return lista,tamanhos

todos=list_asc(ficheiros)[0]
tamanhos_iniciais=list_asc(ficheiros)[1]
#print(tamanhos_iniciais)

def ordenar_listas(lista):
    less = []
    equal = []
    greater = []

    if len(lista) > 1:
        pivot = lista[0][0][0]
        for x in lista:
            if x[0][0] < pivot:
                less.append(x)
            if x[0][0] == pivot:
                equal.append(x)
            if x[0][0] > pivot:
                greater.append(x)
        # Don't forget to return something!
        return ordenar_listas(less)+equal+ordenar_listas(greater)  # Just use the + operator to join lists
    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return lista

todos_ordenados=ordenar_listas(todos)
#print(todos_ordenados)

def conc(lista):
    Wavelenght=[]
    Flux=[]
    for i in lista:
        Wavelenght.append(i[0])
        Flux.append(i[1])
    return np.concatenate(Wavelenght),np.concatenate(Flux)

espectro_unico=conc(todos_ordenados)

f = open("HIP75172B_total.dat","w")
for i in range(len(espectro_unico[0])):
    #print(espectro_unico[0][i], espectro_unico[1][i])
    f.write("%f\t%f\n" % (espectro_unico[0][i], espectro_unico[1][i]))
f.close()

#print(espectro_unico)
def plot_espectro_total(lista,save='no',estilo='original'):
    cores=['black','red','orange','yellow','green','aquamarine','blue','purple']
    fig, ax = plt.subplots()

    if estilo=='original':
        ax.plot(lista[0], lista[1])
    if estilo=='red_dots':
        ax.plot(lista[0], lista[1],'ro',markersize=2,marker='.')
    if estilo=='thin':
        for i in range(len(tamanhos_iniciais)):
            print(i)
            ax.plot(lista[0][i*1020:((i+1)*1020)], lista[1][i*1020:((i+1)*1020)],color=cores[i],linewidth=0.5)
            #ax.plot(lista[0], lista[1],'ro',markersize=2,marker='.')


    plt.title(str('Total - HIP75172B'))
    plt.ylabel('Flux')
    plt.xlabel('Wavelenght')
    if save=='yes':
        plt.savefig(str('Spectrum of ')+str('Total')+str(' - ')+str(estilo)+str('.pdf'), bbox_inches='tight')
    plt.show()

#print(espectro_unico)
plot_espectro_total(espectro_unico,save='yes',estilo='thin')

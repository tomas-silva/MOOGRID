import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
from scipy.stats import chisquare
import sys
from time import sleep

# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write("\r"),
    sys.stdout.write('%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def plot_dados(file, save='no', estilo='original'):
    """Função inicial faz plot de dados de um determinado ficheiro, podemos escolher
    guardar e se queremos estilo normal ou em bolinhas vermelhas"""

    dados = np.loadtxt(file, skiprows=2)

    fig, ax = plt.subplots()

    if estilo == 'original':
        ax.plot(dados[:, 0], dados[:, 1])
    if estilo == 'red_dots':
        ax.plot(dados[:, 0], dados[:, 1], 'ro', markersize=2, marker='.')

    plt.title(str(file[0:-4]))
    plt.ylabel('Flux')
    plt.xlabel('Wavelenght')
    if save == 'yes':
        plt.savefig(str('Spectrum of ') + str(file[0:-4]) + str(' - ') + str(estilo) + str('.pdf'), bbox_inches='tight')
    plt.show()


# plot_dados("plansm.outtest",'no')


def plot_dados_comparar(files, save='no', modo='original', top=8, ficheiro_a_comparar=None):
    """Função avançada, faz plot dados de um ou vários ficheiros, tal como podemos comparar um set de ficheiros
    com um especifico, pode ser feito um ajuste de chi quadrado para ver qual dos ficheiros melhor se ajusta
     ao ficheiro a comparar, podendo escolher os ficheiros que melhor fazem o fit"""

    cores = ['red', 'orange', 'yellow', 'yellowgreen', 'green', 'aquamarine', 'blue', 'purple']
    numeros = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    fig, ax = plt.subplots()
    a = 0
    if modo == 'original':
        for file in files:
            dados = np.loadtxt(file, skiprows=2)
            if file[15] not in numeros:
                ax.plot(dados[:, 0], dados[:, 1], color='black',
                        label=str('Dados ficheiro .atm ' + str(file[15:])))
            else:
                ax.plot(dados[:, 0], dados[:, 1], color=cores[a % (len(cores))],
                        label=str('[') + str(file[15:19]) + str(',') + str(file[20:24]) + str(',')
                              + str(file[25:29]) + str(',') + str(file[30:34]) + str(']'))
            a = a + 1

        legend = ax.legend()  # mostra legenda

        plt.title('Comparações - Temperatura, logg, [Fe/H], microturbulencia')
        plt.ylabel('Flux')
        plt.xlabel('Wavelenght')
        if save == 'yes':
            plt.savefig(str('Spectrum of ') + str('many') + str(' - ') + str(estilo) + str('.pdf'), bbox_inches='tight')
        plt.show()

    if modo == 'chi_quadrado':
        """ Verificar sempre len(), step, range, ... de ficheiros synth vs ficheiro a comparar. """
        #print(' ')
        #print('Verificar sempre len(), step, range, ... de ficheiros synth vs ficheiro a comparar. ')
        #print(' ')

        dados = np.loadtxt(ficheiro_a_comparar, skiprows=2)

        ax.plot(dados[:, 0], dados[:, 1], color='black',
                label=str('Dados ficheiro .atm ' + str(ficheiro_a_comparar[15:])))

        # Criar listas que irão ser as ordenadas no final, tem top+1 pois têm um index a mais que é residuo da função
        # criada para organizar
        lista_top_fluxos = [1000] * (top + 1)
        lista_top_ficheiros = [1000] * (top + 1)

        count_progress = 0
        l = len(files)-1 #menos o que está a comparar
        print(' ')
        print('Calculation of best fits:')

        for file_comp in files:
            if file_comp != ficheiro_a_comparar:
                dados_comp = np.loadtxt(file_comp, skiprows=2)
                chi_square = chisquare(dados_comp[:, 1], f_exp=dados[:, 1])
                chi_square_value = chi_square[0]
                (index_top, valor_topo) = lugar_no_top(lista_top_fluxos[:-1], chi_square_value)
                #print(lista_top_fluxos)

                print_progress(count_progress, l, prefix='Progress:', suffix='Complete', decimals=1, bar_length=100)
                count_progress += 1

                for i in range(index_top,top):
                    lista_top_fluxos[i+1] = lista_top_fluxos[i]
                    lista_top_ficheiros[i+1] = lista_top_ficheiros[i]
                lista_top_fluxos[index_top] = chi_square_value
                lista_top_ficheiros[index_top] = file_comp

        # -1 porque ultimo elemento das listas é tipo lixo residual da funçao de fazer listas de topo
        for file_finais in lista_top_ficheiros[:-1]:
            dados_finais = np.loadtxt(file_finais, skiprows=2)
            extra_met=0
            extra_micro=0
            if file_finais[25] == '-':
                extra_met=1
            if file_finais[30+extra_met] == '-':
                extra_micro = 1
            ax.plot(dados_finais[:, 0], dados_finais[:, 1], color=cores[a % (len(cores))],
                    label=str('[') + str(file_finais[15:19]) + str(',') + str(file_finais[20:24]) + str(',')
                          + str(file_finais[25:29+extra_met]) + str(',') + str(file_finais[30+extra_met:34+extra_met+extra_micro]) + str(']'))
            a = a + 1

        ### Extra - também quero comparar com dados do MOOG para parametros do Sol

        ficheiro_Sun = 'plansm.outtest_5777_4.44_0.00_1.00'
        dados_Sun_MOOG = np.loadtxt(ficheiro_Sun, skiprows=2)
        ax.plot(dados_Sun_MOOG[:, 0], dados_Sun_MOOG[:, 1], 'ko', markersize=1,
                label=str('[') + str(ficheiro_Sun[15:19]) + str(',') + str(ficheiro_Sun[20:24]) + str(',')
                      + str(ficheiro_Sun[25:29]) + str(',') + str(ficheiro_Sun[30:34]) + str(']'))

        ### Extra

        legend = ax.legend()  # mostra legenda

        plt.title('Melhores aproximações - Método chi_quadrado')
        plt.ylabel('Flux')
        plt.xlabel('Wavelenght')
        if save == 'yes':
            plt.savefig(str('Spectrum of ') + str('many') + str(' - ') + str(estilo) + str('.pdf'),
                        bbox_inches='tight')
        plt.show()


def plansm_filtro(todos_ficheiros):
    """ Função para filtrar ficheiros por nome, assim só obtemos os 'plansm', o que queremos, retirando por exemplo
    ficheiros Python"""
    lista = []
    for ficheiro in todos_ficheiros:
        if ficheiro[:6] == 'plansm':  # ler primeiras seis letras
            lista.append(ficheiro)
    return lista


def construct_list_filenames(set_temp, set_logg, set_metal, set_micro, extra):
    """ Dados os sets de parametros esta função cria os nomes dos ficheiros que é suposto encontrarmos no
    nosso diretorio"""
    lista = []
    f = open("Files_dont_exist.txt", "w")
    count_ficheiros_nao_existentes = 0
    count_ficheiros_brancos = 0
    for temp in set_temp:
        for logg in set_logg:
            for metal in set_metal:
                for micro in set_micro:
                    file_name = 'plansm.outtest_' + str(temp) + '_' + str("{0:.2f}".format(logg)) \
                         + '_' + str("{0:.2f}".format(metal)) + '_' + str("{0:.2f}".format(micro))

                    # Verificar se ficheiro existe
                    if os.path.isfile(file_name) is True:
                        g = open(file_name, "r")
                        linha = g.readline()
                        g.close()
                        if linha == '':
                            count_ficheiros_brancos += 1
                        else:
                            lista.append(file_name)
                    else:
                        count_ficheiros_nao_existentes += 1
                        # Escreve no ficheiro criado todos os plansm que não existem e não podem ser plottados
                        f.write(file_name + '\n')
    f.close()
    print('*')
    print(str(count_ficheiros_nao_existentes) + str(' combinações sem criação de ficheiros'))
    print(str(count_ficheiros_brancos) + str(' ficheiros criados em branco'))
    print(str(len(set_temp)*len(set_logg)*len(set_metal)*len(set_micro)) + str(' ficheiros possiveis'))
    print('*')
    # if extra != None:
    if extra is not None:
        lista.append('plansm.outtest_' + str(extra))

    return lista


def lugar_no_top(lista_top, candidato): # função recursiva
    """Função responsavel por dada uma certa lista e um candidato 'returnar' a posição de o candidato na lista
    Atenção: No topo é sempre o menor"""
    if candidato < lista_top[-1]:
        if len(lista_top) == 1:
            return (0, candidato)
        return lugar_no_top(lista_top[:-1], candidato)
    return (len(lista_top), candidato)


# Valores possiveis
#set_comparar_temp = [5600, 5650, 5700, 5750, 5777, 5800, 5850, 5900, 5950, 6000]
#set_comparar_logg = [4.3, 4.4, 4.44, 4.5, 4.6]
#set_comparar_metal = [-0.4, -0.2, -0.1, 0, 0.1, 0.2, 0.4]
#set_comparar_micro = [0.6, 0.8, -1.1, 1, 1.1, 1.2, 1.4]


# Chamar ficheiros da minha pasta, criados por MOOG
all_files = os.listdir("/home/tomas/Masters/Sun_MOOG/Files_plansm.outtest")

# Só temos agora os ficheiros a começar por 'plansm'
plansm_files = plansm_filtro(all_files)


set_comparar_temp = [5600, 5650, 5700, 5750, 5777, 5800, 5850, 5900, 5950, 6000]
set_comparar_logg = [4.3, 4.4, 4.44, 4.5, 4.6]
set_comparar_metal = [-0.4, -0.2, -0.1, 0, 0.1, 0.2, 0.4]
set_comparar_micro = [0.6, 0.8, -1.1, 1, 1.1, 1.2, 1.4]

# files_compare = (construct_list_filenames(set_comparar_temp, set_comparar_logg, set_comparar_metal, set_comparar_micro, 'Sergio'))

Total_set = (construct_list_filenames(set_comparar_temp, set_comparar_logg,
                                      set_comparar_metal, set_comparar_micro, None))

#plot_dados_comparar(files_compare, 'no_save','chi_quadrado',8,'plansm.outtest_Nuno')
plot_dados_comparar(Total_set, 'no_save','chi_quadrado',8,'plansm.outtest_Sergio')

##ARRANJAR CENA DE TER QUE ESCREVER NOME DUAS VEZES NO files_compare e no input do plot_dados_comparar


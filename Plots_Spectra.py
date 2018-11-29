import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
from scipy.stats import chisquare
import sys
from time import sleep
from scipy.interpolate import interp1d


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

def construct_list_filenames(set_temp, set_logg, set_metal, set_micro, extra_txt, extra_files=None):
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
                         + '_' + str("{0:.2f}".format(metal)) + '_' + str("{0:.2f}".format(micro)) + extra_txt
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
    if type(extra_files) == list:
        for extra in extra_files:
            lista.append(str(extra))
    if type(extra_files) == str:
        lista.append(str(extra_files))
    return lista


def plot_dados_lindgren(files, valores_medios, save='no', estilo='original', coluna_wv=0, coluna_flux=1, min_wv=0,
                        max_wv=0, min_fl=0.8, max_fl=1.05):
    """Função inicial faz plot de dados de um determinado ficheiro, podemos escolher
    guardar e se queremos estilo normal ou em bolinhas vermelhas"""

    reds = ['darkorange', 'red', 'maroon']
    blues = ['royalblue', 'blue', 'navy']
    yellows = ['orange', 'goldenrod', 'yellow']
    pinks = ['magenta', 'deeppink', 'mediumvioletered']
    greens = ['lawngreen', 'green', 'forestgreen']

    temp_med = str('{:04}'.format(valores_medios[0]))
    logg_med = str("{0:.2f}".format(valores_medios[1]))
    met_med = str("{0:.2f}".format(valores_medios[2]))
    micro_med = str("{0:.2f}".format(valores_medios[3]))

    reds_counts = 0
    blues_counts = 0
    yellows_counts = 0
    greens_counts = 0
    pinks_counts = 0

    fig, ax = plt.subplots()

    if type(valores_medios) == list:  # Quero fazer comparaçoes de plots
        count_progress = 0  # Para barra de progresso
        print('')
        for file in files:
            print_progress(count_progress, len(files), prefix='Progress:', suffix='Complete',
                           decimals=1, bar_length=100)
            dados = np.loadtxt(file, skiprows=2)
            if file == 'HIP57172B_total.dat':
                dados = np.loadtxt(file, skiprows=0)
                if estilo == 'original':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], markersize=0.5, color='black', label='Observ.')
                if estilo == 'red_dots':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], 'ro', markersize=2, marker='.')
                if estilo == 'black_squares':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], 'ro', markersize=2, marker='s', color='black')

            if file[15:19] == temp_med and file[20:24] == logg_med and file[25:29] == met_med \
                    and file[30:34] == micro_med:
                ax.plot(dados[:, 0], dados[:, 1], color=greens[1], label='All')

            if file[20:24] == logg_med and file[25:29] == met_med and file[30:34] == micro_med and \
                    file[15:19] != temp_med:
                label_form = 'Temp ' + file[15:19]
                ax.plot(dados[:, 0], dados[:, 1], color=reds[reds_counts], label=label_form)
                reds_counts += 1

            if file[15:19] == temp_med and file[25:29] == met_med and file[30:34] == micro_med and \
                    file[20:24] != logg_med:
                label_form = 'Logg ' + file[20:24]
                ax.plot(dados[:, 0], dados[:, 1], color=blues[blues_counts], label=label_form)
                blues_counts += 1

            if file[15:19] == temp_med and file[20:24] == logg_med and file[30:34] == micro_med and \
                    file[25:29] != met_med:
                label_form = 'Met ' + file[25:29]
                ax.plot(dados[:, 0], dados[:, 1], color=yellows[yellows_counts], label=label_form)
                yellows_counts += 1

            if file[15:19] == temp_med and file[20:24] == logg_med and file[25:29] == met_med and \
                    file[30:34] != micro_med:
                label_form = 'Micro ' + file[30:34]
                ax.plot(dados[:, 0], dados[:, 1], color=pinks[pinks_counts], label=label_form)
                pinks_counts += 1

            count_progress += 1
        # Ultimo step do progesso

        print_progress(count_progress, len(files), prefix='Progress:', suffix='Complete',
                       decimals=1, bar_length=100)

    else:
        for file in files:
            print(file)
            dados = np.loadtxt(file, skiprows=2)
            if file == 'HIP57172B_total.dat':
                dados = np.loadtxt(file, skiprows=0)
                if estilo == 'original':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], markersize=0.5, color='black', label='Observ.')
                if estilo == 'red_dots':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], 'ro', markersize=2, marker='.')
                if estilo == 'black_squares':
                    ax.plot(dados[:, coluna_wv], dados[:, coluna_flux], 'ro', markersize=2, marker='s', color='black')

            ax.plot(dados[:, 0], dados[:, 1], color=reds[0], label=file[15:34])

    if min_wv != 0 and max_wv != 0:
        ax.set_xlim(min_wv, max_wv)
    if min_fl != 0 and max_fl != 0:
        ax.set_ylim(min_fl, max_fl)
    ax.legend()
    handles, labels = plt.gca().get_legend_handles_labels()
    order = [3, 0, 6, 1, 5, 2, 4, 7] #Ordem das legendas
    plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
    plt.title('Synth_Lindgren')
    plt.ylabel('Flux')
    plt.xlabel('Wavelenght')
    if save == 'yes':
        plt.savefig(str('Spectrum of Lindgren') + str('.pdf'), bbox_inches='tight')
    plt.show()


ficheiros_teste = ["HIP57172B_total.dat",
                   "plansm.outtest_3900_4.46_0.16_1.00_r_0,011_1,000_1,000_3,500_0,000"]

valores_medios_HIP57172B = [3900, 4.46, 0.16, 1]

set_comparar_temp = [3700, 3900, 4100]
set_comparar_logg = [4.37, 4.46, 4.55]
set_comparar_metal = [0.08, 0.16, 0.24]
set_comparar_micro = [1]

ficheiros = construct_list_filenames(set_comparar_temp, set_comparar_logg, set_comparar_metal, set_comparar_micro,
                                     '_r_0,011_1,000_1,000_0,390_0,000', extra_files="HIP57172B_total.dat")

plot_dados_lindgren(ficheiros, valores_medios_HIP57172B, save='no', estilo='original', coluna_wv=0, coluna_flux=1,
                    min_wv=11945, max_wv=11995, min_fl=0.8, max_fl=1.02)

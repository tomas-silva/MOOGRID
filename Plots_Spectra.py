import numpy as np
import matplotlib.pyplot as plt
import os
import os.path
from scipy.stats import chisquare
import sys
from time import sleep
from scipy.interpolate import interp1d
import pickle
import time


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
    print(str(len(set_temp)*len(set_logg)*len(set_metal)*len(set_micro)-count_ficheiros_nao_existentes-count_ficheiros_brancos) + str('/') + str(len(set_temp)*len(set_logg)*len(set_metal)*len(set_micro)) + str(' ficheiros corretamente criados'))
    print('*')
    # if extra != None:
    if type(extra_files) == list:
        for extra in extra_files:
            lista.append(str(extra))
    if type(extra_files) == str:
        lista.append(str(extra_files))
    return lista


def ajustar_lens(dados_1, inicio, fim, tamanho, plot='no'):

    f = interp1d(dados_1[:,0], dados_1[:,1])

    xnew = np.linspace(inicio, fim, num=tamanho, endpoint=True)

    if plot == 'yes':
        plt.plot(dados_1[:,0], dados_1[:,1], 'b-')
        plt.plot(xnew, f(xnew), 'ro', markersize=5, marker='.')
        plt.show()
    return [xnew, f(xnew)]


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    # print(array[idx])
    return idx


def index_dos_intervalos(intervalos, dados_totais):
    dados = dados_totais[:, 0]
    lista_final = []
    indexes=[]
    for mask in intervalos:
        indexes_intv=([find_nearest(dados,mask[0]),find_nearest(dados,mask[1])])
        lista_final.append(dados_totais[indexes_intv[0]:indexes_intv[1]+1]) # mais um para incluir ultimo
        indexes.append(indexes_intv)

    return np.concatenate(lista_final)


def plot_dados_lindgren(files, tipo, valores_medios, intervalos_mask, ficheiro_obs=None, save='no', estilo='original', coluna_wv=0, coluna_flux=1, min_wv=0,
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

    if tipo == 'comparar':
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

    if tipo == 'chi_quadrado':

        start_time = time.time()

        count_progress = 0

        lista_file_chi_square = []

        # Dados observados nos limites da mask:

        dados_observ = np.loadtxt(ficheiro_obs, skiprows=2)
        dados_sim_exmpl = np.loadtxt(files[0], skiprows=2)

        lim_inf_wv = max(dados_observ[0, 0], dados_sim_exmpl[0, 0])
        lim_sup_wv = min(dados_observ[-1, 0], dados_sim_exmpl[-1, 0])
        len_wv = min(len(dados_observ[:, 0]), len(dados_sim_exmpl[:, 0]))

        dados_mid_format = ajustar_lens(dados_observ, lim_inf_wv, lim_sup_wv, len_wv)
        dados_observ_ajust = np.zeros((len(dados_mid_format[0]), 2))
        dados_observ_ajust[:, 0] = dados_mid_format[0]
        dados_observ_ajust[:, 1] = dados_mid_format[1]

        if intervalos_mask != None:
            lista_mask_obs=index_dos_intervalos(intervalos_mask, dados_observ_ajust)
        ax.plot(lista_mask_obs[:, 0], lista_mask_obs[:, 1], 'ro', markersize=10, marker='.')

        print('')
        print('Calculo de chi-quadrado para todos os ficheiros:')

        for file in files:
            print_progress(count_progress, len(files), prefix='Progress:', suffix='Complete',
                           decimals=1, bar_length=100)

            dados_file = np.loadtxt(file, skiprows=2)
            dados_mid_format = ajustar_lens(dados_file, lim_inf_wv, lim_sup_wv, len_wv)
            dados_ajust = np.zeros((len(dados_mid_format[0]), 2))
            dados_ajust[:, 0] = dados_mid_format[0]
            dados_ajust[:, 1] = dados_mid_format[1]

            lista_mask_dados = index_dos_intervalos(intervalos_mask, dados_ajust)
            #ax.plot(dados_ajust[:, 0], dados_ajust[:, 1], 'go', markersize=10, marker='.')

            chi_square = chisquare(lista_mask_dados[:, 1], f_exp=lista_mask_obs[:, 1])
            chi_square_value = chi_square[0]
            lista_file_chi_square.append([file, chi_square_value])
            print('')
            print(lista_file_chi_square)
            count_progress += 1

        print_progress(count_progress, len(files), prefix='Progress:', suffix='Complete',
                       decimals=1, bar_length=100)
        elapsed_time = time.time() - start_time
        print('')
        print('Tempo decorrido no cálculo do chi-quadrado: ' + str(elapsed_time))

    if intervalos_mask != None:
        for mask in (intervalos_mask):
            plt.axvspan(mask[0], mask[1], facecolor='#2ca02c', alpha=0.5)

    dados_plot = np.loadtxt('HIP57172B_total.dat', skiprows=0)
    ax.plot(dados_plot[:, coluna_wv], dados_plot[:, coluna_flux], markersize=0.5, color='black', label='Observ.')
    if min_wv != 0 and max_wv != 0:
        ax.set_xlim(min_wv, max_wv)
    if min_fl != 0 and max_fl != 0:
        ax.set_ylim(min_fl, max_fl)
    ax.legend()
    handles, labels = plt.gca().get_legend_handles_labels()
    #order = [3, 0, 6, 1, 5, 2, 4, 7] #Ordem das legendas
    #plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
    #print(lista_file_chi_square)
    plt.title('Synth_Lindgren')
    plt.ylabel('Flux')
    plt.xlabel('Wavelenght')
    if save == 'yes':
        plt.savefig(str('Spectrum of Lindgren') + str('.pdf'), bbox_inches='tight')
    plt.show()
    return lista_file_chi_square

def plot_chi(chi_data):
    temp_grid_values = []
    met_grid_values = []
    chi_squared_grid_values = []

    temp_pivot = float(chi_data[0][0][15:19])
    temp_grid_values.append(temp_pivot)

    list_chis = []
    for set in chi_data:
        if float(set[0][15:19]) == temp_pivot:
            if temp_pivot == float(chi_data[0][0][15:19]):
                if (set[0][25]) == '-':
                    met_grid_values.append(float(set[0][25:30]))
                else:
                    met_grid_values.append(float(set[0][25:29]))
            list_chis.append(set[1])
        else:
            temp_pivot = float(set[0][15:19])
            temp_grid_values.append(temp_pivot)
            chi_squared_grid_values.append(list_chis)

            list_chis = []
            list_chis.append(set[1])
    chi_squared_grid_values.append(list_chis)

    minimos_posi_temp = [1000] * (len(met_grid_values))
    minimos_posi_met = [1000] * (len(met_grid_values))
    minimos_chis = [1000] * (len(met_grid_values))
    for set in chi_data:
        if float(set[0][25:29]) in met_grid_values:  # Se a metelacidade faz parte da lista de metalicidade temos o index
            if (set[0][25]) == '-':
                index_lista = (met_grid_values.index(float(set[0][25:30])))
                posi_met = float(set[0][25:30])
            else:
                index_lista = (met_grid_values.index(float(set[0][25:29])))
                posi_met = float(set[0][25:29])
            if set[1] < minimos_chis[index_lista]:
                minimos_chis[index_lista] = set[1]
                minimos_posi_temp[index_lista] = float(set[0][15:19])
                minimos_posi_met[index_lista] = posi_met

    chi_squared_grid_values_transposed = (list(map(list, zip(*chi_squared_grid_values))))


    temp_contour, met_contour = np.meshgrid(temp_grid_values, met_grid_values)
    chi_squared_contour = chi_squared_grid_values_transposed

    X=temp_contour
    Y=met_contour
    Z=chi_squared_contour
    fig1, ax2 = plt.subplots(constrained_layout=True)
    CS = ax2.contourf(X, Y, Z, 10, cmap=plt.cm.viridis)

    ax2.plot(minimos_posi_temp, minimos_posi_met, 'ro--' , markersize=5, color='red', label=str('Minimum ') + str(r'$\mathregular{\chi^{2}}$'))

    ax2.set_title('HIP57172B')
    ax2.set_xlabel('Temperature [K]')
    ax2.set_ylabel('Metallicity')
    ax2.legend()
    cbar = fig1.colorbar(CS)
    cbar.ax.set_ylabel(str(r'$\mathregular{\chi^{2}}$'))
    plt.show()


ficheiros_teste = ["HIP57172B_total.dat",
                   "plansm.outtest_3900_4.46_0.16_1.00_r_0,011_1,000_1,000_3,500_0,000"]

valores_medios_HIP57172B = [3900, 4.46, 0.16, 1]

set_comparar_temp = [3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250,
                     4300, 4350, 4400, 4450, 4500]
set_comparar_logg = [4.46]
set_comparar_metal = [-0.25, -0.2, -0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25]
set_comparar_micro = [1]


linha_1 = [11763, 11768.4]
linha_2 = [11796.5, 11798]
linha_3 = [11820, 11836]
linha_4 = [11955, 11957.5]
linha_5 = [11968, 11979]

mask_lines = [linha_1, linha_2, linha_3, linha_4, linha_5]

ficheiros = construct_list_filenames(set_comparar_temp, set_comparar_logg, set_comparar_metal, set_comparar_micro,
                                     '_r_0,011_1,000_1,000_0,390_0,000')

tipo_lind = 'chi_quadrado'

file_obs = "HIP57172B_total.dat"

'''
chi_data = plot_dados_lindgren(ficheiros, tipo_lind, valores_medios_HIP57172B, mask_lines, file_obs, save='no', estilo='original',
                    coluna_wv=0, coluna_flux=1, min_wv=11945, max_wv=11995, min_fl=0.8, max_fl=1.02)


with open("test.txt", "wb") as fp:   #Pickling
    pickle.dump(chi_data, fp)
'''

with open("test.txt", "rb") as fp:   # Unpickling
    chi_data_loaded = pickle.load(fp)

plot_chi(chi_data_loaded)
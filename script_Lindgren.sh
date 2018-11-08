
#!/bin/bash

# Tentativa de fazer ciclo, bash

counter=1

# Localização de ficheiros

folder_script=$(echo ~/Masters)

folder_lines=$(echo ~/Masters/Lindgren/Lines)
name_file_lines=$(echo 'line_article_Lindgren.list')
#name_file_lines=$(echo 'lineMgIb_original.list')

folder_with_interpol=$(echo ~/Masters/school_codes/interpol_models_marcs) 
folder_where_error_files_go=$(echo ~/Masters/Onehag/Error_files_from_script) 

folder_atm=$(echo ~/Masters/Lindgren/Files_atm) 
folder_par=$(echo ~/Masters/Lindgren/Files_par) 

folder_plan=$(echo ~/Masters/Lindgren/Files_plan.outtest) 
folder_planraw=$(echo ~/Masters/Lindgren/Files_planraw.outtest) 
folder_plansm=$(echo ~/Masters/Lindgren/Files_plansm.outtest) 
folder_plansm_wv_parts=$(echo ~/Masters/Lindgren/Files_plansm.outtest/Wv_parts) 

# Intervalo de comprimentos de onda a ser estudado, vou ter que separar em intervalos de 400A devido a problemas de memoria do MOOG

declare -a min_wv=(11680.0)
 
declare -a max_wv=(12920.0)

# Parametros a serem feitos modelos por interpolação usando MOOG

declare -a temperat=(3900)

declare -a logg=(4.46) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!

declare -a met=(0) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!

declare -a micro=(1) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!


# Dados teste - Sun

#declare -a temperat=(5777)
#declare -a logg=(4.44) 
#declare -a met=(0)
#declare -a micro=(1)

cd $folder_lines
ls 
cp $name_file_lines $folder_script
cp $name_file_lines $folder_with_interpol

cd $folder_with_interpol

# Intervalo de comprimentos de onda a ser estudado

dif_wv=$(echo "$max_wv - $min_wv" | bc) #diferença entre intervalo de wv
div_int=$(echo "$dif_wv / 400" | bc) #divisao inteira 
div_sobra=$(echo "$dif_wv % 400" | bc) #resto

# Construçao de Array inicial, sem consideraçao por possivel resto

END_div_int=div_int
for ((i=1;i<=END_div_int;i++));
do
	valor_min_wv_iter=$(echo "$min_wv + (400 * ($i-1))" | bc)
	ARRAY_wv_intv[$i]=$valor_min_wv_iter
done

max_wv_from_intdiv=$(echo "${ARRAY_wv_intv[-1]} + 400" | bc)
index_for_max_wv_from_intdiv=$(echo "$div_int + 1" | bc)
ARRAY_wv_intv[$index_for_max_wv_from_intdiv]=$max_wv_from_intdiv

# Verificar se há resto ou não e caso haja incluir no Array


max_wv_from_rest=$(echo "$max_wv_from_intdiv + $div_sobra" | bc)
index_for_rest=$(echo "$div_int + 2" | bc)

if [ $max_wv_from_intdiv != $max_wv ];
then
    ARRAY_wv_intv[$index_for_rest]=$max_wv_from_rest
    END_wv_intv=div_int+1
    echo "Divisão não inteira"

else
    END_wv_intv=div_int
    echo "Divisão inteira"
fi

echo "Steps:"
echo ${ARRAY_wv_intv[*]}

for value_temp in "${temperat[@]}"
do
	for value_logg in "${logg[@]}"
	do
		for value_met in "${met[@]}"
		do
			for value_micro in "${micro[@]}"
			do

				echo $value_temp $value_logg $value_met $value_micro

				# Criar interpolação
				./make_model_marcs.bash $value_temp $value_logg $value_met $value_micro

				# Mudar nome de ficheiro de atmosferas criado
				mv out_marcs.atm  out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm

				for ((i=1;i<=END_wv_intv;i++));
				do
					valor_min_wv_iter=$(echo "${ARRAY_wv_intv[$i]}" | bc)
					valor_max_wv_iter=$(echo "${ARRAY_wv_intv[$i+1]}" | bc)

					# Criar ficheiro.
					exec 3<> synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par # Se nome for maior dá erro, coding is a dark magic

	    					# Conteudo do ficheiro a ser criado
						echo 'synth' >&3
						echo 'terminal    x11' >&3
						echo 'atmosphere  1' >&3
						echo 'lines       1' >&3
						echo 'flux/int    0' >&3
						echo 'synlimits' >&3
						echo $valor_min_wv_iter' '$valor_max_wv_iter' 0.001 10.0' >&3 # 400 parece ser intervalo optimo, intervalos grandes dá memory error
						echo 'plot        1' >&3		
						echo 'damping     0' >&3
						echo 'units       0' >&3
						echo 'molecules   2' >&3
						echo 'obspectrum  0' >&3
						echo 'plotpars 1' >&3
						echo '   '$valor_min_wv_iter' '$valor_max_wv_iter' -0.1  1.1' >&3
						echo '     0.0  0.0  0.0 1.003'  >&3  # ? 
						echo '   n 0.01 1.7 0.6 3.5 0.0' >&3  # ? r 0.01 1.7 0.6 3.5 0.0'
						echo 'standard_out 'plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'summary_out  'planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'smoothed_out 'plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'model_in     'out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm >&3
						echo 'lines_in     '$name_file_lines >&3

					# Fechar ficheiro criado
					exec 3>&-

					echo synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par | MOOGSILENT

					#Formatar numeros - casas decimais - de ficheiros plan, planraw e plans para ter sempre mesmo nº de digitos em todos os parametros
					
			
					temp_formatado_temporario=$(echo $value_temp | xargs printf "%.*f\n" 0)  #0 é nº de digitos
					logg_formatado_temporario=$(echo $value_logg | xargs printf "%.*f\n" 2)  #2 é nº de digitos
					met_formatado_temporario=$(echo $value_met | xargs printf "%.*f\n" 2)  #2 é nº de digitos
					micro_formatado_temporario=$(echo $value_micro | xargs printf "%.*f\n" 2)  #2 é nº de digitos

					#Transforma virgulas em ponts

					temp_formatado=$(echo $temp_formatado_temporario | tr ',' '.')
					logg_formatado=$(echo $logg_formatado_temporario | tr ',' '.')
					met_formatado=$(echo $met_formatado_temporario | tr ',' '.')
					micro_formatado=$(echo $micro_formatado_temporario | tr ',' '.')

					#Fim de formatar numeros

					#Mudar nome de ficheiros para terem numeros corretamente formatados - casas decimais

					mv plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter plan.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv plan.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_plan

					mv planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter planraw.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv planraw.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_planraw

					mv plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter plansm.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv plansm.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_plansm_wv_parts
					
					#out_marcs tem que estar fora para poder reutilizar no ciclo pois .atm é sempre o mesmo
					
					mv synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par $folder_par

				done #fim do ciclo for das divisoes inteiras

			mv out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm $folder_atm

			done 
		done 
	done
done

cd $folder_with_interpol
rm $name_file_lines 
cd $folder_script
rm $name_file_lines 

cd $folder_with_interpol



#Todos os ficheiros que não são criados corretamente ficam com ficheiros parcialmente errados no folder do sript, para não encher folder mando para uma pasta especifica

#if [ -e out_marcs_fromscript_* ]
if [ `ls -1 out_marcs_fromscript_*  2>/dev/null | wc -l ` -gt 0 ];
then
    mv out_marcs_fromscript_* $folder_where_error_files_go
    mv synth_sun_fromscript_* $folder_where_error_files_go
    mv plan.outtest_* $folder_where_error_files_go
    mv planraw.outtest_* $folder_where_error_files_go
    mv plansm.outtest_* $folder_where_error_files_go
    echo " "
    echo "Existem ficheiros movidos para folder de Erros!"
    echo " "
else
    echo " "
    echo "0 ficheiros para folder de Erros"
    echo " "
fi

#Todos os ficheiros que não são criados corretamente estão na pasta


echo " "
echo "Script terminado"
echo " "

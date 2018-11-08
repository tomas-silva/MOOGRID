
#!/bin/bash

# Tentativa de fazer ciclo, bash

counter=1

# Localização de ficheiros

folder_script=$(echo ~/Masters)

folder_lines=$(echo ~/Masters/Sun_MOOG)
name_file_lines=$(echo 'lineMgIb.list')

folder_with_interpol=$(echo ~/Masters/school_codes/interpol_models_marcs) 
folder_where_error_files_go=$(echo ~/Masters/Sun_MOOG/Error_files_from_script) 

folder_atm=$(echo ~/Masters/Sun_MOOG/Files_atm) 
folder_par=$(echo ~/Masters/Sun_MOOG/Files_par) 

folder_plan=$(echo ~/Masters/Sun_MOOG/Files_plan.outtest) 
folder_planraw=$(echo ~/Masters/Sun_MOOG/Files_planraw.outtest) 
folder_plansm=$(echo ~/Masters/Sun_MOOG/Files_plansm.outtest) 

# Parametros a serem feitos modelos por interpolação usando MOOG

declare -a temperat=(5600 5650 5700 5750 5777 5800 5850 5900 5950 6000)

declare -a logg=(4.3 4.4 4.44 4.5 4.6) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!

declare -a met=(-0.4 -0.2 -0.1 0 0.1 0.2 0.4) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!

declare -a micro=(0.6 0.8 -1.1 1 1.1 1.2 1.4) #Não usar algo tipo '1.0', usar '1', '1.0' pode dar erro !!!


# Dados teste - Sun

#declare -a temperat=(5777)
#declare -a logg=(4.44) 
#declare -a met=(0)
#declare -a micro=(1)

cd $folder_lines
ls 
cp $name_file_lines $folder_script

cd $folder_with_interpol


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
				
				# Criar ficheiro.
				exec 3<> synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.par

    					# Conteudo do ficheiro a ser criado
					echo 'synth' >&3
					echo 'terminal    x11' >&3
					echo 'atmosphere  1' >&3
					echo 'lines       1' >&3
					echo 'flux/int    0' >&3
					echo 'abundances 1 1' >&3
	 				echo '	 12  0.02' >&3
					echo 'synlimits' >&3
					echo '5180.0 5187.0 0.001 10.0' >&3 
					echo 'plot        1' >&3 #estava 2		
					echo 'damping     0' >&3
					echo 'units       0' >&3
					echo 'molecules   2' >&3
					echo 'obspectrum  0' >&3 #estava 5
					echo 'plotpars 1' >&3
					echo '   5180.0 5187.0 -0.1  1.1' >&3
					echo '     0.0  0.0  0.0 1.003'  >&3
					echo '   r 0.01 1.7 0.6 3.5 0.0' >&3
					echo 'standard_out 'plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro >&3
					echo 'summary_out  'planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro >&3
					echo 'smoothed_out 'plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro >&3
					echo 'model_in      'out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm >&3
					echo 'lines_in     '$name_file_lines >&3
					echo 'histogram    1' >&3

				
				# Fechar ficheiro criado
				exec 3>&-

				echo synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.par | MOOGSILENT

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

				mv plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro plan.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado
				mv plan.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado $folder_plan

				mv planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro planraw.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado
				mv planraw.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado $folder_planraw

				mv plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro plansm.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado
				mv plansm.outtest_$temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado $folder_plansm


				mv out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm $folder_atm

				mv synth_sun_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.par $folder_par	

			done 
		done 
	done
done

#Todos os ficheiros que não são criados corretamente ficam com ficheiros parcialmente errados no folder do sript, para não encher folder mando para uma pasta especifica

if [ -e out_marcs_fromscript_* ]
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

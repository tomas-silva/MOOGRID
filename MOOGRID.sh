
#!/bin/bash

###
# Run script in terminal: ./name_of_script
###

: '
Inputs:

A) Location of files - script, lines, interpolation codes, folders for files with errors, input MOOG files
B) Wavelength characteristics MOOG
C) Smoothing parameters for MOOG
D) Star parameters to be studied

Relevant Outputs:
Flux vs Wavelength
plansm.outtest_temp_logg_metalicity_microturbulance_smoothing parameters_wavelength interval

'
###
###
### Inputs

## A) Location of files

folder_script=$(echo ~/Master_folder) # Folder of this script

folder_lines=$(echo /Master_folder/Lines) # Folder of the line list
name_file_lines=$(echo 'lines.list')  # Name of the line list

folder_with_interpol=$(echo ~/Master_folder/school_codes/interpol_models_marcs) # Folder for interpolation codes
folder_where_error_files_go=$(echo /Master_folder/Error_files_from_script) # Folder for files with errors

# MOOG files

folder_atm=$(echo /Master_folder/Files_atm) 
folder_par=$(echo /Master_folder/Files_par) 

folder_plan=$(echo /Master_folder/Files_plan.outtest) 
folder_planraw=$(echo /Master_folder/Files_planraw.outtest) 
folder_plansm=$(echo /Master_folder/Files_plansm_synth.outtest) # connected with below folder
folder_plansm_wv_parts=$(echo /Master_folder/Files_plansm_synth.outtest/Wv_parts) # connected with folder above, saves the files created in the different wavelenghts


## B) Wavelength characteristics MOOG

declare -a min_wv=(11680.0) 
 
declare -a max_wv=(13000.0) 

declare -a interv_wv=(10) # Small values to avoid memory errors with MOOG

declare -a step_wv_MOOG=(0.001) 

## C) Smoothing type

plot_par_smooth_type='r'
plot_par_fwhm_g=0.011
plot_par_vsin=1.0 # correr com 1.0 no int mais alargado
plot_par_rot=1.0 
plot_par_fwhm_macro=0.39
plot_par_fwhm_lorentz=0.0


## D) Star parameters

# HIP 57172B

# N. combinations: 5720 (Expected running time: 100 hrs)

declare -a temperat=(3700 3750 3800 3850 3900 3950 4000 4050 4100 4150 4200)
declare -a logg=(4.20 4.25 4.30 4.35 4.40 4.45 4.50 4.55 4.60 4.65) 
declare -a met=(-0.3 -0.25 -0.2 -0.15 -0.1 -0.05 0 0.05 0.10 0.15 0.20 0.25 0.30)
declare -a micro=(0 0.5 1.0 1.5)

# Sun

#declare -a temperat=(5777)
#declare -a logg=(4.44) 
#declare -a met=(0)
#declare -a micro=(1)

clean_folders='yes'

### End - Inputs

### Formating plotpar so that it always has the same number of decimal places and create the name for the files in an uniform way (Important for use in Python so we can easly get the parameters)

plot_par_fwhm_g_formatado=$(echo $plot_par_fwhm_g | xargs printf "%.*f\n" 3)  # 3 decimal places 
plot_par_vsin_formatado=$(echo $plot_par_vsin | xargs printf "%.*f\n" 3)  # 3 decimal places
plot_par_rot_formatado=$(echo $plot_par_rot | xargs printf "%.*f\n" 3)  # 3 decimal places
plot_par_fwhm_macro_formatado=$(echo $plot_par_fwhm_macro | xargs printf "%.*f\n" 3)  # 3 decimal places
plot_par_fwhm_lorentz_formatado=$(echo $plot_par_fwhm_lorentz | xargs printf "%.*f\n" 3)  # 3 decimal places

plotpars_line3_input=$(echo "   "$plot_par_smooth_type' '$plot_par_fwhm_g_formatado' '$plot_par_vsin_formatado' '$plot_par_rot_formatado' '$plot_par_fwhm_macro_formatado' '$plot_par_fwhm_lorentz_formatado"") # Input for the .par file created.

plotpars_line3=$(echo $plot_par_smooth_type'_'$plot_par_fwhm_g_formatado'_'$plot_par_vsin_formatado'_'$plot_par_rot_formatado'_'$plot_par_fwhm_macro_formatado'_'$plot_par_fwhm_lorentz_formatado)
# input para nome de ficheiros no final

### End - Formating plotpar


### Linelist copy - Enter folders to copy the linelist file to the interpolation folder

cd $folder_lines
 
cp $name_file_lines $folder_script
cp $name_file_lines $folder_with_interpol

cd $folder_with_interpol

### End - Linelist copy


### Creation of wavelength steps to be studied

dif_wv=$(echo "$max_wv - $min_wv" | bc) # Diference between wavelength intervals
div_int=$(echo "$dif_wv / $interv_wv" | bc) # Entire division - Remainde = 0
div_sobra=$(echo "$dif_wv % $interv_wv" | bc) # Remainder

## Construction of the wavelength array

END_div_int=$div_int

if [ $END_div_int -eq 0 ]; # If interval is smaller than step
then
	ARRAY_wv_intv[1]=$min_wv
	ARRAY_wv_intv[2]=$max_wv
	END_wv_intv=$div_int+1 # Do one iteraction in the cicle that creates the files
else # If interval bigger than step
	for ((i=1;i<=END_div_int;i++)); 
	do
		valor_min_wv_iter=$(echo "$min_wv + ($interv_wv * ($i-1))" | bc)
		ARRAY_wv_intv[$i]=$valor_min_wv_iter
	done
	max_wv_from_intdiv=$(echo "${ARRAY_wv_intv[-1]} + $interv_wv" | bc)
	index_for_max_wv_from_intdiv=$(echo "$div_int + 1" | bc)
	ARRAY_wv_intv[$index_for_max_wv_from_intdiv]=$max_wv_from_intdiv

	# Verify if there is remainder and if there is include in the Array


	max_wv_from_rest=$(echo "$max_wv_from_intdiv + $div_sobra" | bc)
	index_for_rest=$(echo "$div_int + 2" | bc)

	if [ $max_wv_from_intdiv != $max_wv ];
	then
	    ARRAY_wv_intv[$index_for_rest]=$max_wv_from_rest
	    END_wv_intv=$div_int+1
	    echo "Divisão não inteira"

	else
	    END_wv_intv=$div_int
	    echo "Divisão inteira"
	fi
fi


echo "Steps:"
echo ${ARRAY_wv_intv[*]}

### End - Creation of wavelength steps to be studied

### Creation of the files for our parameter space

for value_temp in "${temperat[@]}"
do
	for value_logg in "${logg[@]}"
	do
		for value_met in "${met[@]}"
		do
			for value_micro in "${micro[@]}"
			do

				echo $value_temp $value_logg $value_met $value_micro

				# Create interpolation
				./make_model_marcs.bash $value_temp $value_logg $value_met $value_micro

				# Use of 20 moleculs instead of 19, this is adding FeH (126.0)

				file_mol='out_marcs.atm'
				perl -pi -e 's/NMOL      19/NMOL      20/g' $file_mol
				perl -pi -e 's/8.1    822.0     22.1/8.1    822.0     22.1    126.0/g' $file_mol

				# Change name of the atmosphere file created
				mv out_marcs.atm  out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm

				for ((i=1;i<=END_wv_intv;i++));
				do
					valor_min_wv_iter=$(echo "${ARRAY_wv_intv[$i]}" | bc)
					valor_max_wv_iter=$(echo "${ARRAY_wv_intv[$i+1]}" | bc)

					# Create file
					exec 3<> synth_fscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par # If name is any bigger it gives error - black magic

	    					# Content of the file being created
						echo 'synth' >&3
						echo 'terminal    x11' >&3
						echo 'atmosphere  1' >&3
						echo 'lines       1' >&3
						echo 'flux/int    0' >&3
						#echo 'abundances 7 1' >&3
	 					#echo '	 12  0.65' >&3   #Mg 0.65
						echo 'synlimits' >&3
						echo $valor_min_wv_iter' '$valor_max_wv_iter' '$step_wv_MOOG' 1.0' >&3 # Attention - small intervals to avoid memory errors
						echo 'plot        1' >&3		
						echo 'damping     1' >&3
						echo 'units       0' >&3
						echo 'molecules   2' >&3
						echo 'obspectrum  0' >&3
						echo 'plotpars 1' >&3
						echo '   '$valor_min_wv_iter' '$valor_max_wv_iter' -0.1  1.1' >&3
						echo '     0.0  0.0  0.0 1.003'  >&3 
						echo $plotpars_line3_input >&3 
						echo 'standard_out 'plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'summary_out  'planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'smoothed_out 'plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter >&3
						echo 'model_in     'out_marcs_fromscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro.atm >&3
						echo 'lines_in     '$name_file_lines >&3

					# Closing created file
					exec 3>&-

					echo synth_fscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par | MOOGSILENT

					## Formating numbers - Decimal places - so files plan, planraw, and plans all have the same number of digits in all the parameters					
			
					temp_formatado_temporario=$(echo $value_temp | xargs printf "%.*f\n" 0)  # 0 decimal places
					logg_formatado_temporario=$(echo $value_logg | xargs printf "%.*f\n" 2)  # 2 decimal places
					met_formatado_temporario=$(echo $value_met | xargs printf "%.*f\n" 2)  # 2 decimal places
					micro_formatado_temporario=$(echo $value_micro | xargs printf "%.*f\n" 2)  # 2 decimal places

					# Changes commas to points

					temp_formatado=$(echo $temp_formatado_temporario | tr ',' '.')
					logg_formatado=$(echo $logg_formatado_temporario | tr ',' '.')
					met_formatado=$(echo $met_formatado_temporario | tr ',' '.')
					micro_formatado=$(echo $micro_formatado_temporario | tr ',' '.')

					## End - Formating numbers

					## Changes names of the files so they have numbers correctly formated - decimal places

					name_vars_final=$(echo $temp_formatado'_'$logg_formatado'_'$met_formatado'_'$micro_formatado'_'$plotpars_line3)

					mv plan.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter plan.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv plan.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_plan

					mv planraw.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter planraw.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv planraw.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_planraw

					mv plansm.outtest_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_'$valor_min_wv_iter'_'$valor_max_wv_iter plansm.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter
					mv plansm.outtest_$name_vars_final'_'$valor_min_wv_iter'_'$valor_max_wv_iter $folder_plansm_wv_parts
					
					# out_marcs is outside the cycle so it can be re-used, since .atm is always the same
					
					mv synth_fscript_$value_temp'_'$value_logg'_'$value_met'_'$value_micro'_Pr'.par $folder_par


				done # End of divison cycle
				
				## Union of files

				cd $folder_plansm_wv_parts # Folder where all diferent fractions of wavelength were created

				number_of_elements_in_ARRAY=${#ARRAY_wv_intv[@]} # Nº of elements in the array
				
				if [ $number_of_elements_in_ARRAY -eq 2 ]; # If number of elements is only 2, this means, only one file
				then
					tail -n +3 <plansm.outtest_$name_vars_final'_'${ARRAY_wv_intv[1]}'_'${ARRAY_wv_intv[2]} >parcial_uniq.txt # Ignores first two lines of the file

					# Creates header
					echo 'start =  '${ARRAY_wv_intv[1]}'     stop =  '${ARRAY_wv_intv[2]}'     step =      '$step_wv_MOOG'' | cat - parcial_uniq.txt > temp && mv temp parcial_uniq.txt
					echo 'Final file - from unique file' | cat - parcial_uniq.txt > temp && mv temp parcial_uniq.txt	
				else # If number of elements bigger than 2, this means, multiple files
					for ((i=1;i<=number_of_elements_in_ARRAY-1;i++)); do # -1 because last one can have max wavelength different from the multiple of the wavelength 
						# Want a $i with 3 digits, if it isn't parcial10 comes before parcial9 and when when concatenated (cat) everything becomes deformed						
						i_parcial_formatado=$(printf %03d $i)  # 1 -> 001
	
						if [ ${ARRAY_wv_intv[i]} == $min_wv ];
						then
							
							tail -n +3 <plansm.outtest_$name_vars_final'_'${ARRAY_wv_intv[i]}'_'${ARRAY_wv_intv[i+1]} >parcial$i_parcial_formatado.txt # Ignores first two lines of the file

							# Creates header
							echo 'start =  '$min_wv'     stop =  '$max_wv'     step =      '$step_wv_MOOG'' | cat - parcial$i_parcial_formatado.txt > temp && mv temp parcial$i_parcial_formatado.txt
							echo 'Final file - from '$(echo "$number_of_elements_in_ARRAY-1" | bc)' files with wv generic interval of '$interv_wv'' | cat - parcial$i_parcial_formatado.txt > temp && mv temp parcial$i_parcial_formatado.txt
						else	
							tail -n +4 <plansm.outtest_$name_vars_final'_'${ARRAY_wv_intv[i]}'_'${ARRAY_wv_intv[i+1]} >parcial$i_parcial_formatado.txt # Deletes 3 first lines, 2 from the text and 1 so the numbers dont repeat (they are equal to the last ones from the previous)
						fi
					done
				fi

				if [ -f parcial_uniq.txt ]; # If there is only one file
				then
					# Want to keep the header - move file to ouside folder, create file and them remove the other
					mv parcial_uniq.txt $folder_plansm
					cd $folder_plansm
					rm plansm.outtest_$name_vars_final
					cat parcial_uniq.txt >> plansm.outtest_$name_vars_final
					#cat parcial_uniq.txt >> plansm.outtest_3900_4.46_0.00_1.00'_'${ARRAY_wv_intv[1]}'_'${ARRAY_wv_intv[-1]}
					rm parcial_uniq.txt
				else
					# Concatenate files
					cat parcial* >> plansm.outtest_$name_vars_final
					#cat parcial* >> plansm.outtest_3900_4.46_0.00_1.00'_'${ARRAY_wv_intv[1]}'_'${ARRAY_wv_intv[-1]}
					rm parcial*
					mv plansm.outtest_$name_vars_final $folder_plansm
				fi
				## End - Union of files

			cd $folder_with_interpol
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


# All the files that were not correctly created result in parcial files leftover in the script folder. So it doesn't occupy space in this folder we move them to an error files specific one

if [ `ls -1 out_marcs_fromscript_*  2>/dev/null | wc -l ` -gt 0 ]; # If there is a file out_marcs_fromscript_*
then
    mv out_marcs_fromscript_* $folder_where_error_files_go
    mv synth_fscript_* $folder_where_error_files_go
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

# All files are in their respective folders

# Cleaning folders to save space

if [ $clean_folders == 'yes' ];
then
    cd $folder_plan
    rm plan.outtest*
    cd $folder_planraw
    rm planraw.outtest*
    cd $folder_plansm_wv_parts
    rm plansm.outtest*
fi


echo " "
echo "Script terminado"
echo " "

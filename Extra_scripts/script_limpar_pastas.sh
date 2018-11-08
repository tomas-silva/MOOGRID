
#!/bin/bash

cd Files_atm/
rm out_marcs_fromscript_3*
rm out_marcs_fromscript_4*
rm out_marcs_fromscript_5*
rm out_marcs_fromscript_6*

cd ..

cd Files_par/
rm synth_sun_fromscript_3*
rm synth_sun_fromscript_4*
rm synth_sun_fromscript_5*
rm synth_sun_fromscript_6*

cd ..

cd Files_plan.outtest/
rm plan.outtest_3*
rm plan.outtest_4*
rm plan.outtest_5*
rm plan.outtest_6*

cd ..

cd Files_planraw.outtest/
rm planraw.outtest_3*
rm planraw.outtest_4*
rm planraw.outtest_5*
rm planraw.outtest_6*

cd ..

cd Files_plansm.outtest/
rm plansm.outtest_3*
rm plansm.outtest_4*
rm plansm.outtest_5*
rm plansm.outtest_6*

echo
echo Tudo limpo
echo 
echo Verificaçao:
ls

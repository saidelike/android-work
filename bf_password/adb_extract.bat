mkdir out
FOR /F %%G IN (files_unlock.txt) DO adb pull %%G out
FOR /F %%G IN (files_list_DZ.txt) DO adb pull %%G out

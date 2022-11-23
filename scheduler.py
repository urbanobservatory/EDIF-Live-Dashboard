# checks whether should update or use previously collected data
# only allow update if last updated over 4 mins ago (i.e. not at very start)

import time
import run

def update(variable, dict_all, src):
    print(time.time() - (time.mktime(dict_all[variable]['end'].timetuple())))
    if time.time() - (time.mktime(dict_all[variable]['end'].timetuple())) > 240 \
    or variable not in dict_all:
        if src == 'UO' or src == 'UOFile':
            run.uo(variable, dict_all, src)
        elif src == 'UDX' or src == 'UDXFile':
            run.udx(variable, dict_all)
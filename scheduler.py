# checks whether should update or use previously collected data
# only allow update if last updated over 4 mins ago (i.e. not at very start)

import time
import run

def update(variable, location, locations, src):
    #print(time.time() - (time.mktime(dict_all[variable]['end'].timetuple())))
    if time.time() - (time.mktime(locations[location][variable]['end'].timetuple())) > 240 \
    or variable not in locations[location]:
        # if src == 'UO' or src == 'UOFile':
        #     run.uo(variable, dict_all, src)
        # elif src == 'UDX' or src == 'UDXFile':
        run.udx(locations, src)
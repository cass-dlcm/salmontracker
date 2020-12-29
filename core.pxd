import cython

@cython.locals(reader=object)
cpdef bint hasJobs(str data)

@cython.locals(result=list, reader=object, job=object)
cpdef list listAllUsers(str data)

@cython.locals(result=dict, reader=object, line=bytes, job=object, i=cython.int)
cpdef dict findWeaponsAndStageByRotation(str data, int rotation)

@cython.locals(foundIds=list, reader=object, line=bytes, job=object, teammate=object)
cpdef list findPlayerIdByName(str data, str player)

cpdef str getValMultiDimensional(object data, list statArr)

@cython.locals(statArr=list, sumVal=cython.double, maxVal=cython.double, minVal=cython.double, vals=list, count=cython.double, line=bytes, job=object, val=cython.double)
cpdef tuple statSummary(str data, str stat)

@cython.locals(sumVal=cython.double, count=cython.double, line=bytes, job=object)
cpdef double waveClearPercentageWithWeapon(str data, str weapon)

@cython.locals(sumVal=cython.int, w=object)
cpdef int sumStatWaves(object data, str stat)

@cython.locals(attrsList=list, attrs=list, p=object)
cpdef list getPlayersAttribute(object data, str attr)

@cython.locals(attrs=str, attrsList=list, i=cython.int)
cpdef str getWavesAttribute(object data, str attr)

@cython.locals(result=str, stats=list, reader=object, clearCount=cython.double, waveTwoCount=cython.double, waveOneCount=cython.double, sumVal=cython.double[6], maxVal=cython.double[6], minVal=cython.double[6], vals=list, count=cython.int, line=bytes, job=object, i=cython.int, val=cython.double)
cpdef str getOverview(str data)

cpdef void printGeneral(object data)
cpdef void printWaves(object data)

@cython.locals(i=cython.int, player=object)
cpdef void printWeapons(object data)

@cython.locals(i=cython.int)
cpdef void printSpecials(object data)

cpdef void printPlayers(object data)

@cython.locals(results=list, names=dict, appearances=dict, boss=object, my_data=dict, teammate=object, teammate_data=dict)
cdef list getBosses(object data)

@cython.locals(count=cython.int, reader=object, line=bytes)
cpdef object getSingleJob(str data, int index=*)

@cython.locals(names=list, namesStr=str, name=str, bosses=list, listBosses=list, boss=cython.int)
cpdef void printBosses(object data)

@cython.locals(reader=object, results=list, line=bytes, job=object)
cpdef list getArrayOfStat(str data, str stat)

@cython.locals(headers=dict, fileName=str, url=str, recentId=cython.int, reader=object, writer=object, line=object, prevLastId=cython.int, params=dict, temp=list, lastId=cython.int, job=dict, result=object)
cpdef str init(str mode, str data_path, str api_key=*)

@cython.locals(jobs=list, reader=object, line=bytes)
cpdef list loadJobsFromFile(str data)
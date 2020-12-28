import cython

@cython.declare(locale=str, grizzcoWeapons=tuple)

@cython.locals(reader=object)
cpdef bint hasJobs(str data)

@cython.locals(result=list, reader=object, job=object)
cpdef list listAllUsers(str data)

@cython.locals(result=dict, reader=object, line=str, job=object, i=cython.int)
cpdef dict findWeaponsAndStageByRotation(str data, int rotation)

@cython.locals(foundIds=list, reader=object, line=str, job=object, teammate=object)
cpdef list findPlayerIdByName(str data, str player)


cpdef str getValMultiDimensional(object data, list statArr)
cpdef tuple statSummary(str data, str stat)
cpdef double waveClearPercentageWithWeapon(str data, str weapon)
cpdef int sumStatWaves(object data, str stat)
cpdef list getPlayersAttribute(object data, str attr)
cpdef str getWavesAttribute(object data, str attr)
cpdef str getOverview(str data)
cpdef void printGeneral(object data)
cpdef void printWaves(object data)
cpdef void printWeapons(object data)
cpdef void printSpecials(object data)
cpdef void printPlayers(object data)
cdef list getBosses(object data)
cpdef object getSingleJob(str data, int index=*)
cpdef void printBosses(object data)
cpdef list getArrayOfStat(str data, str stat)
cpdef str init(str mode, str api_key=*)
cpdef list loadJobsFromFile(str data)
import cython

@cython.locals(filters=list, stat=str, playerName=str, playerId=list, val=str, mode=str, clearAfter=str, i=cython.int, weapons=list, stageChoice=str, rotations=list, rot=int, comparison=str, wave=int)
cpdef list filterBy(list dataFile)

@cython.locals(which=str, i=cython.int, chosenList=cython.int)
cdef void printOverview(list dataFile)

@cython.locals(reader=object, job=object)
cdef void printAllJobs(str dataFile)

@cython.locals(which=str, i=cython.int, chosenList=cython.int)
cdef void printJobs(list dataFile)

@cython.locals(i=cython.int, first=cython.int, second=cython.int, stat=str, firstStat=list, secondStat=list, t=cython.double, p=cython.double)
cdef void hypothesisTesting(list dataFile)

@cython.locals(which=str, stat=str, mode=str, i=cython.int, chosenList=cython.int)
cdef void sortAttributeByStat(list dataFile)

@cython.locals(which=str, weaopn=str, i=cython.int, chosenList=cython.int)
cdef void waveClearPercentageWithWeapon(list dataFile)

@cython.locals(mode=str)
cpdef void processData(list dataFile)
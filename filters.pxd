import cython

@cython.locals(reader=object, writerA=object, writerB=object, line=str, job=object)
cpdef tuple filterJobs(str data, str outpath, object filterFunction)

@cython.locals(reader=object, writerA=object, writerB=object, line=str, job=object, found=cython.bint, funct=object)
cpdef tuple filterJobsOr(str data, str outpath, list filterFunctions)

@cython.locals(reader=object, writerA=object, writerB=object, line=str, job=object, found=cython.bint, funct=object)
cpdef tuple filterJobsAnd(str data, str outpath, list filterFunctions)

@cython.locals(outPath=str, filterFunctions=list, player=str)
cpdef tuple hasPlayers(str data, list players, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, weapon=str)
cpdef tuple hasWeapons(str data, list weapons, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, weapon=str)
cpdef tuple usesWeapons(str data, list weapons, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, stage=str)
cpdef tuple onStages(str data, list stages, str mode=*)

cpdef tuple withSpecial(str data, str special)

@cython.locals(filterFunctions=list, outPath=str, reason=str)
cpdef tuple failReasons(str data, list reasons, str mode=*)

@cython.locals(filterFunctions=list, outPath=str, rotation=cython.int)
cpdef tuple duringRotationInts(str data, list rotations, str mode=*)

@cython.locals(outPath=str)
cpdef tuple clearWave(str data, int wave, str comparison=*)

@cython.locals(outPath=str)
cpdef tuple dangerRate(str data, double rate, str comparison=*)

@cython.locals(filterFunctions=list, outPath=str, tide=str)
cpdef tuple hasTides(str data, list tides, str mode=*)

@cython.locals(filterFunctions=list, outPath=str, event=str)
cpdef tuple hasEvents(str data, list events, str mode=*)

@cython.locals(weaponList=list, grizzWeapon=tuple, new=dict, weaponDict=dict, i=dict, filterFunctions=list, outPath=str, wtype=str)
cpdef tuple hasWeaponTypes(str data, list types, str mode=*)
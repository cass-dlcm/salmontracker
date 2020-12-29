import cython

@cython.locals(reader=object, writerA=object, writerB=object, line=bytes, job=object, jobsWith=list, jobsWithout=list)
cpdef object filterJobs(str location, object data, object filterFunction, str outpath)

@cython.locals(reader=object, writerA=object, writerB=object, line=bytes, job=object, found=cython.bint, funct=object, jobsWith=list, jobsWithout=list)
cpdef object filterJobsOr(str location, object data, list filterFunctions, str outpath)

@cython.locals(reader=object, writerA=object, writerB=object, line=bytes, job=object, found=cython.bint, funct=object, jobsWith=list, jobsWithout=list)
cpdef object filterJobsAnd(str location, object data, list filterFunctions, str outpath)

@cython.locals(outPath=str, filterFunctions=list, player=str)
cpdef object hasPlayers(str location, object data, list players, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, weapon=str)
cpdef object hasWeapons(str location, object data, list weapons, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, weapon=str)
cpdef object usesWeapons(str location, object data, list weapons, str mode=*)

@cython.locals(outPath=str, filterFunctions=list, stage=str)
cpdef object onStages(str location, object data, list stages, str mode=*)

cpdef object withSpecial(str location, object data, str special)

@cython.locals(filterFunctions=list, outPath=str, reason=str)
cpdef object failReasons(str location, object data, list reasons, str mode=*)

@cython.locals(filterFunctions=list, outPath=str, rotation=cython.int)
cpdef object duringRotationInts(str location, object data, list rotations, str mode=*)

@cython.locals(outPath=str)
cpdef object clearWave(str location, object data, int wave, str comparison=*)

@cython.locals(outPath=str)
cpdef object dangerRate(str location, object data, double rate, str comparison=*)

@cython.locals(filterFunctions=list, outPath=str, tide=str)
cpdef object hasTides(str location, object data, list tides, str mode=*)

@cython.locals(filterFunctions=list, outPath=str, event=str)
cpdef object hasEvents(str location, object data, list events, str mode=*)

@cython.locals(weaponList=list, grizzWeapon=tuple, new=dict, weaponDict=dict, i=dict, filterFunctions=list, outPath=str, wtype=str)
cpdef object hasWeaponTypes(str location, object data, list types, str mode=*)
cdef tuple filterJobs(str data, str outpath, object filterFunction)
cdef tuple filterJobsOr(str data, str outpath, list filterFunctions)
cdef tuple filterJobsAnd(str data, str outpath, list filterFunctions)
cpdef tuple hasPlayers(str data, list players, str mode=*)
cpdef tuple hasWeapons(str data, list weapons, str mode=*)
cpdef tuple usesWeapons(str data, list weapons, str mode=*)
cpdef tuple onStages(str data, list stages, str mode=*)
cpdef tuple withSpecial(str data, str special)
cpdef tuple failReasons(str data, list reasons, str mode=*)
cpdef tuple duringRotationInts(str data, list rotations, str mode=*)
cpdef tuple clearWave(str data, int wave, str comparison=*)
cpdef tuple dangerRate(str data, double rate, str comparison=*)
cpdef tuple hasTides(str data, list tides, str mode=*)
cpdef tuple hasEvents(str data, list events, str mode=*)
cpdef tuple hasWeaponTypes(str data, list types, str mode=*)
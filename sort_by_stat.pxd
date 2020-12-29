import cython

@cython.locals(item=dict)
cdef bint hasVal(list var, object val)

@cython.locals(weaponsList=dict, grizzWeapon=tuple, results=list, result=dict, filterPaths=tuple, withVal=str, withoutVal=str)
cpdef void sortWeapons(str data, str stat)

@cython.locals(stageDict=dict, stageList=list, reader=object, line=bytes, job=object, stage=dict)
cpdef void sortStages(str data, str stat)

@cython.locals(specialDict=dict, specialList=list, reader=object, line=bytes, job=object, special=dict)
cpdef void sortSpecial(str data, str stat)

@cython.locals(rotationList=list, rotationResultsList=list, reader=object, job=object, rotation=cython.int, result=dict, filterPaths=tuple, withVal=str, withoutVal=str)
cpdef void sortRotation(str data, str stat)
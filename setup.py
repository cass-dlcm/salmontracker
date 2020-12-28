from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    ext_modules=cythonize(
        [
            Extension("objects", ["objects.py", "objects.pxd"]),
            Extension("core", ["core.py", "core.pxd"]),
            Extension("filters", ["filters.py", "filters.pxd"]),
            Extension("main", ["main.py", "main.pxd"]),
            Extension("sort_by_stat", ["sort_by_stat.py", "sort_by_stat.pxd"]),
        ],
        compiler_directives={"language_level": "3"},
    ),
    cmdclass={"build_ext": build_ext},
)

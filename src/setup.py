from Cython.Build import cythonize
from distutils.core import setup, Extension

setup(
    name = "Consolidated Loop",
    ext_modules = cythonize("0401067_DM.py")
)
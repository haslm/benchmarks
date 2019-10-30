# This file is generated by numpy's setup.py
# It contains system_info results at the time of building this package.
__all__ = ["get_info","show"]



import os
import sys

extra_dll_dir = os.path.join(os.path.dirname(__file__), '.libs')

if sys.platform == 'win32' and os.path.isdir(extra_dll_dir):
    os.environ.setdefault('PATH', '')
    os.environ['PATH'] += os.pathsep + extra_dll_dir

lapack_mkl_info={}
lapack_opt_info={'language': 'c', 'libraries': ['openblas', 'openblas'], 'library_dirs': ['/usr/local/lib'], 'define_macros': [('HAVE_CBLAS', None)]}
openblas_info={'language': 'c', 'libraries': ['openblas', 'openblas'], 'library_dirs': ['/usr/local/lib'], 'define_macros': [('HAVE_CBLAS', None)]}
openblas_lapack_info={'language': 'c', 'libraries': ['openblas', 'openblas'], 'library_dirs': ['/usr/local/lib'], 'define_macros': [('HAVE_CBLAS', None)]}
blis_info={}
blas_mkl_info={}
blas_opt_info={'language': 'c', 'libraries': ['openblas', 'openblas'], 'library_dirs': ['/usr/local/lib'], 'define_macros': [('HAVE_CBLAS', None)]}

def get_info(name):
    g = globals()
    return g.get(name, g.get(name + "_info", {}))

def show():
    for name,info_dict in globals().items():
        if name[0] == "_" or type(info_dict) is not type({}): continue
        print(name + ":")
        if not info_dict:
            print("  NOT AVAILABLE")
        for k,v in info_dict.items():
            v = str(v)
            if k == "sources" and len(v) > 200:
                v = v[:60] + " ...\n... " + v[-60:]
            print("    %s = %s" % (k,v))
    
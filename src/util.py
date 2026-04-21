
# Simple method for printing version numbers of imported modules for sanity
# Input: type: module name
# Output: type: string

def ver(module):
    version = getattr(module, "__version__", "Unknown")
    print(f"{module.__name__}: {version}")

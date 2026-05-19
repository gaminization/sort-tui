import os
import glob

def fix_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    if "def _base_frame(" not in content:
        wrapper = """
def _base_frame(arr, **kwargs):
    kwargs.setdefault('explanation', '')
    kwargs.setdefault('operation', '')
    return base_frame(arr, **kwargs)
"""
        content = content.replace("class ", wrapper + "\nclass ", 1)
        content = content.replace("yield base_frame(", "yield _base_frame(")
        
        with open(filepath, "w") as f:
            f.write(content)

for cat in ['simple', 'efficient', 'adaptive', 'hybrid']:
    for f in glob.glob(f"sortui/algorithms/{cat}/*.py"):
        if f.endswith("__init__.py"): continue
        fix_file(f)

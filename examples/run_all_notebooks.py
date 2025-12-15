import os
import sys
import subprocess
import glob
from pathlib import Path

def run_notebook(notebook_path):
    print(f"Testing {notebook_path}...")
    try:
        # Construct the command to execute the notebook
        # using sys.executable ensures we use the same python environment
        cmd = [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--stdout",
            "--ExecutePreprocessor.timeout=600",
            notebook_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(f"PASS: {notebook_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAIL: {notebook_path}")
        print("Error output (last 30 lines):")
        # Print last 30 lines of stderr
        lines = e.stderr.splitlines()
        for line in lines[-30:]:
            print(line)
        return False
    except Exception as e:
        print(f"ERROR: {notebook_path} - {str(e)}")
        return False

def main():
    base_dir = Path(__file__).parent.absolute() # examples/
    
    # Define notebooks files to test
    # We can walk the directory, or specify them. Walking is better for coverage.
    notebooks = []
    
    # Add notebooks in examples/
    notebooks.extend(base_dir.glob("*.ipynb"))
    
    # Add notebooks in examples/notebooks/
    notebooks.extend(base_dir.joinpath("notebooks").glob("*.ipynb"))
    
    # Filter out checkpoints
    notebooks = [n for n in notebooks if ".ipynb_checkpoints" not in str(n)]
    
    print(f"Found {len(notebooks)} notebooks to test.")
    
    failed_notebooks = []
    
    for nb in notebooks:
        if not run_notebook(str(nb)):
            failed_notebooks.append(str(nb))
            
    print("\n" + "="*40)
    print(f"Test Summary: {len(notebooks) - len(failed_notebooks)} passed, {len(failed_notebooks)} failed.")
    print("="*40)
    
    if failed_notebooks:
        print("\nFailed Notebooks:")
        for nb in failed_notebooks:
            print(f"- {nb}")
        sys.exit(1)
    else:
        print("\nAll notebooks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()

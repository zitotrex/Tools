import os
import sys
import subprocess

CODE_EXE = r"C:\Program Files\Microsoft VS Code\Code.exe"

if len(sys.argv) >= 3:
    local_file = os.path.abspath(sys.argv[1])
    remote_file = os.path.abspath(sys.argv[2])
    
    # Direct process call bypasses cmd.exe, batch files, and MSYS path conversion
    subprocess.run([CODE_EXE, "--wait", "--diff", local_file, remote_file], check=True)
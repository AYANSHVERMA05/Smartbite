"""
SmartBite - Smart Food Ordering and Management System
B.Tech Academic Project Entry Point
"""
import os
import sys
import subprocess

if __name__ == '__main__':
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    print("==================================================================")
    print("🚀 Launching SmartBite — Smart Food Ordering & Management System")
    print("==================================================================")
    print("🌐 Opening local server at: http://127.0.0.1:8000/\n")
    subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])


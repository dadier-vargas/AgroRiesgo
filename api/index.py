import os
import sys

# Agregar la raíz del proyecto a sys.path para que pueda importar app.py
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel Serverless Function entrypoint
if __name__ == '__main__':
    app.run()

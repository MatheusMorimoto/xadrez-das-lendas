import sys
import os
from cx_Freeze import setup, Executable

# Define os arquivos extras (imagens e vídeos)
build_exe_options = {
    "packages": ["pygame", "cv2", "os"],
    "includes": ["piece"],
    "path": [os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")] + sys.path,
    "include_files": ["assets/"],
}

# Configura para não abrir o console no Windows
base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="Xadrez_das_Lendas",
    version="1.0",
    description="Um jogo de quebra-cabeças de xadrez progressivo",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            os.path.join("main.py", "main.py"), 
            base=base, 
            target_name="Xadrez_das_Lendas.exe"
        )
    ],
)
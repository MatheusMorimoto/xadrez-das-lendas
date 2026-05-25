import sys
import os
from cx_Freeze import setup, Executable

# Define os arquivos extras (imagens e vídeos)
build_exe_options = {
    "packages": ["pygame", "cv2", "os"],
    "includes": ["piece"],
    "include_files": [(os.path.join("..", "assets"), "assets")],
}

# Configura para não abrir o console no Windows
base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="Xadrez_das_Lendas",
    version="1.0",
    description="Um jogo de quebra-cabeças de xadrez progressivo",
    options={"build_exe": {**build_exe_options, "path": [os.path.abspath(os.path.dirname(__file__))] + sys.path}},
    executables=[
        Executable(
            "main.py", 
            base=base, 
            target_name="Xadrez_das_Lendas.exe"
        )
    ],
)
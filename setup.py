import subprocess
import pathlib

subprocess.run("unzip stockfish-bin.zip", shell = True, cwd = pathlib.Path(__file__).resolve().parent)
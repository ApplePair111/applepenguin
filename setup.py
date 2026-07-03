import subprocess
import pathlib

subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part000", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part001", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part002", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part003", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part004", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part005", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.part006", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/Stockfish-sf_18.zip.sha256", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("wget https://github.com/ApplePair111/applepenguin/raw/refs/heads/stockfish-bin/filesplitter.py", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)


with open("executable", "w") as f:
    f.write(f"""#!/usr/bin/env bash

exec python {pathlib.Path(__file__).resolve().parent / "main.py"}""")

subprocess.run("chmod +x executable", shell = True, cwd = pathlib.Path(__file__).resolve().parent)

subprocess.run("python filesplitter.py join Stockfish-sf_18.zip.part000", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)
subprocess.run("mv Stockfish-sf_18.zip ../Stockfish-bin.zip", cwd = pathlib.Path(__file__).resolve().parent / "stockfishparts", shell = True)

subprocess.run("unzip Stockfish-bin.zip", shell = True, cwd = pathlib.Path(__file__).resolve().parent)


subprocess.run("mv Stockfish-sf_18 stockfish-bin.zip", shell = True, cwd = pathlib.Path(__file__).resolve().parent)

subprocess.run("pip install python-chess")

print("Done!")
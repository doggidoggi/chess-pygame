# chess_ai.spec
from PyInstaller.utils.hooks import collect_all

torch_datas, torch_binaries, torch_hiddenimports = collect_all("torch")

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=torch_binaries,
    datas=[
        ("assets", "assets"),
        ("models", "models"),
        *torch_datas,
    ],
    hiddenimports=torch_hiddenimports,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ChessAI",
    console=False,
    icon="assets/images/icon.png",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="ChessAI",
)
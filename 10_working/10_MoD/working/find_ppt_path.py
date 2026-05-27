from pathlib import Path
base = Path(r"c:\Users\kimiito\OneDrive - Cisco\Documents\700 - github\kimiito_Note\10_working\10_MoD\04_CSA")
for p in base.glob("*.pptx"):
    print(repr(str(p)))
    print(p.exists())

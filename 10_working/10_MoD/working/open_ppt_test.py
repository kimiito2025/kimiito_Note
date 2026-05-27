from pptx import Presentation
paths = [
 r"c:\Users\kimiito\OneDrive - Cisco\Documents\700 - github\kimiito_Note\10_working\10_MoD\04_CSA\cisco2025_template.pptx",
 r"c:\Users\kimiito\OneDrive - Cisco\Documents\700 - github\kimiito_Note\10_working\10_MoD\04_CSA\CSA_基礎知識.pptx",
]
for p in paths:
    try:
        prs = Presentation(p)
        print('ok', p, len(prs.slides))
    except Exception as e:
        print('ng', p, type(e).__name__, e)

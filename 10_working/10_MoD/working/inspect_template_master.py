from pptx import Presentation
p = Presentation(r"c:\Users\kimiito\OneDrive - Cisco\Documents\700 - github\kimiito_Note\10_working\10_MoD\04_CSA\cisco2025_template.pptx")
print('slide masters:', len(p.slide_masters))
for mi, m in enumerate(p.slide_masters):
    print(f"MASTER {mi}: name={m.name}")
    print('  layouts:', len(m.slide_layouts))
    for li, l in enumerate(m.slide_layouts):
        print(f"    {li}: {l.name}")

# theme/name hints from package parts are not exposed directly; print core props
cp = p.core_properties
print('title:', cp.title)
print('subject:', cp.subject)
print('keywords:', cp.keywords)
print('category:', cp.category)

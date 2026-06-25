"""Remove inline transform from model overlay JS — translateX(-50%) now in CSS."""
path = r'I:\BAK ABO\04_TEMA_SHOPIFY\assets\bks-piano-hero.js'
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()
src = src.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

old = "        modelEl.style.transform = 'translateX(-50%) translateY(18px) scale(0.88)';\n"
new = ""

assert old in src, "inline transform not found"
src = src.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

print("Inline transform removed — translateX(-50%) now in CSS.")

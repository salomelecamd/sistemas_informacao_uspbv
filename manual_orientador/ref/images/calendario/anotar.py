# Gera as imagens anotadas do manual (Calendário Partilhado) a partir das capturas em raw/.
# Cada anotação: retângulo com número; opcionalmente áreas a tapar (dados de teste).
# Uso: python anotar.py   (corre a partir desta pasta)
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
COR = (232, 89, 12)          # laranja: contrasta com o azul e o verde da app
FONTE = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
ESCALA = 2                   # desenha em 2x para traços mais suaves

# nome: (corte (x0,y0,x1,y1) ou None, [(n, caixa), ...], [caixas a tapar com branco])
APP = (141, 48, 1139, 609)
APP2 = (132, 39, 1436, 772)
IMAGENS = {
    # v0.12.0 (capturas a 1568x772): ecrã inicial e formulários
    "01_inicio": (APP2, [(1, (266, 249, 743, 402)), (2, (825, 249, 1302, 402)), (3, (265, 487, 1303, 584)),
                         (4, (265, 632, 775, 700)), (5, (793, 632, 1303, 700)), (6, (140, 748, 272, 769))], []),
    "02_planear_vazio": (APP2, [(1, (158, 160, 756, 202)), (2, (158, 254, 756, 296)), (3, (809, 160, 1407, 202)),
                                (4, (809, 210, 1421, 296)), (5, (809, 441, 1407, 483)), (6, (525, 708, 1067, 742)),
                                (7, (1203, 695, 1400, 753))], []),
    "02b_duracao_outra": (APP2, [(1, (809, 252, 1020, 296)), (2, (1338, 252, 1408, 296)), (3, (1278, 211, 1421, 235))], []),
    "02c_calendario": (APP2, [(1, (811, 200, 1234, 432)), (2, (809, 160, 1105, 202))], []),
    "03_planear_tipo": (APP2, [(1, (158, 160, 756, 202)), (2, (158, 296, 756, 676))], []),
    "04_registar": (APP2, [(1, (172, 58, 480, 104)), (2, (809, 160, 1407, 202)), (3, (525, 708, 1067, 742))], []),
    "06_meus_mes": (APP, [(1, (168, 108, 441, 150)), (2, (170, 157, 382, 497)), (3, (1007, 265, 1101, 285)),
                          (4, (666, 68, 942, 92)), (5, (170, 499, 382, 594))], []),
    "07_detalhe_porfechar": (APP, [(1, (403, 403, 519, 449)), (2, (520, 403, 636, 449)), (3, (637, 403, 753, 449)),
                                   (4, (754, 403, 876, 449))], [(409, 280, 720, 297)]),
    "08_detalhe_realizada": (APP, [(1, (407, 184, 680, 204)), (2, (754, 403, 876, 449))], [(409, 280, 720, 297)]),
    "10_vg_mes": (APP, [(1, (168, 102, 445, 142)), (2, (168, 145, 745, 204)), (3, (752, 155, 1112, 191)),
                        (4, (172, 431, 304, 450))], []),
    "11_vg_lista": (APP, [(1, (1010, 223, 1100, 520)), (2, (268, 431, 438, 452))], []),
    "12_vg_numeros": (APP, [(1, (168, 210, 1112, 295)), (2, (168, 303, 1112, 412))], []),
    "13_biblioteca": ((74, 56, 1568, 420), [(1, (1383, 146, 1529, 183)), (2, (368, 303, 905, 390))], []),
    "14_modelo": ((0, 170, 1568, 730), [(1, (36, 225, 1560, 246)), (2, (88, 698, 347, 722))], []),
    "15_email_aprov": ((684, 125, 1268, 600), [(1, (746, 130, 867, 158)), (2, (766, 343, 1203, 422)),
                                               (3, (766, 433, 1203, 500))], []),
    "16_pbi": ((68, 0, 1280, 590), [(1, (305, 8, 522, 40)), (2, (70, 178, 250, 336)), (3, (343, 123, 1162, 178))], []),
}


def anotar(nome, corte, marcas, tapar):
    img = Image.open(os.path.join(AQUI, "raw", nome + ".jpg")).convert("RGB")
    d = ImageDraw.Draw(img)
    for caixa in tapar:
        d.rectangle(caixa, fill="white")
    if corte:
        img = img.crop(corte)
        dx, dy = corte[0], corte[1]
    else:
        dx = dy = 0
    big = img.resize((img.width * ESCALA, img.height * ESCALA), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    for n, (x0, y0, x1, y1) in marcas:
        x0, y0, x1, y1 = [(v - o) * ESCALA for v, o in ((x0, dx), (y0, dy), (x1, dx), (y1, dy))]
        d.rounded_rectangle((x0, y0, x1, y1), radius=8, outline=COR, width=5)
        r = 17 * ESCALA // 2 + 4
        cx, cy = max(x0, r + 2), max(y0, r + 2)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=COR, outline="white", width=3)
        f = FONTE.font_variant(size=20 * ESCALA // 2 + 6)
        d.text((cx, cy), str(n), font=f, fill="white", anchor="mm")
    out = big.resize((img.width * 3 // 2, img.height * 3 // 2), Image.LANCZOS)
    out.save(os.path.join(AQUI, nome + ".jpg"), quality=88, optimize=True)


for nome, (corte, marcas, tapar) in IMAGENS.items():
    anotar(nome, corte, marcas, tapar)
    print(nome)

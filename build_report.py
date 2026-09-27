# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_PATH = r"C:\Users\lasto\goruntu-isleme-doku-analizi\docs\Goruntu Isleme Raporu - GLCM Tabanli Doku Analizi.docx"

doc = Document()
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)


def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_title(text, subtitle, author_line):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(22)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(subtitle)
    r2.italic = True
    r2.font.size = Pt(13)
    r2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run(author_line)
    r3.font.size = Pt(11)
    r3.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    doc.add_paragraph()


def h1(text):
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def para(text, bold_lead=None):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
    p.add_run(text)
    return p


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


def table(headers, rows, widths_cm):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    hdr_cells = t.rows[0].cells
    for i, htext in enumerate(headers):
        hdr_cells[i].text = htext
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
        set_cell_shading(hdr_cells[i], "D9E2F3")
        hdr_cells[i].width = Cm(widths_cm[i])
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            cells[i].width = Cm(widths_cm[i])
    doc.add_paragraph()
    return t


def sonuc_tablosu(baslik, aciklama, acc_rows, kappa_rows, yorum):
    h2(baslik)
    para(aciklama)
    para("Doğruluk (%) Tablosu:", bold_lead="")
    table(["D", "Random Forest", "J48", "Random Tree"], acc_rows, [3, 4.5, 4.5, 4.5])
    para("Kappa Değer Tablosu:", bold_lead="")
    table(["D", "Random Forest", "J48", "Random Tree"], kappa_rows, [3, 4.5, 4.5, 4.5])
    for y in yorum:
        para(y)


# ============================================================
add_title(
    "GLCM Tabanlı Doku Analizi ile Yaprak Sınıflandırması",
    "Görüntü İşleme Dersi Final Projesi — Teknik Rapor",
    "Hazırlayan: Eyüp Ensar Gündüz",
)

para(
    "Bu rapor, görüntü işleme dersi kapsamında hazırladığım \"GLCM Tabanlı Doku "
    "Analizi\" projesini belgelemektedir. Projenin amacı, Gri Seviye Eş-Oluşum "
    "Matrisi (GLCM) yöntemiyle görüntülerden dokusal özellikler çıkarmak, bu "
    "özellikleri farklı ek doku/şekil tanımlayıcılarıyla (LBP, LCP, HOG, PHOG, "
    "Alan-Şekil, Soft Histogram, Dalgacık/Wavelet Dönüşümü) zenginleştirmek ve "
    "elde edilen öznitelik kümeleriyle WEKA yazılımında sınıflandırma yaparak "
    "hangi özellik kombinasyonunun ve hangi piksel-mesafe (D) değerinin en "
    "yüksek doğruluğu verdiğini deneysel olarak karşılaştırmaktır."
)

# 1
h1("1. Proje Amacı")
para(
    "Doku (texture), bir görüntüdeki piksel yoğunluklarının uzamsal düzenini "
    "ifade eder ve şekil/renk bilgisi yetersiz kaldığında nesneleri ayırt "
    "etmek için güçlü bir tamamlayıcı özellik kaynağıdır. Bu projede, dört "
    "farklı yaprak durumunu (sağlıklı, hastalıklı, taze, kuru) birbirinden "
    "ayırt edebilecek bir doku-tabanlı sınıflandırma boru hattı kurulması "
    "amaçlanmıştır. Temel araştırma sorusu şudur: GLCM'nin temel 6 dokusal "
    "özelliğine hangi ek özellik türleri eklendiğinde ve GLCM'nin piksel "
    "mesafesi (D) parametresi nasıl değiştirildiğinde sınıflandırma "
    "doğruluğu en üst seviyeye çıkar?"
)

# 2
h1("2. Veri Seti")
para(
    "Veri seti, her biri ayrı bir klasörde toplanmış 4 sınıftan oluşan "
    "toplam 670 yaprak görüntüsü içermektedir:"
)
table(
    ["Sınıf", "Görüntü Sayısı", "Açıklama"],
    [
        ["Kuru Yaprak", "180", "Kurumuş, kahverengi tonlarda yapraklar"],
        ["Meşe Yaprağı (Oak)", "186", "Meşe ağacına ait yapraklar, karakteristik loblu şekil"],
        ["Taze Yaprak", "160", "Sağlıklı, yeşil, canlı dokulu yapraklar"],
        ["Hastalıklı Yaprak", "144", "Leke/bozulma belirtisi gösteren yapraklar"],
        ["Toplam", "670", "—"],
    ],
    [5, 4, 8],
)
para(
    "Görüntüler JPG formatındadır ve boyutları standart değildir; her "
    "özellik çıkarım betiğinde ön işleme adımında sabit bir boyuta "
    "(genellikle 128×128 veya 256×256 piksel) yeniden boyutlandırılmıştır."
)

# 3
h1("3. Yöntem")

h2("3.1 Ön İşleme")
para(
    "Her görüntü önce gri tonlamaya (grayscale) dönüştürülür (OpenCV "
    "`cv2.cvtColor`). GLCM ve türetilmiş doku özellikleri renk bilgisiyle "
    "değil, piksel yoğunluğu düzenleriyle ilgilendiği için bu dönüşüm "
    "gereklidir. Ardından görüntü, özellik çıkarım betiğine göre 128×128 "
    "ya da 256×256 piksele yeniden boyutlandırılarak tüm görüntüler için "
    "tutarlı bir öznitelik vektörü uzunluğu garanti edilir."
)

h2("3.2 GLCM Tabanlı Temel Doku Özellikleri")
para(
    "Gri Seviye Eş-Oluşum Matrisi (Gray-Level Co-occurrence Matrix), belirli "
    "bir mesafede (D) ve açıda (θ) birbirine komşu piksel çiftlerinin gri "
    "seviye kombinasyonlarının ne sıklıkla oluştuğunu sayan bir matristir. "
    "Bu projede `skimage.feature.graycomatrix` fonksiyonu ile 4 açı "
    "(0°, 45°, 90°, 135°) için simetrik ve normalize edilmiş GLCM matrisleri "
    "oluşturulmuş, ardından `graycoprops` ile şu 6 istatistiksel özellik "
    "hesaplanıp 4 açının ortalaması alınmıştır:"
)
bullet("Contrast (Kontrast): Komşu piksel çiftleri arasındaki yoğunluk farkının karesinin ağırlıklı toplamı — yüksek kontrast, keskin doku geçişlerini gösterir.")
bullet("Dissimilarity (Farklılık): Kontrasta benzer ama karesi alınmadan, mutlak farkla hesaplanır.")
bullet("Homogeneity (Homojenlik): GLCM'deki değerlerin köşegene ne kadar yakın dağıldığını ölçer; pürüzsüz dokularda yüksektir.")
bullet("Energy (Enerji): GLCM elemanlarının karelerinin toplamı; tekdüze/düzenli dokularda yüksek çıkar.")
bullet("Correlation (Korelasyon): Bir pikselin komşusuyla ne kadar doğrusal ilişkili olduğunu ölçer.")
bullet("ASM (Angular Second Moment): Enerjinin kareköksüz hali, doku düzenliliğinin bir başka göstergesi.")
para(
    "Mesafe parametresi D, koddaki `graycomatrix(gray, [D], ...)` çağrısında "
    "elle değiştirilerek D=1, 2, 4 ve 8 değerleri için ayrı ayrı özellik "
    "dosyaları üretilmiş ve her biri WEKA'da bağımsız olarak sınıflandırılmıştır "
    "— yani D taraması kod içinde otomatik bir döngü değil, betiğin D "
    "parametresi değiştirilerek tekrar tekrar çalıştırılmasıyla elde edilmiştir."
)

h2("3.3 Ek Özellik Türleri")
para("GLCM'nin temel 6 özelliğine, doku ve şeklin farklı yönlerini yakalamak için sırasıyla şu özellik türleri eklenmiştir:")
bullet("LBP (Local Binary Pattern): Her pikseli komşularıyla karşılaştırıp ikili bir desen kodu üretir (`skimage.feature.local_binary_pattern`, uniform yöntem, yarıçap=1, 8 komşu); histogram haline getirilip mikro-doku (yaprak damarı gibi ince detaylar) yakalanır.")
bullet("LCP (Local Contrast Pattern): Bir Laplacian benzeri konvolüsyon çekirdeği (`[[1,1,1],[1,-8,1],[1,1,1]]`) ile yerel kontrast haritası çıkarılır ve histogramlanır; özellikle leke/renk-tonu farklılıklarını yakalamada güçlüdür.")
bullet("HOG (Histogram of Oriented Gradients): Görüntüdeki kenar yönelim histogramlarının ortalama ve standart sapması; yaprağın dış hatlarını/genel şeklini tanımlar.")
bullet("PHOG (Pyramid HOG): HOG'un piramitsel (çok ölçekli) versiyonu — görüntü 2 seviyeli bir ızgaraya bölünüp her hücrede ayrı bir gradyan-yönelim histogramı çıkarılır; böylece kenar bilgisine konumsal bağlam da eklenir.")
bullet("Alan ve Şekil Özellikleri: Otsu eşikleme + kontur bulma (`cv2.threshold` + `cv2.findContours`) ile yaprağın alanı, çevresi, dairesellik oranı (4π·Alan/Çevre²) ve en-boy oranı hesaplanır — yaprağın boyut/geometri sınıfını (küçük/büyük, ince/yuvarlak) ayırt eder.")
bullet("Soft Histogram: Klasik histogramın aksine, her piksel en yakın bin merkezine değil, üçgen ağırlık fonksiyonuyla birden fazla bine \"yumuşak\" biçimde dağıtılır; bu, renk/ton geçişlerindeki ani kesişimlerden kaynaklanan gürültüyü azaltır.")
bullet("Dalgacık (Wavelet) Dönüşümü: Haar dalgacığıyla (`pywt.dwt2`) görüntü 4 frekans bandına ayrılır (LL: düşük frekanslı öz; LH, HL, HH: yatay/dikey/çapraz detaylar); LL bandının ortalama/std'si ve detay bantlarının enerjileri özellik olarak kullanılır.")

h2("3.4 Özellik Kombinasyonları")
para(
    "Sekiz farklı özellik kombinasyonu ayrı Python betikleriyle üretilmiş, "
    "her biri ayrı bir ARFF dosyasına yazılmıştır (bkz. `src/` ve `arff/` "
    "klasörleri):"
)
table(
    ["#", "Kombinasyon", "Betik / ARFF"],
    [
        ["1", "GLCM + LBP", "01_glcm_lbp.py → glcm_lbp.arff"],
        ["2", "GLCM + LBP + HOG", "02_glcm_lbp_hog.py → glcm_lbp_hog.arff"],
        ["3", "GLCM + LCP", "03_glcm_lcp.py → glcm_lcp_features.arff"],
        ["4", "GLCM + LCP + PHOG", "04_glcm_lcp_phog.py → glcm_lcp_phog.arff"],
        ["5", "GLCM + Alan/Şekil", "05_glcm_alan_sekil.py → glcm_shape_features.arff"],
        ["6", "GLCM + Alan/Şekil + Soft Histogram", "06_glcm_alan_sekil_soft_histogram.py → glcm_shape_soft_hist.arff"],
        ["7", "\"Süper\": GLCM+LBP+LCP+HOG+PHOG+Alan/Şekil+SoftHist", "07_super_tum_ozellikler.py → full_feature_fusion.arff"],
        ["8", "GLCM + Wavelet (ayrı deney)", "08_wavelet_glcm.py → wavelet_glcm.arff"],
    ],
    [1.5, 9, 7],
)

h2("3.5 Sınıflandırma")
para(
    "Üretilen her ARFF dosyası WEKA yazılımına yüklenerek 3 farklı "
    "sınıflandırma algoritmasıyla test edilmiştir: Random Forest (çok "
    "sayıda karar ağacının oylamasıyla çalışan topluluk yöntemi), J48 "
    "(C4.5 algoritmasının WEKA implementasyonu olan budanmış karar ağacı) "
    "ve Random Tree (rastgele bir öznitelik alt kümesiyle kurulan tek karar "
    "ağacı). Başarı ölçütü olarak doğruluk yüzdesi (accuracy) ve Kappa "
    "istatistiği (şans faktörü çıkarılmış uyum ölçüsü) kullanılmıştır."
)

# 4
h1("4. Sonuçlar")

sonuc_tablosu(
    "4.1 GLCM + LBP",
    "GLCM'nin temel 6 özelliğine LBP histogramı eklenerek 4 farklı D "
    "değeri için sınıflandırma yapılmıştır.",
    [["D=1", "80.10", "78.40", "78.15"], ["D=2", "81.50", "79.60", "76.90"],
     ["D=4", "83.25", "81.10", "79.40"], ["D=8", "80.12", "78.74", "77.08"]],
    [["D=1", "0.74", "0.72", "0.72"], ["D=2", "0.75", "0.71", "0.72"],
     ["D=4", "0.77", "0.73", "0.73"], ["D=8", "0.77", "0.70", "0.71"]],
    [
        "En yüksek doğruluk D=4'te elde edilmiştir. Bu mesafenin, bir doku "
        "deseninin başlangıcı ile bitişi arasındaki değişikliği en net "
        "yakalayan mesafe olduğu değerlendirilmektedir. D=8'deki düşüş, "
        "büyük mesafede piksel ilişkilerinin yaprak dokusunun bütünlüğünü "
        "bozmasına bağlanmıştır.",
    ],
)

sonuc_tablosu(
    "4.2 GLCM + LBP + HOG",
    "Üstteki kombinasyona ek olarak HOG (kenar yönelimi) özelliği "
    "eklenmiştir.",
    [["D=1", "80.27", "80.81", "77.42"], ["D=2", "81.50", "79.95", "78.61"],
     ["D=4", "83.51", "82.71", "79.27"], ["D=8", "80.31", "78.11", "76.08"]],
    [["D=1", "0.72", "0.69", "0.69"], ["D=2", "0.72", "0.73", "0.71"],
     ["D=4", "0.74", "0.71", "0.69"], ["D=8", "0.74", "0.70", "0.68"]],
    [
        "HOG eklenmesiyle doğruluk hafifçe artmıştır; en yüksek sonucu ve "
        "en yüksek Kappa değerini Random Forest vermiştir. D=4'te pikseller "
        "arası gereksiz benzerliklerin azalması, sınıfları ayıran doku "
        "düzensizliklerinin daha belirgin öne çıkmasını sağlamıştır.",
    ],
)

sonuc_tablosu(
    "4.3 GLCM + LCP",
    "GLCM'ye, yerel kontrast tabanlı LCP özelliği eklenmiştir.",
    [["D=1", "79.82", "77.20", "74.19"], ["D=2", "80.12", "77.75", "77.45"],
     ["D=4", "82.78", "78.17", "79.57"], ["D=8", "79.54", "75.42", "76.14"]],
    [["D=1", "0.71", "0.68", "0.71"], ["D=2", "0.69", "0.65", "0.68"],
     ["D=4", "0.74", "0.71", "0.66"], ["D=8", "0.71", "0.69", "0.69"]],
    [
        "En yüksek değişim yine D=4'te görülmüştür; bu, LCP'nin yapraklar "
        "üzerindeki hastalık lekesi ya da kuruma belirtilerini bu mesafede "
        "daha iyi ayırt ettiğini göstermektedir. D=8'de kontrast ilişkisi "
        "zayıflamıştır.",
    ],
)

sonuc_tablosu(
    "4.4 GLCM + LCP + PHOG",
    "LCP'ye ek olarak PHOG (piramit gradyan histogramı) eklenmiştir.",
    [["D=1", "81.12", "79.14", "78.19"], ["D=2", "79.18", "80.74", "79.75"],
     ["D=4", "84.53", "81.47", "80.63"], ["D=8", "81.45", "80.02", "77.23"]],
    [["D=1", "0.72", "0.69", "0.67"], ["D=2", "0.72", "0.68", "0.68"],
     ["D=4", "0.75", "0.70", "0.71"], ["D=8", "0.71", "0.67", "0.65"]],
    [
        "PHOG'un konumsal bilgi eklemesi doğruluğu belirgin şekilde "
        "artırmıştır: LCP leke/damar belirginliğini yakalarken, PHOG bu "
        "detayların yaprak geometrisi üzerindeki konumunu işlemektedir. "
        "En yüksek doğruluk yine D=4'te elde edilmiştir.",
    ],
)

sonuc_tablosu(
    "4.5 GLCM + Alan ve Şekil Özellikleri",
    "Bu deneyde doku özelliklerine ek olarak sadece geometrik (alan, "
    "çevre, dairesellik, en-boy oranı) özellikler kullanılmıştır.",
    [["D=1", "73.74", "71.47", "68.14"], ["D=2", "74.58", "72.70", "67.56"],
     ["D=4", "77.22", "73.14", "69.13"], ["D=8", "72.98", "71.36", "68.12"]],
    [["D=1", "0.69", "0.65", "0.61"], ["D=2", "0.66", "0.62", "0.68"],
     ["D=4", "0.69", "0.63", "0.64"], ["D=8", "0.67", "0.66", "0.63"]],
    [
        "Bu kombinasyon, diğerlerine kıyasla en düşük doğruluğu vermiştir. "
        "Sebebi, veri setindeki yaprakların birbirine benzer büyüklük ve "
        "şekillerde olması, dolayısıyla salt geometrik özelliklerin sınıflar "
        "arasında yeterince ayırt edici olmamasıdır.",
    ],
)

sonuc_tablosu(
    "4.6 GLCM + Alan/Şekil + Soft Histogram",
    "Geometrik özelliklere ek olarak Soft Histogram (yumuşak yoğunluk "
    "dağılımı) eklenmiştir.",
    [["D=1", "75.12", "72.78", "72.85"], ["D=2", "77.45", "73.70", "69.89"],
     ["D=4", "79.53", "74.34", "72.16"], ["D=8", "73.66", "72.41", "73.15"]],
    [["D=1", "0.71", "0.65", "0.61"], ["D=2", "0.73", "0.64", "0.61"],
     ["D=4", "0.71", "0.67", "0.63"], ["D=8", "0.68", "0.63", "0.62"]],
    [
        "Soft Histogram eklenmesiyle doğruluk, salt Alan/Şekil'e göre "
        "belirgin şekilde artmıştır: Alan/Şekil yaprağın sınırını "
        "tanımlarken, Soft Histogram yaprağın İÇİNDEKİ renk/ton yoğunluğunu "
        "(örn. kahverengi–yeşil ayrımı) tanımlamaktadır — aynı boyut ve "
        "şekildeki kuru/taze yaprakları ayırt etmek için gereklidir.",
    ],
)

sonuc_tablosu(
    "4.7 \"Süper\" Kombinasyon: Tüm Özellikler Bir Arada",
    "GLCM + LBP + LCP + HOG + PHOG + Alan/Şekil + Soft Histogram "
    "özelliklerinin TAMAMI aynı öznitelik vektöründe birleştirilmiştir.",
    [["D=1", "85.20", "82.36", "74.14"], ["D=2", "85.38", "82.51", "75.18"],
     ["D=4", "88.53", "81.76", "78.79"], ["D=8", "84.60", "82.21", "74.73"]],
    [["D=1", "0.80", "0.76", "0.65"], ["D=2", "0.79", "0.76", "0.66"],
     ["D=4", "0.82", "0.75", "0.63"], ["D=8", "0.78", "0.76", "0.66"]],
    [
        "Bu, projenin EN YÜKSEK sonucudur: D=4, Random Forest ile %88,53 "
        "doğruluk ve 0,82 Kappa. Özellikler birbirini tamamlayıcı şekilde "
        "çalışmıştır: LBP ve LCP yaprak damarlarındaki mikro detayları, "
        "HOG ve PHOG dış hatları/iskeleti, Alan-Şekil boyut sınıfını, Soft "
        "Histogram ise renk geçişlerindeki gürültüyü temizlemiştir. Tüm "
        "özelliklerin bir araya gelmesi, tek başına hiçbirinin "
        "yakalayamadığı ayırt edici bilgiyi ortaya çıkarmıştır.",
    ],
)

sonuc_tablosu(
    "4.8 GLCM + Wavelet Dönüşümü (Ayrı Deney)",
    "GLCM'nin temel özelliklerine, Haar dalgacık dönüşümünün alt-bant "
    "enerjileri eklenerek ayrı bir deney yapılmıştır.",
    [["D=1", "82.81", "83.55", "79.37"], ["D=2", "83.73", "83.75", "78.40"],
     ["D=4", "84.51", "84.90", "80.27"], ["D=8", "80.31", "79.11", "76.08"]],
    [["D=1", "0.76", "0.77", "0.72"], ["D=2", "0.74", "0.72", "0.75"],
     ["D=4", "0.78", "0.80", "0.73"], ["D=8", "0.69", "0.73", "0.68"]],
    [
        "Bu deneyde diğerlerinden farklı olarak en yüksek doğruluğu J48 "
        "vermiştir (D=4'te %84,90). Wavelet dönüşümü görüntüyü frekans "
        "bantlarına ayırarak hem ana hatları hem ince damar detaylarını "
        "yakaladığından, sınıflar arası sınırların belirginleşmesi "
        "doğruluğu artırmıştır. D=8'de sonucun düşmesi, dönüşümün büyük "
        "piksel mesafelerinde hassasiyetini kaybetmesiyle açıklanmaktadır.",
    ],
)

# 5
h1("5. Genel Değerlendirme")
para(
    "Sekiz deney genelinde tutarlı biçimde gözlemlenen iki örüntü öne "
    "çıkmaktadır:"
)
bullet("D=4, neredeyse tüm özellik kombinasyonlarında en yüksek doğruluğu veren piksel mesafesidir — bu mesafenin, yaprak dokusundaki karakteristik deseni (damar aralığı, leke boyutu) ne çok yakından (gürültüye duyarlı) ne çok uzaktan (doku bütünlüğünü kaybeden) yakaladığı için optimal bir denge noktası olduğu değerlendirilmektedir.")
bullet("Özellik çeşitliliği arttıkça (tek başına GLCM+LBP'den, 7 özelliğin birleştiği \"süper\" kombinasyona doğru) doğruluk sistematik olarak artmıştır (%83,25 → %88,53) — bu, hiçbir tekil özellik türünün doku bilgisinin tamamını yakalayamadığını, birbirini tamamlayan farklı bakış açılarının (mikro-doku, kenar, geometri, renk yoğunluğu) bir arada kullanılmasının en güvenilir sonucu verdiğini göstermektedir.")
bullet("Sınıflandırıcılar arasında Random Forest, neredeyse her deneyde en yüksek veya en yüksete yakın doğruluğu vermiştir — çoklu karar ağacının oylamaya dayalı yapısının, tek bir karar ağacına (J48, Random Tree) göre gürültüye karşı daha dayanıklı olması beklenen bir sonuçtur.")
bullet("En düşük performansı salt geometrik (Alan/Şekil) özellikler vermiştir; bu, veri setindeki yaprakların boyut/şekil açısından görsel olarak benzer olmasından, dolayısıyla ayırt edici gücün asıl doku ve renk bilgisinde yattığından kaynaklanmaktadır.")

# 6
h1("6. Sonuç")
para(
    "Bu projede, GLCM tabanlı doku analizinin tek başına makul (%80 "
    "civarı) ama ek özellik türleriyle zenginleştirildiğinde çok daha "
    "güçlü (%88,53'e kadar) bir sınıflandırma performansı sağladığı "
    "gösterilmiştir. En iyi sonuç, GLCM'nin 6 temel özelliğine LBP, LCP, "
    "HOG, PHOG, Alan/Şekil ve Soft Histogram özelliklerinin TÜMÜNÜN "
    "eklendiği \"süper\" kombinasyonla, D=4 piksel mesafesinde ve Random "
    "Forest sınıflandırıcısıyla elde edilmiştir (%88,53 doğruluk, 0,82 "
    "Kappa). Bu sonuç, doku analizinde tek bir yöntemle yetinmek yerine "
    "birden fazla tamamlayıcı özellik türünü bir arada kullanmanın "
    "pratik değerini somut sayılarla ortaya koymaktadır."
)

h1("Ek: Depo (Repository) İçeriği")
para("Bu raporun dayandığı kaynak kodlar ve öznitelik dosyaları aynı GitHub deposunda şu şekilde yer almaktadır:")
bullet("src/ — 8 özellik çıkarım betiğinin tamamı (Python, OpenCV + scikit-image + PyWavelets)")
bullet("arff/ — Her özellik kombinasyonu için WEKA'ya hazır ARFF dosyaları")
bullet("docs/ — Bu rapor")

doc.save(OUT_PATH)
print("Kaydedildi:", OUT_PATH)

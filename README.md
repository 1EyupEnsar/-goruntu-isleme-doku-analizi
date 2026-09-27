# GLCM Tabanlı Doku Analizi ile Yaprak Sınıflandırması

Görüntü işleme dersi kapsamında hazırlanan bir final projesi. Amaç, GLCM
(Gri Seviye Eş-Oluşum Matrisi) yöntemiyle çıkarılan dokusal özelliklerin,
farklı ek özellik türleriyle (LBP, LCP, HOG, PHOG, Alan/Şekil, Soft
Histogram, Wavelet) zenginleştirildiğinde 4 sınıflı bir yaprak veri
setinde (Kuru / Meşe / Taze / Hastalıklı, toplam 670 görüntü) ne kadar
yüksek bir sınıflandırma doğruluğu sağlayabileceğini deneysel olarak
karşılaştırmaktır.

Tüm deney ve sonuçların ayrıntılı açıklaması için:
**[`docs/Goruntu Isleme Raporu - GLCM Tabanli Doku Analizi.docx`](docs/Goruntu%20Isleme%20Raporu%20-%20GLCM%20Tabanli%20Doku%20Analizi.docx)**

## Öne çıkan sonuç

Tüm özellik türlerinin (GLCM + LBP + LCP + HOG + PHOG + Alan/Şekil + Soft
Histogram) birleştirildiği "süper" kombinasyon, D=4 piksel mesafesinde ve
Random Forest sınıflandırıcısıyla **%88,53 doğruluk, 0,82 Kappa** ile en
iyi sonucu vermiştir.

## Depo Yapısı

```
├── src/     8 özellik çıkarım betiği (Python: OpenCV, scikit-image, PyWavelets)
├── arff/    Her özellik kombinasyonu için WEKA'ya hazır ARFF dosyaları
└── docs/    Teknik rapor (.docx)
```

## Yöntem Özeti

1. Görüntü gri tonlamaya çevrilir, sabit boyuta (128×128 / 256×256) getirilir.
2. GLCM ile 6 temel doku özelliği (Contrast, Dissimilarity, Homogeneity,
   Energy, Correlation, ASM) 4 açıda (0°/45°/90°/135°) hesaplanır.
3. Farklı piksel mesafeleri (D=1, 2, 4, 8) için ayrı ayrı denenir.
4. GLCM'ye sırasıyla LBP, LCP, HOG, PHOG, Alan/Şekil, Soft Histogram ve
   Wavelet özellikleri eklenerek 8 farklı öznitelik kombinasyonu üretilir.
5. Her kombinasyon WEKA'da Random Forest, J48 ve Random Tree ile
   sınıflandırılır; doğruluk (%) ve Kappa değerleri karşılaştırılır.

## Çalıştırma

```bash
pip install opencv-python scikit-image pandas numpy PyWavelets
python src/07_super_tum_ozellikler.py   # örn. en iyi sonucu veren betik
```

Betikler `dataset_path` değişkeninde tanımlı bir klasördeki alt klasörleri
(her biri bir sınıf) tarar ve bir `.arff` dosyası üretir; bu dosya WEKA'ya
doğrudan yüklenebilir (Explorer → Open file → Classify).

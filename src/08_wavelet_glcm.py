#Wavelet + GLCM Özellik Çıkarım Kodu
import os
import numpy as np
import cv2
import pandas as pd
import pywt  # Wavelet kütüphanesi
from skimage.feature import graycomatrix, graycoprops

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_wavelet_glcm_features(img):
    # --- 1. ÖN İŞLEME ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256)) # Standart boyut
    
    features = {}

    # --- 2. GLCM ÖZELLİKLERİ (Orijinal Görüntüden) ---
    glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value)

    # --- 3. WAVELET DÖNÜŞÜMÜ (Haar Wavelet) ---
    # Görüntüyü 4 frekans bandına ayırır: LL (Aproksimasyon), LH, HL, HH (Detaylar)
    coeffs2 = pywt.dwt2(gray, 'haar')
    LL, (LH, HL, HH) = coeffs2
    
    

    # Wavelet Tabanlı Özellikler:
    # LL bandı görüntünün düşük frekanslı özüdür
    features["wavelet_LL_mean"] = np.mean(LL)
    features["wavelet_LL_std"] = np.std(LL)
    
    # LH, HL ve HH bantları yatay, dikey ve çapraz detay enerjilerini verir
    # Yaprak damarlarının yoğunluğunu anlamak için bu enerjiler kritiktir
    features["wavelet_LH_energy"] = np.sum(np.square(LH))
    features["wavelet_HL_energy"] = np.sum(np.square(HL))
    features["wavelet_HH_energy"] = np.sum(np.square(HH))

    return features

# --- VERİ OKUMA VE ARFF OLUŞTURMA ---
data_list = []
for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path):
        continue
    
    print(f"İşleniyor: {class_name}")
    for filename in os.listdir(class_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            file_path = os.path.join(class_path, filename)
            img = cv2.imread(file_path)
            if img is None: continue
            
            # Özellikleri çıkar
            features = extract_wavelet_glcm_features(img)
            features["class"] = class_name
            data_list.append(features)

# DataFrame oluşturma
df = pd.DataFrame(data_list)

# ARFF DOSYASINI KAYDETME
arff_file = "wavelet_glcm.arff"
with open(arff_file, "w") as f:
    f.write(f"@RELATION wavelet_glcm_analysis\n\n")
    # Öznitelik isimlerini yaz (class hariç)
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    # Sınıf isimlerini yaz
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    
    # Verileri yaz
    f.write("@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"ARFF dosyası başarıyla oluşturuldu: {arff_file}")
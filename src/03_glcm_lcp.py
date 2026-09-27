import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_features(img):
    # 1. Ön İşleme: Gri Tonlama
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Boyut küçültme (hesaplama hızı ve standartlaştırma için)
    gray = cv2.resize(gray, (256, 256))
    
    features = {}
    
    # --- A. GLCM ÖZELLİKLERİ ---
    glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value)

    # --- B. LCP (Local Contrast Pattern) ÖZELLİKLERİ ---
    # LCP mantığı: Bir pikselin komşularıyla olan mutlak farklarının ortalaması
    # Bu yöntem yerel kontrast değişimlerini (kenar ve doku) yakalar.
    
    # 3x3'lük bir pencerede merkezi piksel ile komşular arasındaki farkı bulalım
    kernel = np.array([[1, 1, 1],
                       [1, -8, 1],
                       [1, 1, 1]], dtype=np.float32)
    
    lcp_map = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    lcp_map = np.abs(lcp_map) # Negatif farkları pozitife çevir (mutlak kontrast)
    
    # LCP sonuçlarını histograma dökerek öznitelik haline getiriyoruz
    (lcp_hist, _) = np.histogram(lcp_map.ravel(), bins=8, range=(0, 255))
    lcp_hist = lcp_hist.astype("float")
    lcp_hist /= (lcp_hist.sum() + 1e-7) # Normalizasyon
    
    for i, val in enumerate(lcp_hist):
        features[f"lcp_bin_{i}"] = val

    return features

# --- VERİ OKUMA VE İŞLEME ---
data_list = []
for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path):
        continue
    
    print(f"İşleniyor: {class_name}...")
    for filename in os.listdir(class_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            file_path = os.path.join(class_path, filename)
            img = cv2.imread(file_path)
            if img is None: continue
            
            # GLCM ve LCP birleştirilmiş özellikleri al
            feats = extract_features(img)
            feats["class"] = class_name
            data_list.append(feats)

# DataFrame oluşturma
df = pd.DataFrame(data_list)

# ARFF Dosyasını Kaydetme
arff_file = "glcm_lcp_features.arff"
with open(arff_file, "w") as f:
    f.write("@RELATION glcm_lcp_analysis\n\n")
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    
    f.write("@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"ARFF dosyası başarıyla oluşturuldu: {arff_file}")
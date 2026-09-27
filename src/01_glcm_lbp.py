import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_features(img):
    # 1. ÖN İŞLEME: Gri Tonlamaya Çeviriyoruz
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    features = {}
    
    # --- A. GLCM ÖZELLİKLERİ ---
    glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value) # 4 yönün ortalaması
        
    # --- B. LBP ÖZELLİKLERİ ---
    radius = 1
    n_points = 8 * radius
    # LBP hesaplanıyor (Dairesel ve uniform modda)
    lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
    # LBP sonuçlarını 10 binli bir histograma dönüştürüyoruz (özellik vektörü için)
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
    
    # Normalizasyon (Özelliklerin toplamı 1 olsun diye)
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)
    
    # Her bir histogram bin'ini bir özellik olarak ekliyoruz
    for i, val in enumerate(hist):
        features[f"lbp_bin_{i}"] = val
        
    return features

# GÖRÜNTÜLERİ OKUYORUZ
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
            if img is None:
                continue
            
            # Hem GLCM hem LBP özelliklerini içeren tek bir sözlük alıyoruz
            features = extract_features(img)
            features["class"] = class_name
            data_list.append(features)

# DataFrame oluşturuyoruz
df = pd.DataFrame(data_list)

# ARFF DOSYASINI KAYDEDİYORUZ
arff_file = "glcm_lbp4.arff"
with open(arff_file, "w") as f:
    f.write(f"@RELATION glcm_lbp_features\n\n")
    # Sayısal özellikler (LBP binleri ve GLCM değerleri)
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    # Sınıf etiketi
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    
    f.write("@DATA\n")
    for _, row in df.iterrows():
        # Verileri virgülle ayırıp yazdırıyoruz
        f.write(",".join(map(str, row.values)) + "\n")

print(f"ARFF dosyası başarıyla oluşturuldu: {arff_file}")
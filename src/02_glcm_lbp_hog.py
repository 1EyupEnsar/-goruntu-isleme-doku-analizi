#GLCM + LBP + HOG kodu
import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern, hog
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_features(img):
    # 1. ÖN İŞLEME: Gri Tonlamaya Çevirme ve Boyutlandırma
    # HOG için tüm görüntülerin aynı boyutta olması (standartlaştırma) önemlidir.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_resized = cv2.resize(gray, (128, 128)) 
    
    features = {}
    
    # --- A. GLCM ÖZELLİKLERİ ---
    glcm = graycomatrix(gray_resized, [8], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value)
        
    # --- B. LBP ÖZELLİKLERİ ---
    radius = 1
    n_points = 8 * radius
    lbp = local_binary_pattern(gray_resized, n_points, radius, method='uniform')
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)
    for i, val in enumerate(hist):
        features[f"lbp_bin_{i}"] = val
        
    # --- C. HOG ÖZELLİKLERİ ---
    # orientations: Yön sayısı, pixels_per_cell: Hücre boyutu
    hog_feats = hog(gray_resized, orientations=9, pixels_per_cell=(16, 16),
                    cells_per_block=(2, 2), visualize=False)
    
    # HOG çok fazla özellik (vektör) üretir. 
    # Bunları Weka'da anlamlı kılmak için özet istatistiklerini veya ilk N elemanını alabiliriz.
    # Burada ortalama, standart sapma ve maksimum değer gibi istatistikleri ekliyoruz:
    features["hog_mean"] = np.mean(hog_feats)
    features["hog_std"] = np.std(hog_feats)
    features["hog_skew"] = np.mean((hog_feats - np.mean(hog_feats))**3) # Eğrilik (opsiyonel)
    
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
            if img is None: continue
            
            features = extract_features(img)
            features["class"] = class_name
            data_list.append(features)

# DataFrame oluşturuyoruz
df = pd.DataFrame(data_list)

# ARFF DOSYASINI KAYDEDİYORUZ
arff_file = "glcm_lbp_hog8.arff"
with open(arff_file, "w") as f:
    f.write(f"@RELATION glcm_lbp_hog_features\n\n")
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    
    f.write("@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"ARFF dosyası başarıyla oluşturuldu: {arff_file}")
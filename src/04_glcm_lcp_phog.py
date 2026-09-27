#GLCM + LCP + PHOG
import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_phog(gray_img, bins=8, levels=2):
    """Görüntüden PHOG özelliklerini çıkarır."""
    # Gradyanları hesapla
    gx = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0, ksize=1)
    gy = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1, ksize=1)
    mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
    
    phog_vector = []
    
    # Her piramit seviyesi için histogram çıkar
    for level in range(levels + 1):
        num_cells = 2**level
        h, w = gray_img.shape
        cell_h, cell_w = h // num_cells, w // num_cells
        
        for i in range(num_cells):
            for j in range(num_cells):
                # Hücreyi kes
                angle_cell = angle[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                mag_cell = mag[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                
                # Açı histogramını oluştur (magnitüd ağırlıklı)
                hist, _ = np.histogram(angle_cell, bins=bins, range=(0, 360), weights=mag_cell)
                # Normalizasyon
                norm = np.linalg.norm(hist) + 1e-7
                phog_vector.extend(hist / norm)
                
    return phog_vector

def extract_features(img):
    # 1. Ön İşleme
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256)) # Standart boyut
    
    features = {}
    
    # --- A. GLCM ÖZELLİKLERİ ---
    glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value)

    # --- B. LCP (Local Contrast Pattern) ÖZELLİKLERİ ---
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)
    lcp_map = np.abs(cv2.filter2D(gray.astype(np.float32), -1, kernel))
    (lcp_hist, _) = np.histogram(lcp_map.ravel(), bins=8, range=(0, 255))
    lcp_hist = lcp_hist.astype("float") / (lcp_hist.sum() + 1e-7)
    for i, val in enumerate(lcp_hist):
        features[f"lcp_bin_{i}"] = val

    # --- C. PHOG ÖZELLİKLERİ ---
    # Piramit seviyesi 2 (1x1 + 2x2 + 4x4 = 21 hücre)
    # Her hücrede 8 yön bin'i = Toplam 168 özellik
    phog_feats = extract_phog(gray, bins=8, levels=2)
    # Weka'da çok fazla kolon oluşmaması için istatistiklerini alabilir veya hepsini ekleyebiliriz.
    # Burada direkt ekliyoruz (Proje isterine tam uyum için):
    for i, val in enumerate(phog_feats):
        features[f"phog_{i}"] = val

    return features

# --- VERİ OKUMA ---
data_list = []
for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path): continue
    
    print(f"İşleniyor: {class_name}...")
    for filename in os.listdir(class_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(os.path.join(class_path, filename))
            if img is None: continue
            
            feats = extract_features(img)
            feats["class"] = class_name
            data_list.append(feats)

# DataFrame ve ARFF Kaydı
df = pd.DataFrame(data_list)
arff_file = "glcm_lcp_phog.arff"

with open(arff_file, "w") as f:
    f.write(f"@RELATION glcm_lcp_phog_analysis\n\n")
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"Başarılı! ARFF dosyası oluşturuldu: {arff_file}")
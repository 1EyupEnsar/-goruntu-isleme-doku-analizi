#GLCM + Alan/Şekil + Soft Histogram
import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_soft_histogram(gray_img, bins=8):
    """Piksel değerlerinden yumuşak geçişli histogram çıkarır."""
    # Görüntüyü düzleştir (vektör yap)
    pixels = gray_img.flatten().astype(float)
    
    # Bin merkezlerini belirle (0-255 arası)
    bin_centers = np.linspace(0, 255, bins)
    bin_width = bin_centers[1] - bin_centers[0]
    
    soft_hist = np.zeros(bins)
    
    for center_idx, center in enumerate(bin_centers):
        # Her pikselin bu bin merkezine olan uzaklığına göre ağırlık hesapla (Gaussian benzeri)
        # Bu işlem 'soft assignment' sağlar
        dist = np.abs(pixels - center)
        weight = np.maximum(0, 1 - (dist / bin_width))
        soft_hist[center_idx] = np.sum(weight)
    
    # Normalizasyon
    soft_hist /= (soft_hist.sum() + 1e-7)
    return soft_hist.tolist()

def extract_features(img):
    # --- 1. ÖN İŞLEME ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Standart boyutlandırma histogram kararlılığı için iyidir
    gray_res = cv2.resize(gray, (256, 256))
    
    features = {}

    # --- 2. GLCM ÖZELLİKLERİ (Doku) ---
    glcm = graycomatrix(gray_res, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[f"glcm_{name}"] = np.mean(value)

    # --- 3. ALAN VE ŞEKİL ÖZELLİKLERİ (Geometri) ---
    _, thresh = cv2.threshold(gray_res, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h if h > 0 else 0
        
        features["shape_area"] = area
        features["shape_perimeter"] = perimeter
        features["shape_circularity"] = circularity
        features["shape_aspect_ratio"] = aspect_ratio
    else:
        features["shape_area"] = 0
        features["shape_perimeter"] = 0
        features["shape_circularity"] = 0
        features["shape_aspect_ratio"] = 0

    # --- 4. SOFT HISTOGRAM ÖZELLİKLERİ ---
    soft_hist_values = extract_soft_histogram(gray_res, bins=8)
    for i, val in enumerate(soft_hist_values):
        features[f"soft_hist_bin_{i}"] = val

    return features

# --- VERİ OKUMA VE ARFF OLUŞTURMA ---
data_list = []
for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path): continue
    
    print(f"İşleniyor: {class_name}")
    for filename in os.listdir(class_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            img = cv2.imread(os.path.join(class_path, filename))
            if img is None: continue
            
            features = extract_features(img)
            features["class"] = class_name
            data_list.append(features)

df = pd.DataFrame(data_list)
arff_file = "glcm_shape_soft_hist.arff"

with open(arff_file, "w") as f:
    f.write(f"@RELATION glcm_shape_soft_analysis\n\n")
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    f.write("@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"Başarılı! ARFF dosyası oluşturuldu: {arff_file}")
import os
import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_features(img):
    # --- 1. ÖN İŞLEME ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    features = {}

    # --- 2. GLCM ÖZELLİKLERİ (Doku) ---
    glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4],
                        symmetric=True, normed=True)
    glcm_names = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]
    for name in glcm_names:
        value = graycoprops(glcm, name)
        features[name] = np.mean(value)

    # --- 3. ALAN VE ŞEKİL ÖZELLİKLERİ (Geometri) ---
    # Otsu metodu ile yaprağı arka plandan ayırıyoruz (Binary Maske)
    # Yapraklar genellikle beyaz fondaysa THRESH_BINARY_INV kullanılır.
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Konturları (Sınırları) bul
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Görüntüdeki en büyük konturu (yaprağı) seç
        cnt = max(contours, key=cv2.contourArea)
        
        area = cv2.contourArea(cnt)      # Alan
        perimeter = cv2.arcLength(cnt, True) # Çevre
        
        # Dairesellik (Circularity): 4*pi*Alan / Çevre^2 (1'e yakınsa tam daire)
        circularity = (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0
        
        # En-Boy Oranı (Aspect Ratio)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h if h > 0 else 0
        
        features["shape_area"] = area
        features["shape_perimeter"] = perimeter
        features["shape_circularity"] = circularity
        features["shape_aspect_ratio"] = aspect_ratio
    else:
        # Eğer yaprak bulunamazsa değerleri 0 ata
        features["shape_area"] = 0
        features["shape_perimeter"] = 0
        features["shape_circularity"] = 0
        features["shape_aspect_ratio"] = 0

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
            
            features = extract_features(img)
            features["class"] = class_name
            data_list.append(features)

df = pd.DataFrame(data_list)
arff_file = "glcm_shape_features.arff"

with open(arff_file, "w") as f:
    f.write("@RELATION glcm_shape_analysis\n\n")
    for col in df.columns[:-1]:
        f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    
    class_values = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_values}}}\n\n")
    f.write("@DATA\n")
    for _, row in df.iterrows():
        f.write(",".join(map(str, row.values)) + "\n")

print(f"Başarılı! ARFF dosyası oluşturuldu: {arff_file}")
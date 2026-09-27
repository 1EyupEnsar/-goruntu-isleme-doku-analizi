# süper: GLCM + LBP + LCP + Alan/Şekil + HOG + PHOG + SoftHist
import os
import numpy as np
import cv2
import pandas as pd
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern, hog

# VERİSETİNİN KLASÖR YOLU
dataset_path = r"C:\Users\lasto\OneDrive\Desktop\YAPRAKLAR"

def extract_phog(gray_img, bins=8, levels=2):
    """Piramit tabanlı gradyan yönelimlerini hesaplar."""
    gx = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0, ksize=1)
    gy = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1, ksize=1)
    mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
    phog_vector = []
    for level in range(levels + 1):
        num_cells = 2**level
        h, w = gray_img.shape
        cell_h, cell_w = h // num_cells, w // num_cells
        for i in range(num_cells):
            for j in range(num_cells):
                angle_cell = angle[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                mag_cell = mag[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                hist, _ = np.histogram(angle_cell, bins=bins, range=(0, 360), weights=mag_cell)
                norm = np.linalg.norm(hist) + 1e-7
                phog_vector.extend(hist / norm)
    return phog_vector

def extract_soft_histogram(gray_img, bins=8):
    """Yumuşak geçişli yoğunluk histogramı hesaplar."""
    pixels = gray_img.flatten().astype(float)
    bin_centers = np.linspace(0, 255, bins)
    bin_width = bin_centers[1] - bin_centers[0]
    soft_hist = np.zeros(bins)
    for center_idx, center in enumerate(bin_centers):
        dist = np.abs(pixels - center)
        weight = np.maximum(0, 1 - (dist / bin_width))
        soft_hist[center_idx] = np.sum(weight)
    soft_hist /= (soft_hist.sum() + 1e-7)
    return soft_hist.tolist()

def extract_all_features(img):
    # --- 1. ÖN İŞLEME ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_res = cv2.resize(gray, (128, 128))
    features = {}

    # --- A. GLCM (Doku) ---
    glcm = graycomatrix(gray_res, [8], [0, np.pi/4, np.pi/2, 3*np.pi/4], symmetric=True, normed=True)
    for name in ["contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"]:
        features[f"glcm_{name}"] = np.mean(graycoprops(glcm, name))

    # --- B. LBP (Yerel Doku) ---
    radius, n_points = 1, 8
    lbp = local_binary_pattern(gray_res, n_points, radius, method='uniform')
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
    hist = hist.astype("float") / (hist.sum() + 1e-7)
    for i, val in enumerate(hist): features[f"lbp_bin_{i}"] = val

    # --- C. LCP (Yerel Kontrast) ---
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)
    lcp_map = np.abs(cv2.filter2D(gray_res.astype(np.float32), -1, kernel))
    (lcp_hist, _) = np.histogram(lcp_map.ravel(), bins=8, range=(0, 255))
    lcp_hist = lcp_hist.astype("float") / (lcp_hist.sum() + 1e-7)
    for i, val in enumerate(lcp_hist): features[f"lcp_bin_{i}"] = val

    # --- D. ALAN VE ŞEKİL (Geometri) ---
    _, thresh = cv2.threshold(gray_res, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        features["shape_area"] = area
        features["shape_perimeter"] = perimeter
        features["shape_circularity"] = (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0
        x, y, w, h = cv2.boundingRect(cnt)
        features["shape_aspect_ratio"] = float(w) / h if h > 0 else 0
    else:
        for k in ["area", "perimeter", "circularity", "aspect_ratio"]: features[f"shape_{k}"] = 0

    # --- E. HOG (Genel Şekil Hatları) ---
    hog_feats = hog(gray_res, orientations=9, pixels_per_cell=(16, 16), cells_per_block=(2, 2))
    features["hog_mean"] = np.mean(hog_feats)
    features["hog_std"] = np.std(hog_feats)

    # --- F. PHOG (Piramit Şekil) ---
    phog_feats = extract_phog(gray_res, bins=8, levels=2)
    for i, val in enumerate(phog_feats): features[f"phog_{i}"] = val

    # --- G. SOFT HISTOGRAM (Yumuşak Geçişli Renk Dağılımı) ---
    sh_vals = extract_soft_histogram(gray_res, bins=8)
    for i, val in enumerate(sh_vals): features[f"soft_hist_{i}"] = val

    return features

# --- ANA DÖNGÜ ---
data_list = []
for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path): continue
    print(f"İşleniyor: {class_name}")
    for filename in os.listdir(class_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(os.path.join(class_path, filename))
            if img is None: continue
            feats = extract_all_features(img)
            feats["class"] = class_name
            data_list.append(feats)

df = pd.DataFrame(data_list)
arff_file = "full_feature_fusion8.arff"
with open(arff_file, "w") as f:
    f.write(f"@RELATION super_leaf_features\n\n")
    for col in df.columns[:-1]: f.write(f"@ATTRIBUTE {col} NUMERIC\n")
    class_vals = ",".join(sorted(df["class"].unique()))
    f.write(f"@ATTRIBUTE class {{{class_vals}}}\n\n@DATA\n")
    for _, row in df.iterrows(): f.write(",".join(map(str, row.values)) + "\n")

print(f"Tam donanımlı ARFF dosyası oluşturuldu: {arff_file}")
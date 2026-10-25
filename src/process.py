import pandas as pd
import re
import numpy as np

def extract_year(text):
    if pd.isna(text): return None
    match = re.search(r'\b(19\d{2}|20\d{2})\b', str(text))
    return int(match.group(1)) if match else None

def extract_price(text):
    if pd.isna(text): return np.nan
    match = re.search(r'৳\s*([\d,]+)', str(text))
    if match:
        val = match.group(1).replace(',', '')
        return float(val) * 210
    return np.nan

def extract_gb(text):
    if pd.isna(text): return np.nan
    match = re.search(r'(\d+)\s*(GB|TB)', str(text), re.IGNORECASE)
    if match:
        val = float(match.group(1))
        unit = match.group(2).upper()
        if unit == 'TB': val *= 1024
        return val
    return np.nan

def extract_mp(text):
    if pd.isna(text): return np.nan
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*MP', str(text), re.IGNORECASE)
    if matches:
        return max([float(m) for m in matches])
    return np.nan

def get_panel(text):
    text = str(text).upper()
    if 'AMOLED' in text: return 'AMOLED'
    if 'OLED' in text: return 'OLED'
    if 'IPS' in text: return 'IPS LCD'
    if 'TFT' in text: return 'TFT LCD'
    if 'LCD' in text: return 'LCD'
    return 'Unknown'

def extract_resolution(text):
    if pd.isna(text): return np.nan
    # Lấy chuỗi pixel thuần túy dạng "1080 x 2400"
    match = re.search(r'(\d{3,4}\s*[xX]\s*\d{3,4})', str(text))
    return match.group(1) if match else np.nan

df = pd.read_csv('data/phones.csv')

df['Nam_ra_mat'] = df['Launch.Announced'].apply(extract_year).fillna(df['Launch.Status'].apply(extract_year))
df = df[df['Nam_ra_mat'].isin([2024, 2025, 2026])]

df_clean = pd.DataFrame()
df_clean['Ten_may'] = df['Ten_may']
df_clean['Hang'] = df['General.Brand'].str.title()
df_clean['Nam_ra_mat'] = df['Nam_ra_mat'].astype(int)
df_clean['Gia_ban'] = df['Gia_ban'].apply(extract_price)

df_clean['He_dieu_hanh'] = df['Platform.OS'].astype(str).str.split(',').str[0]
df_clean['Chipset'] = df['Platform.Chipset']

df_clean['RAM'] = df['Memory.RAM'].apply(extract_gb)
df_clean['ROM'] = df['Memory.Internal'].apply(extract_gb)

df_clean['Ho_tro_5G'] = df['Network.5G bands'].notna().astype(int)
df_clean['Dung_luong_pin'] = df['Battery.Capacity'].astype(str).str.extract(r'(\d{3,5})')[0].astype(float)
df_clean['Cong_suat_sac_W'] = df['Battery.Charging'].astype(str).str.extract(r'(\d+)\s*W')[0].astype(float)

df_clean['Kich_thuoc_man'] = df['Display.Size'].astype(str).str.extract(r'(\d+\.\d+)')[0].astype(float)
df_clean['Tan_so_quet_Hz'] = df['Display.Type'].astype(str).str.extract(r'(\d{2,3})\s*Hz')[0].astype(float)
df_clean['Tam_nen'] = df['Display.Type'].apply(get_panel)
df_clean['Do_phan_giai'] = df['Display.Resolution'].apply(extract_resolution)

df_clean['Cam_sau_MP'] = df['Main camera.Single'].fillna(df['Main camera.Dual']).fillna(df['Main camera.Triple']).fillna(df['Main camera.Quad']).apply(extract_mp)
df_clean['Cam_truoc_MP'] = df['Selfie camera.Single'].fillna(df['Selfie camera.Dual']).apply(extract_mp)
df_clean['Khoi_luong'] = df['Body.Weight'].astype(str).str.extract(r'(\d+)\s*g')[0].astype(float)

df_clean = df_clean.dropna(subset=['Gia_ban', 'RAM', 'ROM'])
df_clean = df_clean.drop_duplicates(subset=['Ten_may'])
df_clean = df_clean.sort_values(by=['Ten_may'])

df_clean.to_csv('data/data_clean.csv', index=False, encoding='utf-8-sig', na_rep='N/a')
print(f"Đã xử lý xong! Thu được {len(df_clean)} máy kèm cột Độ phân giải.")
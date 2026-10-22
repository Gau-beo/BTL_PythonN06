import pandas as pd

df1 = pd.read_csv('data/MockData/dien_thoai_viet_nam_1021.csv')
df2 = pd.read_csv('data/MockData/results.csv')

df = pd.concat([df1, df2], ignore_index=True)
df = df.dropna(how='all')

for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].astype(str).str.strip()

df['Gia_ban'] = pd.to_numeric(df['Gia_ban'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
df['RAM'] = pd.to_numeric(df['RAM'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')

df_clean = df.dropna(subset=['Gia_ban', 'RAM'])
df_clean = df_clean.drop_duplicates()

df_clean.to_csv('data/data_clean.csv', index=False, encoding='utf-8-sig')
print("Đã xử lý xong và lưu file tại data/data_clean.csv thành công!")
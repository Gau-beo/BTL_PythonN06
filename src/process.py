import re
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parents[1]
FILE_VAO = GOC / "data" / "phones.csv"
FILE_RA = GOC / "data" / "data_clean.csv"

FILE_RA = GOC / "data" / "test"/ "data_clean.csv"
FILE_VAO = GOC / "data" / "test" / "phones_crawled.csv"

NAM_MIN, NAM_MAX = 2023, 2026
TY_GIA_BDT_VND = 210
LOAI_THIET_BI = {"Smartphones", "Mobiles"}
UU_TIEN_GIA = ["Official", "Unofficial", "Expected"]

HOP_LE = {
    "ROM": (8, 2048), "RAM": (1, 32), "Kich_thuoc_man": (3.0, 9.0),
    "Khoi_luong": (90, 750), "Dung_luong_pin": (1500, 12000), "Tan_so_quet_Hz": (48, 360),
}


def nam_ra_mat(text):
    m = re.search(r"\b(20\d{2})\b", str(text)) if pd.notna(text) else None
    return int(m.group(1)) if m else np.nan


def so(s):
    return float(s.replace(",", ""))


def tach_gia(text):
    if pd.isna(text):
        return None, np.nan, np.nan, np.nan
    chuoi = re.sub(r"Updated on:.*", "", str(text))
    chuoi = re.sub(r"(Save|Pay)\s*৳\s*[\d,]+(\s*[+-]\d+%)?", " ", chuoi)
    cac_doan = re.split(r"(?=\b(?:Official|Unofficial|Expected)\b)", chuoi)
    doan_theo_loai = {}
    for d in cac_doan:
        m = re.match(r"\s*(Official|Unofficial|Expected)\b", d)
        if m and re.search(r"৳", d):
            doan_theo_loai.setdefault(m.group(1), d)
    for loai in UU_TIEN_GIA:
        if loai in doan_theo_loai:
            d = doan_theo_loai[loai]
            cac_gia = [so(x) for x in re.findall(r"৳\s*([\d,]+)", d) if so(x) > 0]
            if not cac_gia:
                continue
            gia = min(cac_gia)
            bo_nho = []
            for n, u in re.findall(r"\b(\d+)\s*(TB|GB|G)\b", d):
                bo_nho.append(int(n) * (1024 if u == "TB" else 1))
            ram, rom = np.nan, np.nan
            if len(bo_nho) >= 2:
                ram, rom = bo_nho[0], bo_nho[1]
            elif len(bo_nho) == 1:
                rom = bo_nho[0]
            return loai, gia, ram, rom
    return None, np.nan, np.nan, np.nan


def gb_dau_tien(text):
    if pd.isna(text):
        return np.nan
    m = re.search(r"(\d+(?:\s*/\s*\d+)*)\s*(GB|TB|MB)\b", str(text), re.I)
    if not m:
        return np.nan
    gia_tri = float(re.split(r"\s*/\s*", m.group(1))[0])
    don_vi = m.group(2).upper()
    return gia_tri * 1024 if don_vi == "TB" else (np.nan if don_vi == "MB" else gia_tri)


def cap_dau_variant(text):
    if pd.isna(text):
        return np.nan, np.nan
    m = re.search(r"(\d+)\s*GB\s*(\d+)\s*(GB|TB)", str(text), re.I)
    if not m:
        return np.nan, np.nan
    rom = float(m.group(2)) * (1024 if m.group(3).upper() == "TB" else 1)
    return float(m.group(1)), rom


def max_mp(text):
    if pd.isna(text):
        return np.nan
    ds = re.findall(r"(\d+(?:\.\d+)?)\s*MP", str(text), re.I)
    return max(float(x) for x in ds) if ds else np.nan


def tan_so_quet(text):
    t = re.sub(r"\d+\s*Hz\s*PWM", " ", str(text), flags=re.I)
    ds = re.findall(r"(?<!\d)(\d{2,3})\s*Hz", t)
    return max(float(x) for x in ds) if ds else np.nan


def tam_nen(text):
    t = str(text).upper()
    for khoa, ten in [("AMOLED", "AMOLED"), ("OLED", "OLED"), ("IPS", "IPS LCD"), ("TFT", "TFT LCD"), ("LCD", "LCD")]:
        if khoa in t:
            return ten
    return np.nan


def do_phan_giai(text):
    m = re.search(r"(\d{3,4})\s*[xX]\s*(\d{3,4})", str(text)) if pd.notna(text) else None
    return f"{m.group(1)} x {m.group(2)}" if m else np.nan


def cong_suat_sac(text):
    t = str(text)
    m = re.search(r"(\d+)\s*W\s*wired", t, re.I) or re.search(r"(\d+)\s*W", t)
    return float(m.group(1)) if m else np.nan


def trich(series, pattern):
    return series.astype(str).str.extract(pattern)[0].astype(float)

def main():
    df = pd.read_csv(FILE_VAO)
    nhat_ky = [("Dòng trong phones.csv", len(df))]

    df = df[df["General.Device"].isin(LOAI_THIET_BI)].copy()
    nhat_ky.append(("Sau khi chỉ giữ điện thoại (bỏ tablet, đồng hồ, máy cơ bản)", len(df)))

    nam = df["Launch.Announced"].apply(nam_ra_mat).fillna(df["Launch.Status"].apply(nam_ra_mat))
    df = df[nam.between(NAM_MIN, NAM_MAX)].copy()
    df["Nam_ra_mat"] = nam[df.index].astype(int)
    nhat_ky.append((f"Sau khi lọc ra mắt {NAM_MIN}-{NAM_MAX}", len(df)))

    gia = df["Gia_ban"].apply(tach_gia)
    df["Loai_gia"] = gia.str[0]
    df["Gia_BDT"] = gia.str[1]
    ram_gia, rom_gia = gia.str[2], gia.str[3]

    ram_var, rom_var = zip(*df["Memory.Variant"].apply(cap_dau_variant)) if len(df) else ([], [])
    ram_var, rom_var = pd.Series(ram_var, index=df.index), pd.Series(rom_var, index=df.index)

    ram = ram_gia.fillna(ram_var).fillna(df["Memory.RAM"].apply(gb_dau_tien))
    rom = rom_gia.fillna(rom_var).fillna(df["Memory.Internal"].apply(gb_dau_tien))

    out = pd.DataFrame(index=df.index)
    out["Ten_may"] = df["Ten_may"].str.strip()
    out["Hang"] = df["General.Brand"].str.title().replace({"Tcl": "TCL"})
    out["Nam_ra_mat"] = df["Nam_ra_mat"]
    out["Gia_ban"] = (df["Gia_BDT"] * TY_GIA_BDT_VND).round(0)
    out["He_dieu_hanh"] = df["Platform.OS"].astype(str).str.split(",").str[0].replace({"nan": np.nan})
    out["Chipset"] = df["Platform.Chipset"]
    out["RAM"] = ram
    out["ROM"] = rom
    out["Ho_tro_5G"] = (df["Network.5G bands"].notna() | df["Network.Technology"].astype(str).str.contains("5G")).astype(int)
    out["Dung_luong_pin"] = trich(df["Battery.Capacity"], r"(\d{3,5})\s*mAh")
    out["Cong_suat_sac_W"] = df["Battery.Charging"].apply(cong_suat_sac)
    out["Kich_thuoc_man"] = trich(df["Display.Size"], r"(\d+(?:\.\d+)?)\s*inch")
    out["Tan_so_quet_Hz"] = (df["Display.Type"].fillna("") + " " + df["Display.Features"].fillna("")).apply(tan_so_quet)
    out["Tam_nen"] = df["Display.Type"].apply(tam_nen)
    out["Do_phan_giai"] = df["Display.Resolution"].apply(do_phan_giai)
    cam_sau = df.reindex(columns=[
        "Main camera.Single", "Main camera.Dual",
        "Main camera.Triple", "Main camera.Quad",
    ]).bfill(axis=1).iloc[:, 0]
    cam_truoc = df.reindex(columns=[
        "Selfie camera.Single", "Selfie camera.Dual",
    ]).bfill(axis=1).iloc[:, 0]
    out["Cam_sau_MP"] = cam_sau.apply(max_mp)
    out["Cam_truoc_MP"] = cam_truoc.apply(max_mp)
    out["Khoi_luong"] = trich(df["Body.Weight"], r"(\d+(?:\.\d+)?)\s*g\b")
    out["URL"] = df["URL"]

    for cot, (lo, hi) in HOP_LE.items():
        sai = out[cot].notna() & ~out[cot].between(lo, hi)
        if sai.any():
            nhat_ky.append((f"  {cot} ngoài [{lo}, {hi}] đặt thành N/a", int(sai.sum())))
        out.loc[sai, cot] = np.nan

    out = out.dropna(subset=["Gia_ban", "RAM", "ROM"])
    nhat_ky.append(("Sau khi bỏ máy thiếu Gia_ban / RAM / ROM", len(out)))
    out = out.drop_duplicates(subset=["Ten_may"])
    nhat_ky.append(("Sau khi bỏ trùng tên máy (giữ bản đầu)", len(out)))

    out = out.sort_values(by=["Ten_may", "Nam_ra_mat"], ascending=[True, False])
    out.to_csv(FILE_RA, index=False, encoding="utf-8-sig", na_rep="N/a")

    print("=== NHẬT KÝ LÀM SẠCH ===")
    for ten, n in nhat_ky:
        print(f"{ten:<70}{n:>6}")
    print("\nSố máy theo năm :", out["Nam_ra_mat"].value_counts().sort_index().to_dict())
    print("Số máy theo hãng:", out["Hang"].value_counts().to_dict())
    print("Loại giá (chỉ ghi log, không lưu vào CSV):", df.loc[out.index, "Loai_gia"].value_counts().to_dict())
    print("Tỷ lệ N/a (%)   :", (out.isna().mean() * 100).round(1)[lambda s: s > 0].to_dict())
    print(f"\nĐã ghi {FILE_RA} ({len(out)} máy, {out.shape[1]} cột)")

if __name__ == "__main__":
    main()

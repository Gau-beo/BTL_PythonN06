"""Kiểm tra file mô hình .pkl: nạp được, giá hợp lý, phân biệt được máy rẻ/đắt, chịu được ô trống và giá trị lạ.
Chạy sau khi đã chạy train_model.py:
    python src/test_model.py
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

SRC = Path(__file__).resolve().parents[1] / "models"   # models/ nằm ở thư mục gốc dự án
for name in ("phone_price_model.pkl", "model_meta.json"):
    if not (SRC / name).exists():
        sys.exit(f"[LỖI] Chưa có {name}. Hãy chạy 'python src/train_model.py' trước (file nằm ở models/).")

model = joblib.load(SRC / "phone_price_model.pkl")
with open(SRC / "model_meta.json", encoding="utf-8") as f:
    meta = json.load(f)

if meta["sklearn_version"] != sklearn.__version__:
    print(f"[CẢNH BÁO] Phiên bản scikit-learn khác nhau: lúc train {meta['sklearn_version']}, "
          f"hiện tại {sklearn.__version__}. Nhóm Web cần cài đúng phiên bản.")

features, choices, rng = meta["features"], meta["choices"], meta["numeric_ranges"]
pmin, pmax = meta["price_range"]["min"], meta["price_range"]["max"]
LO, HI = pmin * 0.5, pmax * 2          # khoảng giá chấp nhận được


def make_phone(**kw):
    """Máy 'trung bình' (giá trị phổ biến nhất trong dữ liệu), ghi đè bằng kw."""
    row = dict(meta["defaults"])
    row.update({k: v for k, v in kw.items() if k in row and v is not None})
    return pd.DataFrame([row], columns=features)


def price(df):
    return float(model.predict(df)[0])


def pick(col, prefs):
    """Chọn giá trị đầu tiên trong prefs có mặt trong dropdown của cột col."""
    return next((p for p in prefs if p in choices.get(col, [])), None)


ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'OK ' if cond else 'LỖI'}] {name} {detail}")


print(f"Mô hình: {meta['model_name']} | khoảng giá trong dữ liệu: {pmin:,.0f} - {pmax:,.0f} VNĐ")
print(f"Lưu ý: {meta['currency_note']}\n")

# 1. Máy trung bình cho giá hợp lý
p0 = price(make_phone())
check("Giá máy trung bình nằm trong khoảng hợp lý", LO <= p0 <= HI, f"-> {p0:,.0f}")

# 2. Máy cao cấp phải đắt hơn rõ rệt so với máy phổ thông
SPEC = ["RAM", "ROM", "Cam_sau_MP", "Tan_so_quet_Hz", "Dung_luong_pin", "Cong_suat_sac_W"]
re_ = {c: rng[c]["p01"] for c in SPEC}
dat = {c: rng[c]["p99"] for c in SPEC}
for col, ds_re, ds_dat in [
    ("Hang", ["Itel", "Tecno", "Infinix"], ["Samsung", "Apple"]),
    ("Chipset_dong", ["Unisoc", "Helio"], ["Snapdragon 8", "Apple A"]),
    ("Tam_nen", ["TFT LCD", "IPS LCD", "LCD"], ["AMOLED", "OLED"]),
    ("Do_phan_giai", ["HD+"], ["2K+", "FHD+"]),
]:
    re_[col], dat[col] = pick(col, ds_re), pick(col, ds_dat)
p_re, p_dat = price(make_phone(**re_)), price(make_phone(**dat))
check("Máy cao cấp đắt gấp hơn 2 lần máy phổ thông", p_dat > 2 * p_re,
      f"(phổ thông {p_re:,.0f} | cao cấp {p_dat:,.0f})")

# 3. Từng hãng trong dropdown cho giá hợp lệ
gia_hang = {h: price(make_phone(Hang=h)) for h in choices["Hang"]}
bad = [h for h, p in gia_hang.items() if not LO <= p <= HI]
check("Mọi hãng trong dropdown cho giá hợp lý", not bad, f"(bất thường: {bad})" if bad else "")
for h, p in gia_hang.items():
    print(f"    {h:12s}: {p:>14,.0f} VNĐ")

# 4. Ô trống hoàn toàn, giá trị chữ lạ và số liệu cực đoan
pb = price(pd.DataFrame([{c: np.nan for c in features}]))
check("Ô trống hoàn toàn vẫn cho giá hợp lý", LO <= pb <= HI, f"-> {pb:,.0f}")
la = {**{c: "GiaTriLa" for c in meta["categorical_features"]}, **{c: 1e9 for c in meta["numeric_features"]}}
pl = price(make_phone(**la))
check("Giá trị chữ lạ và số liệu cực đoan vẫn cho giá hợp lý", LO <= pl <= HI, f"-> {pl:,.0f}")

# 5. Nhiều dòng cùng lúc
check("Dự đoán nhiều dòng", len(model.predict(pd.concat([make_phone(), make_phone(**dat)]))) == 2)

print("\n=> TẤT CẢ ĐỀU ỔN" if ok else "\n=> CÓ LỖI, xem các dòng [LỖI] ở trên")
sys.exit(0 if ok else 1)
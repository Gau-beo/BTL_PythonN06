"""Kiểm tra file mô hình .pkl: nạp được, giá ra VNĐ hợp lý, chịu được dữ liệu thiếu/lạ.
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

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "src" / "phone_price_model.pkl"
META_PATH = ROOT / "src" / "model_meta.json"

for p in (MODEL_PATH, META_PATH):
    if not p.exists():
        sys.exit(f"[LỖI] Chưa có {p.name}. Hãy chạy 'python src/train_model.py' trước.")

model = joblib.load(MODEL_PATH)
with open(META_PATH, encoding="utf-8") as f:
    meta = json.load(f)

if meta.get("sklearn_version") and meta["sklearn_version"] != sklearn.__version__:
    print(f"[CẢNH BÁO] Phiên bản scikit-learn khác nhau: lúc train {meta['sklearn_version']}, hiện tại {sklearn.__version__}")
    print(f"[CẢNH BÁO] Phiên bản scikit-learn khác nhau: lúc train {meta['sklearn_version']}, "
          f"hiện tại {sklearn.__version__}. Nhóm Web cần cài đúng phiên bản.")

features = meta["features"]
pmin, pmax = meta["price_range"]["min"], meta["price_range"]["max"]
LO, HI = pmin * 0.5, pmax * 2          # khoảng giá chấp nhận được
rng = meta["numeric_ranges"]


def make_phone(**kw):
    row = dict(meta["defaults"])
    row.update({k: v for k, v in kw.items() if k in row})
    return pd.DataFrame([row], columns=features)


def price(df):
    return float(model.predict(df)[0])


ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'OK ' if cond else 'LỖI'}] {name} {detail}")


print(f"Mô hình: {meta['model_name']} | khoảng giá trong dữ liệu: {pmin:,.0f} - {pmax:,.0f} VNĐ\n")

# 1. Dự đoán cơ bản (máy 'trung bình')
p0 = price(make_phone())
print(f"Giá dự đoán (máy trung bình): {p0:,.0f} VNĐ")
check("Giá là VNĐ và nằm trong khoảng hợp lý", LO <= p0 <= HI, f"-> {p0:,.0f}")

# 2. Cấu hình mạnh hơn thì giá không thấp hơn
if "RAM" in rng and "ROM" in rng:
    low = price(make_phone(RAM=rng["RAM"]["p01"], ROM=rng["ROM"]["p01"]))
    high = price(make_phone(RAM=rng["RAM"]["p99"], ROM=rng["ROM"]["p99"]))
    print(f"RAM/ROM thấp: {low:,.0f} | cao: {high:,.0f}")
    check("RAM/ROM cao -> giá không thấp hơn", high >= low)
else:
    print("[BỎ QUA] Không có RAM/ROM trong feature")

# 3. Từng hãng trong dropdown phải cho giá hợp lý
if "Hang" in meta["choices"]:
    bad = []
    for h in meta["choices"]["Hang"]:
        p = price(make_phone(Hang=h))
        flag = "" if LO <= p <= HI else "  <-- BẤT THƯỜNG"
        print(f"  Hãng {h:12s}: {p:>16,.0f} VNĐ{flag}")
        if flag:
            bad.append(h)
    check("Mọi hãng trong dropdown cho giá hợp lý", not bad, f"(bất thường: {bad})" if bad else "")

# 4. Toàn bộ ô rỗng
try:
    pb = price(pd.DataFrame([{c: np.nan for c in features}]))
    check("Ô rỗng hoàn toàn vẫn cho giá hợp lý", LO <= pb <= HI, f"-> {pb:,.0f}")
except Exception as e:  # noqa: BLE001
    check("Ô rỗng hoàn toàn vẫn cho giá hợp lý", False, repr(e))

# 5. Hãng chưa từng thấy / giá trị số cực đoan
if "Hang" in meta["choices"]:
    try:
        p = price(make_phone(Hang="HangLa_ChuaTungThay"))
        check("Hãng lạ cho giá hợp lý", LO <= p <= HI, f"-> {p:,.0f}")
    except Exception as e:  # noqa: BLE001
        check("Hãng lạ cho giá hợp lý", False, repr(e))
try:
    p = price(make_phone(**{c: 1e9 for c in meta["numeric_features"]}))
    check("Số liệu cực đoan (1e9) vẫn cho giá hợp lý", LO <= p <= HI, f"-> {p:,.0f}")
except Exception as e:  # noqa: BLE001
    check("Số liệu cực đoan (1e9) vẫn cho giá hợp lý", False, repr(e))

# 6. Nhiều dòng cùng lúc
batch = pd.concat([make_phone(), make_phone()], ignore_index=True)
check("Dự đoán nhiều dòng", len(model.predict(batch)) == 2)

print("\n=> TẤT CẢ ĐỀU ỔN" if ok else "\n=> CÓ LỖI, xem các dòng [LỖI] ở trên")
sys.exit(0 if ok else 1)
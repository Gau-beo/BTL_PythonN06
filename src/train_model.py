"""Ước lượng giá điện thoại (Nhóm 06) - [GĐ2] Huấn luyện mô hình ước lượng giá.

Đầu vào : data/data_clean.csv (do process.py tạo ra).
          Cột Gia_ban = giá bán tại Bangladesh (BDT) x tỉ giá, đã quy đổi sang VNĐ.
Đầu ra  : models/phone_price_model.pkl   (predict() trả về giá quy đổi, đơn vị VNĐ)
          models/model_meta.json         (đặc trưng, lựa chọn dropdown, khoảng giá cho form web)
          models/model_metrics.csv       (bảng so sánh 3 mô hình)
          models/report_numbers.txt      (các số liệu để điền vào báo cáo)
          figures/*.png               (3 biểu đồ)

Chạy:  python src/train_model.py
"""
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # không cần giao diện
import matplotlib.pyplot as plt
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
sys.path.insert(0, str(SRC))
try:
    from process import TY_GIA_BDT_VND   # lấy tỉ giá từ process.py để hai file luôn khớp nhau
except Exception:
    TY_GIA_BDT_VND = 210

CSV_PATH = ROOT / "data" / "data_clean.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "phone_price_model.pkl"
META_PATH = MODEL_DIR / "model_meta.json"
FIG_DIR = ROOT / "figures"

TARGET = "Gia_ban"
MIN_CAT_COUNT = 5          # giá trị chữ xuất hiện < 5 lần gộp vào nhóm "hiếm"
CLIP_Q = (0.01, 0.99)      # cắt giá trị số về phân vị 1%-99% (chặn số liệu cực đoan nhập từ web)

# Chỉ dùng đặc trưng cấu hình mà người dùng web nhập được vào form.
# (Nam_ra_mat có sẵn trong dữ liệu; thêm vào NUM_COLS nếu muốn dùng, độ chính xác tăng rất ít.)
NUM_COLS = [
    "RAM", "ROM", "Ho_tro_5G", "Kich_thuoc_man", "Tan_so_quet_Hz",
    "Cam_sau_MP", "Cam_truoc_MP", "Khoi_luong", "Dung_luong_pin", "Cong_suat_sac_W",
]
CAT_COLS = ["Hang", "Chipset_dong", "Tam_nen", "Do_phan_giai"]

LABELS = {
    "RAM": "RAM (GB)", "ROM": "Bộ nhớ trong (GB)", "Ho_tro_5G": "Hỗ trợ 5G (1 = có, 0 = không)",
    "Kich_thuoc_man": "Kích thước màn hình (inch)", "Tan_so_quet_Hz": "Tần số quét (Hz)",
    "Cam_sau_MP": "Camera sau (MP)", "Cam_truoc_MP": "Camera trước (MP)",
    "Khoi_luong": "Khối lượng (g)", "Dung_luong_pin": "Dung lượng pin (mAh)",
    "Cong_suat_sac_W": "Công suất sạc (W)",
    "Hang": "Hãng", "Chipset_dong": "Dòng chip", "Tam_nen": "Loại màn hình",
    "Do_phan_giai": "Độ phân giải",
}


# ----------------------------------------------------------------------------
# DỮ LIỆU
# ----------------------------------------------------------------------------
def group_chipset(s):
    """Gom tên chipset về dòng chip (vd 'Qualcomm SM8750-AB Snapdragon 8 Elite (3 nm)' -> 'Snapdragon 8')."""
    t = str(s).lower()
    if "snapdragon" in t:
        m = re.search(r"snapdragon\s*(\d)", t)
        return f"Snapdragon {m.group(1)}" if m else "Snapdragon"
    if "dimensity" in t:
        m = re.search(r"dimensity\s*(\d)", t)
        return f"Dimensity {m.group(1)}" if m else "Dimensity"
    if "helio" in t:
        return "Helio"
    if "apple" in t or re.search(r"\ba\d{2}\b", t) or "bionic" in t:
        return "Apple A"
    if "exynos" in t:
        return "Exynos"
    if "tensor" in t:
        return "Tensor"
    if "unisoc" in t or "tiger" in t or re.search(r"\bt\d{3,4}\b", t):
        return "Unisoc"
    return "Khac"


def group_do_phan_giai(s):
    """Gom '1080 x 2400' về HD+ / FHD+ / 2K+ theo số điểm ảnh của cạnh ngắn."""
    m = re.search(r"(\d{3,4})\s*x\s*(\d{3,4})", str(s))
    if not m:
        return "Khac"
    short = min(int(m.group(1)), int(m.group(2)))
    return "HD+" if short <= 800 else ("FHD+" if short <= 1300 else "2K+")


def load_data():
    if not CSV_PATH.exists():
        sys.exit(f"[LỖI] Không tìm thấy {CSV_PATH}. Hãy chạy process.py trước.")
    df = pd.read_csv(CSV_PATH, na_values=["N/a"]).dropna(subset=[TARGET])

    df["Chipset_dong"] = df["Chipset"].apply(group_chipset)
    df["Do_phan_giai"] = df["Do_phan_giai"].apply(group_do_phan_giai)
    # Cột chữ để kiểu object với np.nan cho ô thiếu (SimpleImputer không xử lý được pd.NA)
    for c in CAT_COLS:
        df[c] = df[c].astype(object).where(df[c].notna(), np.nan)

    thieu = [c for c in NUM_COLS + CAT_COLS if c not in df.columns]
    if thieu:
        sys.exit(f"[LỖI] data_clean.csv thiếu cột: {thieu}")
    return df


# ----------------------------------------------------------------------------
# MÔ HÌNH
# ----------------------------------------------------------------------------
def make_model(estimator, lo, hi):
    """Pipeline + log-giá. Nhờ TransformedTargetRegressor, predict() trả về giá thật (không phải log)."""
    num = Pipeline([
        ("clip", FunctionTransformer(np.clip, kw_args={"a_min": lo, "a_max": hi},
                                     feature_names_out="one-to-one")),
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
    ])
    cat = Pipeline([
        ("imp", SimpleImputer(strategy="constant", fill_value="Khac")),
        # giá trị hiếm và giá trị chưa từng thấy đều rơi vào nhóm "hiếm"
        ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=MIN_CAT_COUNT)),
    ])
    prep = ColumnTransformer([("num", num, NUM_COLS), ("cat", cat, CAT_COLS)])
    return TransformedTargetRegressor(
        regressor=Pipeline([("prep", prep), ("model", estimator)]),
        func=np.log1p, inverse_func=np.expm1,
    )


def metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
        "MAPE": float(np.mean(np.abs(y_true - y_pred) / y_true) * 100),
    }


def feature_importance(model, top=10):
    reg = model.regressor_
    est = reg.named_steps["model"]
    names = [n.split("__", 1)[-1] for n in reg.named_steps["prep"].get_feature_names_out()]
    if hasattr(est, "feature_importances_"):
        return pd.Series(est.feature_importances_, index=names).nlargest(top), "Độ quan trọng"
    return pd.Series(np.abs(est.coef_), index=names).nlargest(top), "|Hệ số| (đã chuẩn hóa)"


def save_plots(y_te, pred_best, best, model_for_importance, test_res):
    plt.figure(figsize=(6, 6))
    plt.scatter(y_te / 1e6, pred_best / 1e6, alpha=0.7, color="teal")
    lim = [0, max(y_te.max(), pred_best.max()) / 1e6]
    plt.plot(lim, lim, "r--", label="Đường chuẩn lý tưởng")
    plt.xlabel("Giá thực tế (triệu VNĐ quy đổi)")
    plt.ylabel("Giá dự đoán (triệu VNĐ quy đổi)")
    plt.title(f"Thực tế vs Dự đoán ({best})")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "gia_thuc_te_vs_du_doan.png", dpi=150)
    plt.close()

    imp, xlabel = feature_importance(model_for_importance)
    plt.figure(figsize=(9, 5))
    imp[::-1].plot(kind="barh", color="coral")
    plt.title(f"Top 10 đặc trưng ảnh hưởng giá nhất ({best})")
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "do_quan_trong_dac_trung.png", dpi=150)
    plt.close()

    names = list(test_res)
    r2s = [test_res[m]["R2"] for m in names]
    plt.figure(figsize=(7, 4))
    plt.bar(names, r2s, color=["skyblue", "orange", "lightgreen"])
    plt.ylabel("R2 Score (tập test)")
    plt.title("So sánh độ chính xác (R2) giữa các mô hình")
    plt.ylim(min(0, min(r2s) - 0.1), 1.1)
    for i, v in enumerate(r2s):
        plt.text(i, v + 0.02, f"{v:.3f}", ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "so_sanh_mo_hinh.png", dpi=150)
    plt.close()


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    FIG_DIR.mkdir(exist_ok=True)
    MODEL_DIR.mkdir(exist_ok=True)
    df = load_data()
    features = NUM_COLS + CAT_COLS
    print(f"Đọc dữ liệu: {CSV_PATH} ({len(df)} máy)")
    print(f"Lưu ý: Gia_ban là giá Bangladesh (BDT) x {TY_GIA_BDT_VND}, đã quy đổi sang VNĐ.")
    print(f"Đặc trưng ({len(features)}): {features}")

    X, y = df[features], df[TARGET].astype(float)
    qs = X[NUM_COLS].quantile(list(CLIP_Q))
    lo, hi = qs.loc[CLIP_Q[0]].values, qs.loc[CLIP_Q[1]].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    estimators = {
        "Ridge Regression": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }
    models = {n: make_model(e, lo, hi) for n, e in estimators.items()}

    # Chọn mô hình bằng cross-validation trên tập train (ổn định hơn 1 lần chia test)
    kf = KFold(5, shuffle=True, random_state=42)
    cv_res, test_res, test_pred = {}, {}, {}
    print("\n--- HUẤN LUYỆN VÀ ĐÁNH GIÁ ---")
    for name, model in models.items():
        cv = cross_val_score(model, X_tr, y_tr, cv=kf, scoring="r2")
        cv_res[name] = (cv.mean(), cv.std())
        model.fit(X_tr, y_tr)
        test_pred[name] = model.predict(X_te)
        test_res[name] = metrics(y_te, test_pred[name])
        r = test_res[name]
        print(f"[{name:18s}] CV R2: {cv.mean():.3f} ± {cv.std():.3f} | Test: MAE {r['MAE']:,.0f} | "
              f"RMSE {r['RMSE']:,.0f} | R2 {r['R2']:.3f} | MAPE {r['MAPE']:.1f}%")

    best = max(cv_res, key=lambda k: cv_res[k][0])
    r = test_res[best]
    print(f"\n=> Mô hình được chọn (CV R2 cao nhất): {best}")

    # Bảng so sánh 3 mô hình + số liệu điền báo cáo
    bang = [{"Mo_hinh": n, "CV_R2": cv_res[n][0], "CV_R2_std": cv_res[n][1], **test_res[n]} for n in test_res]
    pd.DataFrame(bang).round(3).to_csv(MODEL_DIR / "model_metrics.csv", index=False, encoding="utf-8-sig")

    thieu = (df[features].isna().mean() * 100).round(1)
    thieu = thieu[thieu > 0].sort_values(ascending=False)
    dong = [
        "=== SỐ LIỆU CHO BÁO CÁO ===",
        f"File dữ liệu: {CSV_PATH.name}",
        f"Số máy dùng để huấn luyện và kiểm thử: {len(df)} (huấn luyện {len(X_tr)} | kiểm thử {len(X_te)})",
        f"Số hãng: {df['Hang'].nunique()}",
        f"Khoảng giá: {y.min():,.0f} - {y.max():,.0f} VNĐ quy đổi (giá BDT x {TY_GIA_BDT_VND})",
        "Tỉ lệ thiếu theo cột (%): " + (", ".join(f"{k} {v}" for k, v in thieu.items()) or "không có"),
        f"Mô hình được chọn: {best}",
        f"  CV R2 = {cv_res[best][0]:.3f} ± {cv_res[best][1]:.3f}",
        f"  Test: R2 = {r['R2']:.3f} | MAE = {r['MAE']:,.0f} | RMSE = {r['RMSE']:,.0f} | MAPE = {r['MAPE']:.1f}%",
        f"  RMSE / MAE = {r['RMSE'] / r['MAE']:.2f}",
    ]
    (MODEL_DIR / "report_numbers.txt").write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n" + "\n".join(dong) + "\n")

    # Huấn luyện lại trên TOÀN BỘ dữ liệu rồi mới xuất .pkl cho nhóm Web
    joblib.dump(clone(models[best]).fit(X, y), MODEL_PATH)

    vc = {c: df[c].dropna().astype(str).value_counts() for c in CAT_COLS}
    meta = {
        "model_name": best,
        "sklearn_version": sklearn.__version__,
        "target": TARGET,
        "unit": "VND",
        "currency_note": f"Giá bán tại Bangladesh (BDT) quy đổi sang VNĐ, 1 BDT = {TY_GIA_BDT_VND} VNĐ. "
                         "Không phải giá bán tại Việt Nam.",
        "features": features,
        "numeric_features": NUM_COLS,
        "categorical_features": CAT_COLS,
        "labels": {c: LABELS[c] for c in features},
        "choices": {c: sorted(v[v >= MIN_CAT_COUNT].index.tolist() or v.index.tolist()) for c, v in vc.items()},
        "defaults": {**{c: float(df[c].median()) for c in NUM_COLS},
                     **{c: str(df[c].mode().iloc[0]) for c in CAT_COLS}},
        "numeric_ranges": {c: {"min": float(df[c].min()), "p01": float(lo[i]), "median": float(df[c].median()),
                               "p99": float(hi[i]), "max": float(df[c].max())}
                           for i, c in enumerate(NUM_COLS)},
        "price_range": {"min": float(y.min()), "max": float(y.max())},
        "metrics_test": r,
        "cv_r2": {"mean": cv_res[best][0], "std": cv_res[best][1]},
        "note": "Web nên ép kết quả predict() vào khoảng price_range và gửi số bằng pd.to_numeric.",
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    save_plots(y_te, test_pred[best], best, models[best], test_res)

    print(f"Đã xuất: {MODEL_PATH.name}, {META_PATH.name}, model_metrics.csv, report_numbers.txt, "
          f"3 biểu đồ trong figures/")
    print("Hoàn tất. Chạy tiếp: python src/test_model.py")


if __name__ == "__main__":
    main()
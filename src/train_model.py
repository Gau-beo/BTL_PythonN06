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

# ----------------------------------------------------------------------------
# CẤU HÌNH
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CSV_CANDIDATES = [ROOT / "data" / "data_clean.csv", ROOT / "data" / "sample.csv"]
MODEL_PATH = ROOT / "src" / "phone_price_model.pkl"
META_PATH = ROOT / "src" / "model_meta.json"
FIG_DIR = ROOT / "figures"

TARGET = "Gia_ban"
MIN_PRICE = 100_000        # giá nhỏ hơn mức này coi là dữ liệu lỗi và loại bỏ
MAX_PRICE = 150_000_000    # giá lớn hơn mức này (150 triệu) coi là dữ liệu lỗi và loại bỏ
MIN_CAT_COUNT = 5          # giá trị chữ xuất hiện < 5 lần (vd hãng hiếm) gộp vào nhóm "hiếm"
CLIP_Q = (0.01, 0.99)      # cắt giá trị số ngoại lai về khoảng phân vị 1%-99%

NUM_COLS = [
    "RAM", "ROM", "Ho_tro_5G", "Kich_thuoc_man", "Tan_so_quet", "Do_sang_nits",
    "Cam_sau_MP", "Cam_truoc_MP", "Khoi_luong", "Pin_mAh", "Sac_W",
]
CAT_COLS = ["Hang", "Chipset_dong", "Tam_nen", "Do_phan_giai", "Khang_nuoc_bui"]

LABELS = {
    "RAM": "RAM (GB)", "ROM": "Bộ nhớ trong (GB)", "Ho_tro_5G": "Hỗ trợ 5G (1 = có, 0 = không)",
    "Kich_thuoc_man": "Kích thước màn hình (inch)", "Tan_so_quet": "Tần số quét (Hz)",
    "Do_sang_nits": "Độ sáng (nits)", "Cam_sau_MP": "Camera sau (MP)",
    "Cam_truoc_MP": "Camera trước (MP)", "Khoi_luong": "Khối lượng (g)",
    "Pin_mAh": "Dung lượng pin (mAh)", "Sac_W": "Công suất sạc (W)",
    "Hang": "Hãng", "Chipset_dong": "Dòng chip", "Tam_nen": "Loại màn hình",
    "Do_phan_giai": "Độ phân giải", "Khang_nuoc_bui": "Chuẩn kháng nước/bụi",
}


# ----------------------------------------------------------------------------
# LÀM SẠCH + TẠO ĐẶC TRƯNG
# ----------------------------------------------------------------------------
def find_csv():
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if not p.exists():
            sys.exit(f"[LỖI] Không tìm thấy file: {p}")
        return p
    primary, sample = CSV_CANDIDATES
    if primary.exists():
        return primary
    if sample.exists():
        print("[CẢNH BÁO] Không có data/data_clean.csv; đang dùng data/sample.csv. "
              "Chỉ nên dùng để thử chương trình, không dùng làm kết quả huấn luyện chính thức.")
        return sample
    sys.exit("[LỖI] Không tìm thấy data/data_clean.csv hoặc data/sample.csv.")


def extract_pin_mah(s):
    m = re.search(r"(\d{3,5})\s*mAh", str(s), re.IGNORECASE)
    return float(m.group(1)) if m else np.nan


def extract_sac_w(s):
    m = re.search(r"(\d+(?:\.\d+)?)\s*W\b", str(s), re.IGNORECASE)
    return float(m.group(1)) if m else np.nan


def group_chipset(s):
    t = str(s).lower()
    if t in ("nan", "none", ""):
        return "Khac"
    if "snapdragon" in t:
        m = re.search(r"snapdragon\s*(\d)", t)
        return f"Snapdragon {m.group(1)}" if m else "Snapdragon"
    if "dimensity" in t:
        m = re.search(r"dimensity\s*(\d)", t)
        return "Dimensity 9000" if (m and m.group(1) == "9") else "Dimensity"
    if "helio" in t:
        return "Helio"
    if "apple" in t or re.search(r"\ba\d{2}\b", t) or "bionic" in t:
        return "Apple A"
    if "exynos" in t:
        return "Exynos"
    if "tensor" in t:
        return "Tensor"
    if "kirin" in t:
        return "Kirin"
    if "unisoc" in t or "tiger" in t:
        return "Unisoc"
    return "Khac"


def clean_tam_nen(s):
    t = str(s).upper()
    if "AMOLED" in t:
        return "AMOLED"
    if "OLED" in t or "SUPER RETINA" in t:
        return "OLED"
    if "IPS" in t or "LCD" in t:
        return "IPS LCD"
    return "Khac"


def clean_khang_nuoc(s):
    m = re.search(r"IP\s?(\d{2})", str(s), re.IGNORECASE)
    return f"IP{m.group(1)}" if m else "Khong"


def to_5g(v):
    t = str(v).strip().lower()
    if t in ("1", "1.0", "true", "co", "có", "yes", "5g"):
        return 1.0
    if t in ("0", "0.0", "false", "khong", "không", "no", ""):
        return 0.0
    if "5g" in t:
        return 1.0
    return np.nan


def group_do_phan_giai(s):
    """Gom '1080 x 2400 pixels ... (~395 ppi density)' về HD+ / FHD+ / 2K+ để dropdown gọn."""
    t = str(s)
    m = re.search(r"(\d{3,4})\s*x\s*(\d{3,4})", t)
    if m:
        short = min(int(m.group(1)), int(m.group(2)))
        if short <= 800:
            return "HD+"
        if short <= 1300:
            return "FHD+"
        return "2K+"
    tl = t.lower()
    if "2k" in tl or "qhd" in tl:
        return "2K+"
    if "full" in tl or "fhd" in tl:
        return "FHD+"
    if "hd" in tl:
        return "HD+"
    return "Khac"


def normalize_hang(series):
    """Gộp 'HONOR'/'Honor'/'honor' về 1 cách viết (cách viết phổ biến nhất)."""
    s = series.astype(str).str.strip()
    key = s.str.lower()
    canon = s.groupby(key).agg(lambda x: x.value_counts().index[0])
    return key.map(canon)


def load_and_engineer_data(path):
    df = pd.read_csv(path, na_values=["N/a", "N/A", "n/a", "nan", "NaN", ""])
    df.columns = [c.strip() for c in df.columns]

    if TARGET not in df.columns:
        sys.exit(f"[LỖI] File csv không có cột nhãn '{TARGET}'. Các cột hiện có: {list(df.columns)}")

    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df = df[np.isfinite(df[TARGET])]
    out = (df[TARGET] < MIN_PRICE) | (df[TARGET] > MAX_PRICE)
    bad = df[out]
    if len(bad):
        print(f"[CẢNH BÁO] Loại {len(bad)} dòng có giá ngoài khoảng {MIN_PRICE:,} - {MAX_PRICE:,} VNĐ (nghi lỗi dữ liệu):")
        cols = [c for c in ("Ten_may", "Hang", TARGET) if c in bad.columns]
        with pd.option_context("display.float_format", "{:,.0f}".format, "display.max_colwidth", 60):
            print(bad[cols].head(15).to_string())
    df = df[~out].reset_index(drop=True)

    if "Cong_nghe_pin" in df.columns:
        if "Pin_mAh" not in df.columns:
            df["Pin_mAh"] = df["Cong_nghe_pin"].apply(extract_pin_mah)
        if "Sac_W" not in df.columns:
            df["Sac_W"] = df["Cong_nghe_pin"].apply(extract_sac_w)

    if "Chipset" in df.columns:
        df["Chipset_dong"] = df["Chipset"].apply(group_chipset)
    if "Tam_nen" in df.columns:
        df["Tam_nen"] = df["Tam_nen"].apply(clean_tam_nen)
    if "Khang_nuoc_bui" in df.columns:
        df["Khang_nuoc_bui"] = df["Khang_nuoc_bui"].apply(clean_khang_nuoc)
    if "Ho_tro_5G" in df.columns:
        df["Ho_tro_5G"] = df["Ho_tro_5G"].apply(to_5g)
    if "Hang" in df.columns:
        df["Hang"] = normalize_hang(df["Hang"])
    if "Do_phan_giai" in df.columns:
        df["Do_phan_giai"] = df["Do_phan_giai"].apply(group_do_phan_giai)

    for c in NUM_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # RAM thiếu của iPhone: ƯỚC LƯỢNG (Pro 12GB, còn lại 8GB) - cần ghi chú trong báo cáo
    if "RAM" in df.columns and "Hang" in df.columns:
        mask = df["RAM"].isna() & df["Hang"].str.lower().eq("apple")
        ten = df["Ten_may"].astype(str).str.lower() if "Ten_may" in df.columns else pd.Series("", index=df.index)
        df.loc[mask, "RAM"] = np.where(ten.str.contains("pro"), 12, 8)[mask.values]

    return df


def select_columns(df):
    num_cols, cat_cols = [], []
    for c in NUM_COLS:
        if c not in df.columns:
            print(f"  [CẢNH BÁO] Thiếu cột số '{c}' -> bỏ qua")
        elif df[c].notna().sum() == 0:
            print(f"  [CẢNH BÁO] Cột '{c}' toàn rỗng -> bỏ qua")
        else:
            num_cols.append(c)
    for c in CAT_COLS:
        if c not in df.columns:
            print(f"  [CẢNH BÁO] Thiếu cột chữ '{c}' -> bỏ qua")
        elif df[c].notna().sum() == 0:
            print(f"  [CẢNH BÁO] Cột '{c}' toàn rỗng -> bỏ qua")
        else:
            cat_cols.append(c)
    if not num_cols and not cat_cols:
        sys.exit("[LỖI] Không còn feature nào để huấn luyện.")
    return num_cols, cat_cols


def print_data_report(df, num_cols, cat_cols):
    q = df[TARGET].quantile([0, 0.01, 0.5, 0.99, 1])
    print("\n--- KIỂM TRA DỮ LIỆU ---")
    print("Giá (VNĐ): min {:,.0f} | p1 {:,.0f} | median {:,.0f} | p99 {:,.0f} | max {:,.0f}".format(*q.values))
    print(df[num_cols].describe().loc[["min", "50%", "max"]].round(1).to_string())
    if "Hang" in cat_cols:
        vc = df["Hang"].value_counts()
        print(f"Hãng: {len(vc)} giá trị, {int((vc >= MIN_CAT_COUNT).sum())} hãng có >= {MIN_CAT_COUNT} máy. "
              f"Top: {dict(vc.head(8))}")


# ----------------------------------------------------------------------------
# MÔ HÌNH
# ----------------------------------------------------------------------------
def build_preprocess(num_cols, cat_cols, lo, hi):
    num = Pipeline([
        # cắt ngoại lai (np.clip là hàm chuẩn của numpy nên .pkl không phụ thuộc code của nhóm)
        ("clip", FunctionTransformer(np.clip, kw_args={"a_min": lo, "a_max": hi},
                                     feature_names_out="one-to-one")),
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
    ])
    cat = Pipeline([
        ("imp", SimpleImputer(strategy="constant", fill_value="Khac")),
        # hãng hiếm và hãng chưa từng thấy đều rơi vào nhóm "hiếm" thay vì ngoại suy bậy
        ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=MIN_CAT_COUNT)),
    ])
    return ColumnTransformer([("num", num, num_cols), ("cat", cat, cat_cols)])


def make_model(estimator, num_cols, cat_cols, lo, hi):
    return TransformedTargetRegressor(
        regressor=Pipeline([("prep", build_preprocess(num_cols, cat_cols, lo, hi)), ("model", estimator)]),
        func=np.log1p,
        inverse_func=np.expm1,
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


def make_choices(df, cat_cols):
    ch = {}
    for c in cat_cols:
        vc = df[c].dropna().astype(str).value_counts()
        keep = vc[vc >= MIN_CAT_COUNT].index.tolist() or vc.index.tolist()
        ch[c] = sorted(keep)
    return ch


def make_defaults(df, num_cols, cat_cols):
    d = {c: float(df[c].median()) for c in num_cols}
    d.update({c: str(df[c].mode().iloc[0]) for c in cat_cols})
    return d


def sanity_check(model, defaults, choices, features, num_cols, p_min, p_max):
    """Kiểm tra nhanh các đầu vào đại diện; không thay thế đánh giá trên tập test."""
    rows, tags = [], []

    # Bộ thông số mặc định cho từng hãng trong danh sách dropdown.
    for h in choices.get("Hang", [None]):
        row = dict(defaults)
        if h is not None:
            row["Hang"] = h
        rows.append(row)
        tags.append(f"Hãng: {h}" if h is not None else "Máy mặc định")

    # Đầu vào thiếu hoàn toàn.
    rows.append({c: np.nan for c in features})
    tags.append("(ô rỗng)")

    # Hãng lạ và giá trị số cực đoan; pipeline cần xử lý mà không làm giá vọt bất thường.
    if "Hang" in features:
        row = dict(defaults)
        row["Hang"] = "HangLa_ChuaTungThay"
        rows.append(row)
        tags.append("(hãng lạ)")

    row = dict(defaults)
    for c in num_cols:
        row[c] = 1e9
    rows.append(row)
    tags.append("(số liệu cực đoan)")

    preds = model.predict(pd.DataFrame(rows, columns=features))
    lo, hi = p_min * 0.5, p_max * 2
    return [(tag, float(pred)) for tag, pred in zip(tags, preds)
            if not (np.isfinite(pred) and lo <= pred <= hi)]


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    FIG_DIR.mkdir(exist_ok=True)
    MODEL_PATH.parent.mkdir(exist_ok=True)

    csv_path = find_csv()
    print(f"Đọc dữ liệu: {csv_path}")
    df = load_and_engineer_data(csv_path)
    print(f"Số dòng hợp lệ: {len(df)}")
    if len(df) < 20:
        sys.exit("[LỖI] Quá ít dữ liệu (<20 dòng) để huấn luyện.")

    num_cols, cat_cols = select_columns(df)
    features = num_cols + cat_cols
    print(f"Feature số  ({len(num_cols)}): {num_cols}")
    print(f"Feature chữ ({len(cat_cols)}): {cat_cols}")
    print_data_report(df, num_cols, cat_cols)

    qs = df[num_cols].quantile(list(CLIP_Q))
    lo, hi = qs.loc[CLIP_Q[0]].values, qs.loc[CLIP_Q[1]].values

    X, y = df[features], df[TARGET].astype(float)
    p_min, p_max = float(y.min()), float(y.max())
    choices = make_choices(df, cat_cols)
    defaults = make_defaults(df, num_cols, cat_cols)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    estimators = {
        "Ridge Regression": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }
    models = {n: make_model(e, num_cols, cat_cols, lo, hi) for n, e in estimators.items()}

    n_splits = max(2, min(5, len(X_tr) // 5))
    kf = KFold(n_splits, shuffle=True, random_state=42)
    cv_res, test_res, test_pred, sane = {}, {}, {}, {}

    print("\n--- HUẤN LUYỆN VÀ ĐÁNH GIÁ ---")
    for name, model in models.items():
        cv = cross_val_score(model, X_tr, y_tr, cv=kf, scoring="r2")
        cv_res[name] = (cv.mean(), cv.std())
        model.fit(X_tr, y_tr)
        test_pred[name] = model.predict(X_te)
        test_res[name] = metrics(y_te, test_pred[name])
        bad = sanity_check(model, defaults, choices, features, num_cols, p_min, p_max)
        sane[name] = not bad
        r = test_res[name]
        print(f"[{name:18s}] CV R2: {cv.mean():.3f} ± {cv.std():.3f} | Test: MAE {r['MAE']:,.0f} VNĐ | "
              f"RMSE {r['RMSE']:,.0f} | R2 {r['R2']:.3f} | MAPE {r['MAPE']:.1f}% | "
              f"Kiểm tra hợp lý: {'ĐẠT' if not bad else 'KHÔNG ĐẠT'}")
        for tag, p in bad[:5]:
            print(f"      ! dự đoán bất thường cho {tag}: {p:,.0f} VNĐ")

    ranking = sorted(cv_res, key=lambda k: cv_res[k][0], reverse=True)
    best = next((n for n in ranking if sane[n]), None)
    if best is None:
        best = "Random Forest"
        print("[CẢNH BÁO] Không mô hình nào qua kiểm tra hợp lý -> dùng Random Forest (dự đoán luôn nằm trong khoảng giá đã học)")
    elif best != ranking[0]:
        print(f"[CẢNH BÁO] {ranking[0]} có CV R2 cao nhất nhưng dự đoán bất thường nên bị loại.")
    print(f"\n=> Mô hình được chọn: {best}")

    # Lưu bảng so sánh các mô hình để đưa vào báo cáo
    bang = [{"Mo_hinh": n, "CV_R2": cv_res[n][0], "CV_R2_std": cv_res[n][1], **test_res[n]} for n in test_res]
    pd.DataFrame(bang).round(3).to_csv(ROOT / "src" / "model_metrics.csv", index=False, encoding="utf-8-sig")

    final_model = clone(models[best]).fit(X, y)
    joblib.dump(final_model, MODEL_PATH)
    print(f"Đã xuất mô hình: {MODEL_PATH}")

    meta = {
        "model_name": best,
        "sklearn_version": sklearn.__version__,
        "target": TARGET,
        "unit": "VND",
        "features": features,
        "numeric_features": num_cols,
        "categorical_features": cat_cols,
        "labels": {c: LABELS.get(c, c) for c in features},
        "choices": choices,
        "defaults": defaults,
        "numeric_ranges": {c: {"min": float(df[c].min()), "p01": float(lo[i]), "median": float(df[c].median()),
                               "p99": float(hi[i]), "max": float(df[c].max())}
                           for i, c in enumerate(num_cols)},
        "price_range": {"min": p_min, "max": p_max},
        "metrics_test": test_res[best],
        "cv_r2": {"mean": cv_res[best][0], "std": cv_res[best][1]},
        "note": "Web nên ép kết quả predict() vào khoảng price_range và gửi số bằng pd.to_numeric.",
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Đã xuất metadata: {META_PATH}")

    # --- BIỂU ĐỒ ---
    pred_best = test_pred[best]
    plt.figure(figsize=(6, 6))
    plt.scatter(y_te / 1e6, pred_best / 1e6, alpha=0.7, color="teal")
    lim = [0, max(y_te.max(), pred_best.max()) / 1e6]
    plt.plot(lim, lim, "r--", label="Đường chuẩn lý tưởng")
    plt.xlabel("Giá thực tế (triệu VNĐ)")
    plt.ylabel("Giá dự đoán (triệu VNĐ)")
    plt.title(f"Thực tế vs Dự đoán ({best})")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "gia_thuc_te_vs_du_doan.png", dpi=150)
    plt.close()

    imp, xlabel = feature_importance(models[best])
    plt.figure(figsize=(9, 5))
    imp[::-1].plot(kind="barh", color="coral")
    plt.title(f"Top 10 đặc trưng ảnh hưởng giá nhất ({best})")
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "do_quan_trong_dac_trung.png", dpi=150)
    plt.close()

    names = list(test_res.keys())
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

    print(f"Đã lưu 3 biểu đồ vào: {FIG_DIR}")

    # requirements.txt được quản lý riêng, tránh tự ghi đè khi huấn luyện mô hình.
    print("\nHoàn tất. Chạy tiếp: python src/test_model.py")


if __name__ == "__main__":
    main()
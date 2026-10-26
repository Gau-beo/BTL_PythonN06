import argparse
from pathlib import Path

import pandas as pd

THUOC_TINH = [
    "Gia_ban",
    "RAM",
    "ROM",
    "Kich_thuoc_man",
    "Dung_luong_pin",
    "Cong_suat_sac_W",
    "Tan_so_quet_Hz",
    "Cam_sau_MP",
    "Cam_truoc_MP",
    "Khoi_luong",
]
THU_MUC_DU_AN = Path(__file__).resolve().parents[1]
FILE_DU_LIEU = THU_MUC_DU_AN / "data" / "data_clean.csv"
THU_MUC_KET_QUA = THU_MUC_DU_AN / "data"


def doc_du_lieu(duong_dan: Path) -> pd.DataFrame:
    du_lieu = pd.read_csv(duong_dan, encoding="utf-8-sig", na_values=["N/a"])

    for ten_cot in ["Ten_may", "Hang"]:
        du_lieu[ten_cot] = du_lieu[ten_cot].astype("string").str.strip()

    for thuoc_tinh in THUOC_TINH:
        du_lieu[thuoc_tinh] = pd.to_numeric(du_lieu[thuoc_tinh])

    return du_lieu


def tinh_thong_ke(du_lieu: pd.DataFrame) -> pd.DataFrame:
    # Nhóm đầu tiên chứa tất cả điện thoại; các nhóm sau là từng hãng.
    cac_nhom = [("all", du_lieu)]
    for ten_hang, du_lieu_cua_hang in du_lieu.groupby("Hang", sort=True):
        cac_nhom.append((ten_hang, du_lieu_cua_hang))

    ket_qua = []
    for ten_hang, du_lieu_nhom in cac_nhom:
        dong_thong_ke = {"Hang": ten_hang}

        for thuoc_tinh in THUOC_TINH:
            gia_tri = du_lieu_nhom[thuoc_tinh]
            dong_thong_ke[f"Median_{thuoc_tinh}"] = gia_tri.median()
            dong_thong_ke[f"Mean_{thuoc_tinh}"] = gia_tri.mean()
            dong_thong_ke[f"Std_{thuoc_tinh}"] = gia_tri.std(ddof=1)

        ket_qua.append(dong_thong_ke)

    bang_thong_ke = pd.DataFrame(ket_qua)
    bang_thong_ke.insert(0, "STT", range(len(bang_thong_ke)))
    return bang_thong_ke


def tim_top_bottom(du_lieu: pd.DataFrame) -> pd.DataFrame:

    ket_qua = []
    cach_xep_hang = [("Cao_nhat", False), ("Thap_nhat", True)]

    for thuoc_tinh in THUOC_TINH:
        # Chỉ xếp hạng những máy có giá trị của thuộc tính đang xét.
        du_lieu_hop_le = du_lieu.dropna(subset=[thuoc_tinh])

        for ten_nhom, sap_xep_tang_dan in cach_xep_hang:
            du_lieu_sap_xep = du_lieu_hop_le.sort_values(
                [thuoc_tinh, "Ten_may", "Hang"],
                ascending=[sap_xep_tang_dan, True, True],
            )

            cac_may_khac_nhau = du_lieu_sap_xep.drop_duplicates(
                subset=["Ten_may", "Hang"]
            )
            ba_may_dau = cac_may_khac_nhau.head(3)
            danh_sach_may = ba_may_dau.to_dict("records")

            for thu_hang, thong_tin_may in enumerate(danh_sach_may, start=1):
                ket_qua.append({
                    "Thuoc_tinh": thuoc_tinh,
                    "Nhom": ten_nhom,
                    "Thu_hang": thu_hang,
                    "Ten_may": thong_tin_may["Ten_may"],
                    "Hang": thong_tin_may["Hang"],
                    "Gia_tri": thong_tin_may[thuoc_tinh],
                })

    return pd.DataFrame(ket_qua, columns=[
        "Thuoc_tinh", "Nhom", "Thu_hang", "Ten_may", "Hang", "Gia_tri"
    ])


if __name__ == "__main__":
    # 1. Lấy đường dẫn file đầu vào và thư mục đầu ra từ lệnh chạy.
    parser = argparse.ArgumentParser(
        description="Tim Top/Bottom 3 va tinh Median, Mean, Std theo hang dien thoai."
    )
    parser.add_argument(
        "input_csv", type=Path, nargs="?", default=FILE_DU_LIEU,
        help="Duong dan CSV dau vao; mac dinh: data/data_clean.csv.",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=THU_MUC_KET_QUA,
        help="Thu muc luu results2.csv va top_bottom3.csv.",
    )
    tham_so = parser.parse_args()

    # 2. Đọc dữ liệu và tính hai bảng kết quả.
    du_lieu = doc_du_lieu(tham_so.input_csv)
    bang_thong_ke = tinh_thong_ke(du_lieu)
    bang_top_bottom = tim_top_bottom(du_lieu)

    # 3. Lưu mỗi bảng vào một file CSV.
    thu_muc_ket_qua = tham_so.output_dir
    thu_muc_ket_qua.mkdir(parents=True, exist_ok=True)
    cac_file_ket_qua = [
        ("results2.csv", bang_thong_ke),
        ("top_bottom3.csv", bang_top_bottom),
    ]

    for ten_file, bang_ket_qua in cac_file_ket_qua:
        duong_dan = thu_muc_ket_qua / ten_file
        bang_ket_qua.to_csv(
            duong_dan, index=False, encoding="utf-8-sig", float_format="%.10g"
        )
        print(f"Da luu {duong_dan.resolve()}")

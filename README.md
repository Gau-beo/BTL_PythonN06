# BTL Python: Phân tích dữ liệu và ước lượng giá điện thoại (Nhóm 06)

BTL thu thập dữ liệu điện thoại từ MobileDokan, làm thống kê, vẽ histogram, phân cụm (K-means + PCA), vẽ radar, ước lượng giá và có một trang web Streamlit để trình bày kết quả. Hạn nộp: 30/10/2026.

## Cấu trúc thư mục

| Thư mục / file | Nội dung |
|---|---|
| `data/` | `phones.csv` (dữ liệu thô), `data_clean.csv` (đã làm sạch), `results2.csv`, `top_bottom3.csv`, `hang_dan_dau.csv`, `phones_kmeans.csv` |
| `src/` | Toàn bộ mã Python (xem bảng "Cách chạy") |
| `figures/` | Biểu đồ: `histogram/`, `elbow.png`, `silhouette.png`, `kmeans_pca.png`, `radar_chart.png`, `radar_2may.png`, ... |
| `models/` | `phone_price_model.pkl`, `model_meta.json`, `model_metrics.csv`, `report_numbers.txt`, `kmeans_pca.pkl` |
| `assets/phones/` | Ảnh điện thoại cho web |
| `app.py` | Trang web Streamlit (nằm ở thư mục gốc) |

## Quy ước dữ liệu (`data/data_clean.csv`: 1.050 dòng, 19 cột, 12 hãng)

Ô không có thông tin ghi `N/a` (theo đề). Khi đọc bằng pandas dùng `na_values=["N/a"]`.

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `Ten_may` | chuỗi | Tên máy (không trùng) |
| `Hang` | chuỗi | Hãng sản xuất |
| `Nam_ra_mat` | số nguyên | Năm ra mắt (2023-2026) |
| `Gia_ban` | số | Giá **quy đổi sang VNĐ** (giá BDT tại Bangladesh x 210), xem phần "Lưu ý về giá" |
| `He_dieu_hanh`, `Chipset` | chuỗi | Hệ điều hành, chip |
| `RAM`, `ROM` | số | GB |
| `Ho_tro_5G` | 0/1 | Hỗ trợ 5G |
| `Dung_luong_pin` | số | mAh |
| `Cong_suat_sac_W` | số | W |
| `Kich_thuoc_man` | số | inch |
| `Tan_so_quet_Hz` | số | Hz |
| `Tam_nen`, `Do_phan_giai` | chuỗi | Loại màn hình, độ phân giải |
| `Cam_sau_MP`, `Cam_truoc_MP` | số | Megapixel |
| `Khoi_luong` | số | gram |
| `URL` | chuỗi | Trang sản phẩm gốc |

Cần thêm/đổi cột thì nhắn trong nhóm trước, đừng tự đổi.

## Cài đặt

Yêu cầu Python 3.12.

```bash
python -m venv .venv
# Windows:  .\.venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

Mọi lệnh bên dưới chạy từ **thư mục gốc** dự án.

## Cách chạy (theo thứ tự các phần của đề)

| Bước | Lệnh | Kết quả |
|---|---|---|
| Thu thập (tuỳ chọn, cần mạng) | `python src/crawl_mobiledokan_requests.py` | `data/raw/phones_crawled.csv` |
| Bổ sung hãng thiếu | `python src/crawl_mobiledokan_requests.py --brands xiaomi --out data/raw/xiaomi.csv` rồi `python src/merge_phones.py data/raw/xiaomi.csv` | gộp vào `data/phones.csv` |
| Làm sạch | `python src/process.py` | `data/data_clean.csv` |
| Phần II: thống kê | `python src/thong_ke_dien_thoai.py` | `results2.csv`, `top_bottom3.csv`, `hang_dan_dau.csv` |
| Phần II: histogram | `python src/ve_histogram.py` | `figures/histogram/all/`, `figures/histogram/theo_hang/` |
| Phần III: chọn k | `python src/evaluate_clusters.py` | `figures/elbow.png`, `figures/silhouette.png` |
| Phần III: K-means + PCA | `python src/kmeans_pca.py --k 4` | `data/phones_kmeans.csv`, `figures/kmeans_pca.png` |
| Phần III: radar theo cụm | `python src/radar_chart.py` | `figures/radar_chart.png` |
| Phần III: radar 2 máy (theo đề) | `python src/radarChartPlot.py --p1 "Samsung Galaxy A36" --p2 "Oppo Reno13" --Attribute Gia_ban,RAM,ROM,Cam_sau_MP` | `figures/radar_2may.png` |
| Phần IV: huấn luyện mô hình giá | `python src/train_model.py` | `models/*`, 3 biểu đồ trong `figures/` |
| Phần IV: kiểm tra mô hình | `python src/test_model.py` | in kết quả kiểm tra |
| Web | `streamlit run app.py` | trang web |

### Kết quả hiện có

| File | Kích thước (không tính tiêu đề) |
|---|---|
| `results2.csv` | 13 dòng (`all` + 12 hãng) x 32 cột (STT, Hang + Median/Mean/Std của 10 thuộc tính) |
| `top_bottom3.csv` | 60 dòng (10 thuộc tính x cao nhất/thấp nhất x 3 máy) x 6 cột |
| `hang_dan_dau.csv` | 48 dòng: hãng dẫn đầu theo Mean và Median, có xử lý đồng hạng |

Mười thuộc tính thống kê: `Gia_ban`, `RAM`, `ROM`, `Kich_thuoc_man`, `Dung_luong_pin`, `Cong_suat_sac_W`, `Tan_so_quet_Hz`, `Cam_sau_MP`, `Cam_truoc_MP`, `Khoi_luong`. Ô thiếu được bỏ qua ở từng thuộc tính; độ lệch chuẩn mẫu dùng `ddof=1`.

### Chọn số cụm (k)

Silhouette khi chạy `evaluate_clusters.py`: k=2: 0,319; k=3: 0,306; **k=4: 0,326**; k=5: 0,263; k=6: 0,244; k=7: 0,243. Chọn k=4 vì silhouette cao nhất, nhưng chênh lệch với k=2 rất nhỏ nên nhận xét trong báo cáo cần nói rõ điều này. PCA 2 chiều giải thích 66,97% phương sai.

### Mô hình ước lượng giá

Gradient Boosting (chọn theo CV R2): CV R2 = 0,752 +- 0,087; trên tập kiểm thử R2 = 0,833, MAE ~ 2,25 triệu VNĐ, MAPE ~ 21,1%. Trang web "Ước lượng giá" nạp đúng mô hình này từ `models/`, nên số liệu web và báo cáo khớp nhau. Nếu `scikit-learn` trên máy khác phiên bản trong `requirements.txt`, hãy chạy lại `python src/train_model.py`.

## Lưu ý về dữ liệu và giá (nên ghi trong báo cáo)

- Nguồn là MobileDokan (Bangladesh). `Gia_ban` = giá BDT x 210, **không phải giá bán tại Việt Nam**.
- Một phần giá là loại "Expected" (giá dự kiến), chưa phải giá bán thật; có cả máy chưa phát hành.
- Giá lấy mức thấp nhất trong các phiên bản, còn RAM/ROM lấy từ phiên bản đầu tiên, nên một số máy có thể chưa khớp cấu hình.
- `phones.csv` hiện **không có Xiaomi/Poco/Redmi** do bản cào cũ giới hạn 3000 máy theo thứ tự URL. Xem cách bổ sung ở bảng "Cách chạy". Sau khi bổ sung cần chạy lại toàn bộ các bước từ `process.py`.

## Bản sửa kỹ thuật

Giữ nguyên 1.050 máy, không cào thêm. QuantileClipper học ngưỡng trong từng fold huấn luyện. Khi sao chép mô hình, giữ cả src/model_utils.py; app.py đã thiết lập đường dẫn nạp. Radar báo lỗi khi tên không duy nhất hoặc thiếu thông số. Trang phân cụm mặc định dùng 7 đặc trưng như script.

Trên Windows, chạy lệnh bằng `python -X utf8` để log tiếng Việt không lỗi mã hóa. Môi trường đã kiểm tra: Python 3.13, các phiên bản thư viện trong requirements.txt.

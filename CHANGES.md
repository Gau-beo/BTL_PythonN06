# Những thay đổi đã áp dụng cho bản này

## Sửa lỗi
- `app.py`: sửa `BASE_DIR` (trước đây trỏ ra ngoài repo nên không tìm thấy dữ liệu/ảnh); bỏ đường dẫn tới file không tồn tại; slider K mặc định 4; trang "Ước lượng giá" nạp mô hình `models/phone_price_model.pkl` thay vì tự huấn luyện RandomForest riêng.
- `src/train_model.py`, `src/test_model.py`: đọc/ghi trong `models/` (trước đây dùng `src/` nên `test_model.py` báo thiếu file).
- `src/ve_histogram.py`: đường dẫn mặc định đúng (`data/data_clean.csv`), chạy được từ thư mục gốc.
- `src/radar_chart.py`: đường dẫn mặc định đổi thành `data/phones_kmeans.csv`.
- `src/evaluate_clusters.py`: điền thiếu bằng trung vị (cùng cách với K-means), in kết quả WCSS/silhouette.
- `src/crawl_mobiledokan_requests.py`: bỏ giới hạn cứng 3000 máy (nguyên nhân thiếu Xiaomi); thêm `--brands`, `--limit`, `--out`; ghi vào `data/raw/` thay vì `src/outputs/`.

## Thêm mới
- `src/radarChartPlot.py`: radar so sánh hai máy đúng cú pháp đề (`--p1 --p2 --Attribute`).
- `src/merge_phones.py`: gộp dữ liệu cào bổ sung vào `data/phones.csv`.
- `src/kmeans-pca.py` đổi tên thành `src/kmeans_pca.py` (có thể import) và thêm tham số `--k`.
- `models/report_numbers.txt`: số liệu để điền báo cáo.

## Chạy lại để đồng bộ
- `data/phones_kmeans.csv` (nay 1050 dòng, 12 hãng, khớp `data_clean.csv`), `models/kmeans_pca.pkl`, `figures/kmeans_pca.png`, `elbow.png`, `silhouette.png`, `radar_chart.png`, `radar_2may.png`, `results2.csv`, `top_bottom3.csv`, `hang_dan_dau.csv`.
- `models/kmeans_pca.pkl` được tạo bằng scikit-learn 1.8.0; hãy chạy lại `python src/kmeans_pca.py` trên máy dùng đúng phiên bản trong `requirements.txt` cho đồng nhất.

## Chưa thể làm trong bản này
- Cào bổ sung Xiaomi (cần mạng): chạy lệnh trong README.
- Báo cáo `.docx`.
- Quyết định về dữ liệu giá "Expected" và các máy chưa phát hành.
- Chưa chạy thử `streamlit run app.py` (không có Streamlit trong môi trường kiểm tra); đã kiểm tra cú pháp và logic dự đoán giá riêng.

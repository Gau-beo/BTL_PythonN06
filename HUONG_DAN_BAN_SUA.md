# Bản sửa kỹ thuật cho Nhóm 06

Giữ nguyên dữ liệu 1.050 máy và tỷ giá 210. Không thu thập thêm dữ liệu.

## Những thay đổi chính

- Học ngưỡng chặn ngoại lệ bên trong từng tập huấn luyện bằng QuantileClipper. Không dùng thông tin từ tập kiểm thử để đặt ngưỡng.
- Huấn luyện lại ba mô hình và xuất lại mô hình, metadata, chỉ số, biểu đồ giá.
- Web chọn mặc định cùng bảy đặc trưng phân cụm như script và giữ dòng thiếu một phần thông số để điền trung vị.
- Radar báo lỗi khi tên máy chưa đủ cụ thể hoặc thiếu thuộc tính, tránh âm thầm chọn nhầm máy hay biến thông số thiếu thành 0.
- Sửa bảng chi tiết/so sánh để chuyển đổi dữ liệu hiển thị nhất quán.
- MAPE được mô tả là sai số trung bình trên tập kiểm thử, không phải khoảng tin cậy cho từng máy.

## Cách chạy

Giải nén, mở terminal tại thư mục chứa app.py:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Mô hình đã được huấn luyện và đóng gói. Giữ nguyên thư mục src, đặc biệt src/model_utils.py, để nạp mô hình. Nếu cần chạy lại:

```powershell
python -X utf8 src/process.py
python -X utf8 src/thong_ke_dien_thoai.py
python -X utf8 src/ve_histogram.py
python -X utf8 src/kmeans_pca.py --k 4
python -X utf8 src/evaluate_clusters.py
python -X utf8 src/train_model.py
python -X utf8 src/test_model.py
```

## Kết quả đã kiểm tra

- Làm sạch: 1.050 dòng, 19 cột; giá trị dữ liệu khớp bộ dữ liệu gốc.
- Thống kê và histogram: chạy thành công.
- K-means: 4 cụm; silhouette 0,326; PCA hai chiều giữ 66,97% phương sai.
- Gradient Boosting được chọn theo CV: CV R² 0,752 ± 0,087; kiểm thử R² 0,833; MAE 2.250.463 VNĐ quy đổi; RMSE 3.826.342; MAPE 21,1%.
- test_model.py: các kiểm tra đều đạt.
- Kiểm thử tự động bằng Streamlit AppTest: bảy trang và thao tác dự đoán giá. Đây là kiểm thử chức năng, chưa thay thế việc nhóm xem giao diện bằng trình duyệt và chụp ảnh báo cáo.

## Phần nhóm tiếp tục hoàn thiện

Điền ngày thu thập, nguồn tỷ giá, đóng góp thành viên và ảnh trải nghiệm. Dữ liệu vẫn có giá dự kiến và hạn chế khớp RAM/ROM với giá; cần trình bày trung thực trong báo cáo. Không cần cào thêm để sử dụng bản sửa này.

Báo cáo cập nhật đi kèm vẫn giữ các chú thích màu. Bố cục Word chưa được kiểm tra qua dựng trang vì môi trường thiếu LibreOffice; nhóm mở Word, cập nhật mục lục và kiểm tra ngắt trang trước khi nộp.

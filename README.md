# 📱 Dự án Phân tích dữ liệu & Ước lượng giá Điện thoại Thế Giới Di Động (Nhóm 06)

## 📂 Cấu trúc thư mục
* `/data`: Chứa dữ liệu thô cào từ web (`.csv`) và dữ liệu giả (Mock Data) để test.
* `/src`: Chứa mã nguồn Python, chia theo từng chức năng của các thành viên.
* `/figures`: Nơi lưu các biểu đồ (Histogram, Radar chart, v.v.) được xuất ra.

## ⚙️ Hợp đồng Dữ liệu (Data Schema) - BẮT BUỘC
Để đảm bảo code của 10 người khi ghép lại không bị lỗi, toàn bộ file `.csv` thật (đội Data) và file Mock Data (đội AI/Web) **bắt buộc** phải sử dụng đúng tên cột và kiểu dữ liệu sau:

1. `Ten_may` (String): Tên đầy đủ của điện thoại (VD: Samsung Galaxy S24 Ultra)
2. `Hang` (String): Hãng sản xuất (VD: Samsung, Apple, Xiaomi)
3. `Gia_ban` (Integer): Giá máy tính bằng VNĐ, viết liền không dấu phẩy (VD: 33990000)
4. `Man_hinh` (Float): Kích thước màn hình tính bằng inch (VD: 6.8)
5. `RAM` (Integer): Dung lượng RAM tính bằng GB (VD: 12)
6. `ROM` (Integer): Dung lượng bộ nhớ trong tính bằng GB (VD: 256)
7. `Pin` (Integer): Dung lượng pin tính bằng mAh (VD: 5000)

## 🚦 Quy tắc làm việc nhóm (GitHub Workflow)
1. **Luôn PULL trước khi bắt đầu:** Mở GitHub Desktop và bấm `Fetch origin` -> `Pull origin` để lấy code mới nhất của người khác về trước khi code.
2. **Không sửa file của người khác:** Mỗi người chỉ làm việc trên file script của riêng mình trong thư mục `/src`.
3. **Commit rõ ràng:** Ghi chú rõ mình vừa làm gì trước khi nhấn `Commit to main`.
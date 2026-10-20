# BTL Python: Phân tích dữ liệu và ước lượng giá điện thoại (Nhóm 06)

Đây là BTL nhằm thu thập dữ liệu, làm thống kê, phân cụm, ước tính giá của các điện thoại thông minh và tạo một trang web nhỏ để trình bày kết quả. Ngày đến hạn là 30/10/2026.

## Cấu Trúc Thư Mục
- `data/`: Thư mục này sẽ chứa các tệp dữ liệu. Các tệp `.csv` từ trang web sẽ được lưu ở đây, các tệp HTML tải xuống sẽ được đặt trong `data/raw/` và `sample.csv` là tập dữ liệu giả để mọi người thực hành viết code trước khi nhận được dữ liệu thật.
- `src/`: Thư mục này sẽ chứa mã Python. Mỗi thành viên trong nhóm sẽ tạo riêng một tệp liên quan đến nhiệm vụ cụ thể của họ.
- `figures/`: Thư mục này sẽ chứa các biểu đồ được tạo ra (biểu đồ thanh,biểu đồ radar,...).

## Quy ước dữ liệu
Để code của mọi người ghép lại không bị lỗi, file dữ liệu thật và `sample.csv` dùng chung tên cột và kiểu dữ liệu dưới đây. Cần thêm hoặc đổi cột thì nhắn trong nhóm trước, đừng tự đổi.

### 1. Định danh & Phân loại
1. `Ten_may` (String): Tên đầy đủ của thiết bị (VD: Samsung Galaxy S24 Ultra).
2. `Hang` (String): Nhà sản xuất thiết bị (VD: Samsung, Apple, Xiaomi).
3. `Gia_ban` (Integer): Giá thiết bị tính bằng VNĐ, không chứa dấu phân cách (VD: 33990000).
4. `He_dieu_hanh` (String): Nền tảng hệ điều hành mặc định (VD: Android 14, iOS 17).

### 2. Cấu hình phần cứng
5. `Chipset` (String): Tên bộ vi xử lý (VD: Snapdragon 8 Gen 3).
6. `RAM` (Integer): Dung lượng bộ nhớ RAM tính bằng GB (VD: 12).
7. `ROM` (Integer): Dung lượng bộ nhớ trong tính bằng GB (VD: 256).
8. `Ho_tro_5G` (Integer): Trạng thái hỗ trợ mạng 5G (1: Có hỗ trợ, 0: Không hỗ trợ).
9. `Cong_nghe_pin` (String): Các công nghệ pin đi kèm (VD: Sạc nhanh 45W, Li-Po).

### 3. Màn hình hiển thị
10. `Kich_thuoc_man` (Float): Kích thước đường chéo màn hình tính bằng inch (VD: 6.8).
11. `Tam_nen` (String): Công nghệ tấm nền màn hình (VD: Dynamic AMOLED 2X, IPS LCD).
12. `Do_phan_giai` (String): Tiêu chuẩn độ phân giải (VD: 2K+, Full HD+).
13. `Do_sang_nits` (Integer): Độ sáng tối đa tính bằng nits (VD: 2600).

### 4. Hệ thống Camera
14. `Cam_sau_MP` (Float): Độ phân giải của camera chính phía sau tính bằng Megapixel (VD: 200.0).
15. `Cam_truoc_MP` (Float): Độ phân giải của camera selfie tính bằng Megapixel (VD: 12.0).

### 5. Thiết kế & Kết nối
16. `Kich_thuoc` (String): Kích thước tổng thể Dài x Ngang x Dày (VD: Dài 162.3 mm - Ngang 79 mm - Dày 8.6 mm).
17. `Khoi_luong` (Integer): Trọng lượng thiết bị tính bằng gram (VD: 232).
18. `Chat_lieu` (String): Vật liệu cấu thành (VD: Khung Titan & Mặt lưng kính cường lực).
19. `Khang_nuoc_bui` (String): Tiêu chuẩn bảo vệ (VD: IP68, IP54). Điền "Không" nếu không hỗ trợ.
20. `Cong_ket_noi` (String): Loại cổng sạc và trạng thái jack tai nghe (VD: Type-C, Không jack 3.5mm).

Lưu ý:
- Mỗi dòng là một phiên bản bộ nhớ cụ thể (ví dụ 12GB/256GB), tương ứng với một trang sản phẩm trên web.
- Ô nào không có thông tin thì ghi `N/a` (đề của cô yêu cầu vậy). Khi đọc file bằng pandas nhớ thêm `na_values=["N/a"]` để cột số không bị hiểu thành chữ.
- Đây là danh sách cột bản đầu. Khi thu thập xong, cần thiết sẽ bổ sung thêm cột (camera, sạc, tần số quét, ...) và cập nhật lại ở đây.

## Cách chạy

### Thống kê điện thoại trên nhánh `Thong_ke`

Yêu cầu Python 3.12. Các phiên bản thư viện đã kiểm tra được ghi trong
`requirements.txt` để các thành viên dùng cùng môi trường tính toán.

Tải đúng nhánh và mở thư mục dự án:

```bash
git clone --single-branch --branch Thong_ke https://github.com/Gau-beo/BTL_PythonN06.git
cd BTL_PythonN06
```

Trên Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/thong_ke_dien_thoai.py
```

Trên macOS/Linux, dùng Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/thong_ke_dien_thoai.py
```

Mã nguồn nằm trong `src/thong_ke_dien_thoai.py`. Chương trình mặc định đọc
`data/dien_thoai_viet_nam_1021.csv`, gồm 1.021 dòng, 20 cột và 13 hãng.
Đây là bản dữ liệu dùng để tạo kết quả thống kê đã đối chiếu; không tự ghép thêm
`data/MockData/results.csv` hoặc thay bằng `data/data_clean.csv` khi muốn tái tạo
cùng kết quả. Bản `data_clean.csv` hiện có 1.134 dòng và 21 cột, nên thống kê
trên bản đó sẽ khác.

Hai file kết quả được lưu trong `data/`:

| File | Nội dung | Kích thước, không tính dòng tiêu đề |
|---|---|---|
| `results2.csv` | Median, Mean, Std cho toàn bộ dữ liệu (`all`) và từng hãng | 14 dòng × 26 cột |
| `top_bottom3.csv` | 3 máy cao nhất và 3 máy thấp nhất cho mỗi thuộc tính | 48 dòng × 6 cột |

Tám thuộc tính được phân tích là `Gia_ban`, `RAM`, `ROM`, `Kich_thuoc_man`,
`Do_sang_nits`, `Cam_sau_MP`, `Cam_truoc_MP`, `Khoi_luong`. Ô thiếu được bỏ qua
ở từng thuộc tính; độ lệch chuẩn mẫu dùng `ddof=1`. Nếu bằng giá trị, Top 3
ưu tiên tên máy rồi hãng theo A–Z và lấy tối đa một dòng cho mỗi cặp tên máy/hãng.
Riêng bảng Median/Mean/Std tính trên toàn bộ các dòng quan sát trong CSV.

Cài thư viện cần kết nối mạng. Sau khi cài xong, phần thống kê chạy hoàn toàn
từ CSV đi kèm, không cần tải dữ liệu từ website hay truy cập đường dẫn cá nhân.

Có thể chỉ định CSV khác và thư mục xuất khác khi cần:

```powershell
.\.venv\Scripts\python.exe src/thong_ke_dien_thoai.py data/data_clean.csv -o data/thong_ke_du_lieu_sach
```

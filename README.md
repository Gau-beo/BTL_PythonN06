# BTL Python: Phân tích dữ liệu và ước lượng giá điện thoại (Nhóm 06)

Đây là BTL nhằm thu thập dữ liệu, làm thống kê, phân cụm, ước tính giá của các điện thoại thông minh và tạo một trang web nhỏ để trình bày kết quả. Ngày đến hạn là 30/10/2026.

## Cấu Trúc Thư Mục
- `data/`: Thư mục này sẽ chứa các tệp dữ liệu. Các tệp `.csv` từ trang web sẽ được lưu ở đây, các tệp HTML tải xuống sẽ được đặt trong `data/raw/` và `sample.csv` là tập dữ liệu giả để mọi người thực hành viết code trước khi nhận được dữ liệu thật.
- `src/`: Thư mục này sẽ chứa mã Python. Mỗi thành viên trong nhóm sẽ tạo riêng một tệp liên quan đến nhiệm vụ cụ thể của họ.
- `figures/`: Thư mục này sẽ chứa các biểu đồ được tạo ra (biểu đồ thanh,biểu đồ radar,...).

## Quy ước dữ liệu
Để code của mọi người ghép lại không bị lỗi, file dữ liệu thật và `sample.csv` dùng chung tên cột và kiểu dữ liệu dưới đây. Cần thêm hoặc đổi cột thì nhắn trong nhóm trước, đừng tự đổi.

1. `Ten_may` (string): Tên của thiết bị ví dụ như Samsung Galaxy S24 Ultra 12GB/256GB
2. `Hang` (string): Nhà sản xuất của thiết bị ví dụ như Samsung, Apple, Xiaomi
3. `Gia_ban` (integer): Giá tính bằng VND không có dấu chấm hoặc phẩy ví dụ như 33990000
4. `Man_hinh` (float): Kích thước màn hình tính bằng inch ví dụ như 6.8
5. `RAM` (integer): Dung lượng RAM tính bằng GB ví dụ như 12
6. `ROM` (integer): Dung lượng bộ nhớ trong tính bằng GB ví dụ như 256
7. `Pin` (integer): Dung lượng pin tính bằng mAh ví dụ như 5000

Vài lưu ý nhỏ:
- Mỗi dòng là một phiên bản bộ nhớ cụ thể (ví dụ 12GB/256GB), tương ứng với một trang sản phẩm trên web.
- Ô nào không có thông tin thì ghi `N/a` (đề của cô yêu cầu vậy). Khi đọc file bằng pandas nhớ thêm `na_values=["N/a"]` để cột số không bị hiểu thành chữ.
- Đây là danh sách cột bản đầu. Khi thu thập xong, cần thiết sẽ bổ sung thêm cột (camera, sạc, tần số quét, ...) và cập nhật lại ở đây.

## Cách chạy
Cài thư viện bằng `pip install -r requirements.txt` (file này sẽ được thêm sau). Hướng dẫn chạy từng phần sẽ cập nhật khi có code.
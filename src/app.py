
import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# 1. CAU HINH UNG DUNG
# =========================
st.set_page_config(
    page_title="Phân tích giá điện thoại - Nhóm 06",
    page_icon="📱",
    layout="wide"
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.csv"

st.title("📱 PHÂN TÍCH DỮ LIỆU VÀ ƯỚC LƯỢNG GIÁ ĐIỆN THOẠI")
st.caption("BTL Python - Nhóm 06 | Ứng dụng Streamlit")

# =========================
# 2. DOC DU LIEU
# =========================
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, na_values=["N/a"])

    if "Gia_ban" in df.columns:
        df["Gia_ban"] = pd.to_numeric(df["Gia_ban"], errors="coerce")

    for col in ["RAM", "ROM", "Ho_tro_5G"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


if not DATA_PATH.exists():
    st.error("Không tìm thấy data/sample.csv. Hãy kiểm tra thư mục data.")
    st.stop()

df = load_data(str(DATA_PATH))

# =========================
# 3. THANH DIEU HUONG
# =========================
st.sidebar.title("📌 Danh mục")
page = st.sidebar.radio(
    "Chọn chức năng",
    [
        "Tổng quan",
        "Dữ liệu điện thoại",
        "Phân tích thống kê",
        "Phân cụm K-means / PCA / Radar",
        "Ước lượng giá"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Nhóm 06 - BTL Python")
st.sidebar.caption("Lưu ý: đang sử dụng dữ liệu mẫu.")

# =========================
# 4. BO LOC DU LIEU
# =========================
st.sidebar.subheader("🔎 Bộ lọc")

filtered_df = df.copy()

if "Hang" in df.columns:
    brands = sorted(df["Hang"].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect(
        "Hãng điện thoại",
        brands,
        default=brands
    )
    filtered_df = filtered_df[filtered_df["Hang"].isin(selected_brands)]

if "RAM" in df.columns:
    ram_values = sorted(df["RAM"].dropna().unique().tolist())
    selected_ram = st.sidebar.multiselect(
        "RAM (GB)",
        ram_values,
        default=ram_values
    )
    filtered_df = filtered_df[filtered_df["RAM"].isin(selected_ram)]

if "ROM" in df.columns:
    rom_values = sorted(df["ROM"].dropna().unique().tolist())
    selected_rom = st.sidebar.multiselect(
        "ROM (GB)",
        rom_values,
        default=rom_values
    )
    filtered_df = filtered_df[filtered_df["ROM"].isin(selected_rom)]

if "Ho_tro_5G" in df.columns:
    selected_5g = st.sidebar.selectbox(
        "Hỗ trợ 5G",
        ["Tất cả", "Có", "Không"]
    )

    if selected_5g == "Có":
        filtered_df = filtered_df[filtered_df["Ho_tro_5G"] == 1]
    elif selected_5g == "Không":
        filtered_df = filtered_df[filtered_df["Ho_tro_5G"] == 0]

# =========================
# 5. TRANG TONG QUAN
# =========================
if page == "Tổng quan":
    st.subheader("📊 Tổng quan dữ liệu")

    col1, col2, col3 = st.columns(3)

    total_phones = (
        filtered_df["Ten_may"].nunique()
        if "Ten_may" in filtered_df.columns else len(filtered_df)
    )
    total_brands = (
        filtered_df["Hang"].nunique()
        if "Hang" in filtered_df.columns else 0
    )
    average_price = (
        filtered_df["Gia_ban"].mean()
        if "Gia_ban" in filtered_df.columns else None
    )

    col1.metric("Số điện thoại", f"{total_phones:,}")
    col2.metric("Số hãng", f"{total_brands:,}")
    col3.metric(
        "Giá bán trung bình",
        f"{average_price:,.0f} VNĐ" if pd.notna(average_price)
        else "Chưa có dữ liệu"
    )

    st.info("Các chỉ số trên thay đổi theo bộ lọc ở thanh bên.")

    st.subheader("📋 Một số điện thoại")
    st.dataframe(filtered_df.head(10), use_container_width=True)

    if "Gia_ban" in filtered_df.columns and "Ten_may" in filtered_df.columns:
        chart_data = (
            filtered_df.dropna(subset=["Gia_ban"])
            .groupby("Ten_may")["Gia_ban"]
            .mean()
            .sort_values(ascending=False)
        )

        if not chart_data.empty:
            st.subheader("💰 Giá bán theo điện thoại")
            st.bar_chart(chart_data)

# =========================
# 6. TRANG DU LIEU
# =========================
elif page == "Dữ liệu điện thoại":
    st.subheader("📋 Bảng dữ liệu điện thoại")
    st.write(f"Số dòng sau khi lọc: **{len(filtered_df)}**")
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Tải dữ liệu đang lọc (CSV)",
        data=csv_data,
        file_name="du_lieu_dien_thoai.csv",
        mime="text/csv"
    )

# =========================
# 7. TRANG PHAN TICH THONG KE
# =========================
elif page == "Phân tích thống kê":
    st.subheader("📈 Phân tích thống kê")

    if "Hang" in filtered_df.columns and "Gia_ban" in filtered_df.columns:
        brand_price = (
            filtered_df.dropna(subset=["Gia_ban"])
            .groupby("Hang")["Gia_ban"]
            .mean()
            .sort_values(ascending=False)
        )

        if not brand_price.empty:
            st.markdown("**Giá bán trung bình theo hãng (VNĐ)**")
            st.bar_chart(brand_price)

    if "Gia_ban" in filtered_df.columns:
        prices = filtered_df["Gia_ban"].dropna()

        if not prices.empty:
            st.markdown("**Phân bố giá bán**")
            st.bar_chart(
                prices.value_counts(bins=10, sort=False)
                .sort_index()
                .rename("Số điện thoại")
            )

    st.caption(
        "Các biểu đồ này được tạo trực tiếp từ dữ liệu hiện tại. "
        "Sẽ tích hợp thêm biểu đồ thống kê của các thành viên khi có kết quả."
    )

# =========================
# 8. TRANG K-MEANS / PCA / RADAR
# =========================
elif page == "Phân cụm K-means / PCA / Radar":
    st.subheader("🧩 Phân cụm điện thoại")

    st.warning(
        "Đây là khu vực chờ tích hợp kết quả K-means, PCA và biểu đồ radar "
        "từ thành viên phụ trách. Chưa có kết quả mô hình được nạp vào trang."
    )

    st.markdown("**Kết quả dự kiến hiển thị tại đây:**")
    st.write("- Nhãn cụm của từng điện thoại.")
    st.write("- Biểu đồ PCA thể hiện các cụm.")
    st.write("- Biểu đồ radar so sánh đặc điểm giữa các cụm.")

# =========================
# 9. TRANG UOC LUONG GIA
# =========================
elif page == "Ước lượng giá":
    st.subheader("💰 Ước lượng giá điện thoại")

    st.warning(
        "Chưa kết nối mô hình dự đoán giá. "
        "Cần tích hợp mô hình và các bước tiền xử lý do thành viên phụ trách cung cấp."
    )

    st.markdown("**Thông tin dự kiến dùng để ước lượng:**")
    st.write("- Hãng, chipset, RAM và ROM.")
    st.write("- Kích thước màn hình, camera và các thông số khác.")
    st.write("- Giá dự đoán từ mô hình đã huấn luyện.")

    st.info(
        "Không hiển thị giá dự đoán giả. Chức năng sẽ hoạt động "
        "khi nhóm cung cấp mô hình đã huấn luyện."
    )

# =========================
# 10. CHAN TRANG
# =========================
st.divider()
st.caption("BTL Python - Nhóm 06 | Phân tích dữ liệu và ước lượng giá điện thoại")


from pathlib import Path

import pandas as pd
import streamlit as st


# ==================== CẤU HÌNH ====================
st.set_page_config(
    page_title="Phone Analytics | Nhóm 06",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data_clean.csv"


# ==================== GIAO DIỆN ====================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    .stApp {
        background: #f5f7fb;
        color: #182230;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 247, 251, 0.88);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #101b2d;
        border-right: 1px solid #22304a;
    }

    section[data-testid="stSidebar"] * {
        color: #eef4ff;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #b8c5d9;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #1c2a40;
        border-color: #35455f;
    }

    section[data-testid="stSidebar"] input {
        color: #ffffff !important;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 2px 22px 2px;
    }

    .brand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        border-radius: 15px;
        background: linear-gradient(135deg, #5eead4, #60a5fa);
        color: #0b1a2b;
        font-size: 24px;
    }

    .brand-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 800;
        line-height: 1.3;
    }

    .brand-subtitle {
        color: #91a4bf;
        font-size: 11px;
        margin-top: 3px;
        letter-spacing: .8px;
        text-transform: uppercase;
    }

    .eyebrow {
        color: #0d9488;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 30px 34px;
        border-radius: 24px;
        background: linear-gradient(115deg, #10243d 0%, #173d60 56%, #087e8b 100%);
        color: #ffffff;
        margin-bottom: 26px;
        box-shadow: 0 16px 36px rgba(19, 50, 79, .15);
    }

    .hero h1 {
        color: #ffffff;
        font-size: clamp(27px, 3vw, 38px);
        font-weight: 800;
        letter-spacing: -1.1px;
        line-height: 1.2;
        margin: 0 0 12px 0;
    }

    .hero p {
        color: #d4e7f5;
        font-size: 14px;
        line-height: 1.7;
        max-width: 650px;
        margin: 0;
    }

    .hero-pill {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        background: rgba(255,255,255,.12);
        border: 1px solid rgba(255,255,255,.16);
        color: #d8fffa;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 19px;
        font-weight: 800;
        color: #152238;
        letter-spacing: -.35px;
        margin: 4px 0 3px 0;
    }

    .section-caption {
        font-size: 12px;
        color: #758197;
        margin-bottom: 15px;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e8edf5;
        border-radius: 18px;
        padding: 19px 20px;
        min-height: 125px;
        box-shadow: 0 5px 18px rgba(27, 45, 73, .035);
    }

    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #778399;
        margin-bottom: 13px;
    }

    .metric-value {
        font-size: clamp(22px, 2.2vw, 29px);
        font-weight: 800;
        color: #16263e;
        line-height: 1.2;
        letter-spacing: -.8px;
    }

    .metric-foot {
        font-size: 11px;
        color: #0d9488;
        margin-top: 9px;
        font-weight: 600;
    }

    .panel {
        background: #ffffff;
        border: 1px solid #e8edf5;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 5px 18px rgba(27, 45, 73, .035);
    }

    .small-note {
        color: #7c879b;
        font-size: 11px;
        line-height: 1.6;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e6ebf3;
        border-radius: 14px;
        overflow: hidden;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    hr {
        border-color: #e6ebf3;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== ĐỌC DỮ LIỆU ====================
@st.cache_data
def load_data(file_path, modified_time):
    data = pd.read_csv(
        file_path,
        na_values=["N/a", "N/A", "n/a", ""]
    )

    numeric_columns = [
        "Gia_ban",
        "RAM",
        "ROM",
        "Ho_tro_5G",
        "Kich_thuoc_man",
        "Do_sang_nits",
        "Cam_sau_MP",
        "Cam_truoc_MP",
        "Khoi_luong",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    return data


if not DATA_PATH.exists():
    st.error(f"Không tìm thấy dữ liệu tại: {DATA_PATH}")
    st.info("Hãy kiểm tra file data/sample.csv.")
    st.stop()

df = load_data(
    str(DATA_PATH),
    DATA_PATH.stat().st_mtime
)


# ==================== THANH BÊN ====================
with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-icon">📱</div>
            <div>
                <div class="brand-title">Phone Analytics</div>
                <div class="brand-subtitle">PROJECT · NHÓM 06</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### KHÔNG GIAN LÀM VIỆC")

    page = st.radio(
    "Điều hướng",
    [
        "Tổng quan",
        "Dữ liệu điện thoại",
        "Phân tích thống kê",
        "K-means / PCA / Radar",
        "Ước lượng giá",
    ],
    horizontal=True,
    label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("#### BỘ LỌC DỮ LIỆU")

    filtered = df.copy()

    if "Hang" in df.columns:
        brands = sorted(
            df["Hang"].dropna().astype(str).unique().tolist()
        )
        selected_brands = st.multiselect(
            "Hãng điện thoại", brands
        )

        if selected_brands:
            filtered = filtered[
                filtered["Hang"].astype(str).isin(selected_brands)
            ]

    if "RAM" in df.columns:
        ram_options = sorted(df["RAM"].dropna().unique().tolist())
        selected_ram = st.multiselect("RAM (GB)", ram_options)

        if selected_ram:
            filtered = filtered[filtered["RAM"].isin(selected_ram)]

    if "ROM" in df.columns:
        rom_options = sorted(df["ROM"].dropna().unique().tolist())
        selected_rom = st.multiselect(
            "Bộ nhớ trong (GB)", rom_options
        )

        if selected_rom:
            filtered = filtered[filtered["ROM"].isin(selected_rom)]

    if "Ho_tro_5G" in df.columns:
        network = st.selectbox(
            "Kết nối 5G",
            ["Tất cả", "Có 5G", "Không có 5G"],
        )

        if network == "Có 5G":
            filtered = filtered[filtered["Ho_tro_5G"] == 1]
        elif network == "Không có 5G":
            filtered = filtered[filtered["Ho_tro_5G"] == 0]

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background:#1c2a40;
                    border:1px solid #35455f;
                    border-radius:14px;padding:14px;">
            <div style="font-size:11px;color:#9fb0c8;
                        text-transform:uppercase;letter-spacing:1px;">
                Kết quả lọc
            </div>
            <div style="font-size:25px;font-weight:800;
                        color:#ffffff;margin-top:4px;">
                {len(filtered):,}
            </div>
            <div style="font-size:11px;color:#9fb0c8;">
                trên tổng số {len(df):,} bản ghi
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Dữ liệu hiện tại có thể là dữ liệu demo.")


# ==================== HÀM DÙNG CHUNG ====================
def money(value):
    if pd.isna(value):
        return "—"
    return f"{value:,.0f} đ".replace(",", ".")


def metric_card(label, value, foot):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(kicker, title, description):
    st.markdown(
        f'<div class="eyebrow">{kicker}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section-caption">{description}</div>',
        unsafe_allow_html=True,
    )


def chart_data(data, column):
    if column not in data.columns:
        return pd.DataFrame()

    return (
        data[column]
        .dropna()
        .value_counts()
        .head(12)
        .rename_axis(column)
        .reset_index(name="Số lượng")
    )


# ==================== TIÊU ĐỀ CHÍNH ====================
st.markdown(
    """
    <div class="hero">
        <div class="hero-pill">
            DATA · INSIGHTS · PRICE ESTIMATION
        </div>
        <h1>Khám phá thị trường<br>
            điện thoại thông minh
        </h1>
        <p>
            Không gian theo dõi dữ liệu, phân tích thông số và xây dựng
            nền tảng ước lượng giá điện thoại — được thực hiện bởi Nhóm 06.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==================== TRANG TỔNG QUAN ====================
if page == "Tổng quan":
    page_header(
        "DASHBOARD / 01",
        "Bức tranh tổng quan",
        "Tổng hợp nhanh dữ liệu theo bộ lọc hiện tại."
    )

    price_series = (
        filtered["Gia_ban"].dropna()
        if "Gia_ban" in filtered.columns
        else pd.Series(dtype=float)
    )

    phone_count = (
        filtered["Ten_may"].nunique()
        if "Ten_may" in filtered.columns
        else len(filtered)
    )

    brand_count = (
        filtered["Hang"].nunique()
        if "Hang" in filtered.columns
        else 0
    )

    price_series = price_series[
    price_series.between(1, 200_000_000)
    ]

    avg_price = price_series.mean() if not price_series.empty else None
    median_price = price_series.median() if not price_series.empty else None

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        metric_card("ĐIỆN THOẠI", f"{phone_count:,}", "Mẫu trong bộ lọc")

    with c2:
        metric_card("THƯƠNG HIỆU", f"{brand_count:,}", "Hãng đang hiển thị")

    with c3:
        metric_card(
            "GIÁ TRUNG BÌNH",
            money(avg_price) if avg_price is not None else "—",
            "Theo dữ liệu hiện có"
        )

    with c4:
        metric_card(
            "GIÁ TRUNG VỊ",
            money(median_price) if median_price is not None else "—",
            "Ít nhạy với giá ngoại lệ"
        )

    st.write("")

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        page_header(
            "PRICE OVERVIEW",
            "Mức giá theo điện thoại",
            "Tối đa 12 mẫu có giá để biểu đồ dễ đọc."
        )

        if (
            "Ten_may" in filtered.columns
            and "Gia_ban" in filtered.columns
            and not price_series.empty
        ):
            chart_df = (
                filtered[["Ten_may", "Gia_ban"]]
                .dropna()
                .query("Gia_ban > 0 and Gia_ban <= 200000000")
                .sort_values("Gia_ban", ascending=False)
                .head(12)
                .set_index("Ten_may")
            )

            st.bar_chart(chart_df, y="Gia_ban", color="#0f9f9a")

            st.caption(
                "Đơn vị giá: VND. Dữ liệu có thể là dữ liệu demo."
            )
        else:
            st.info("Chưa có đủ dữ liệu để vẽ biểu đồ.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        page_header(
            "BRAND MIX",
            "Cơ cấu thương hiệu",
            "Số mẫu theo từng hãng trong kết quả lọc."
        )

        brand_counts = chart_data(filtered, "Hang")

        if not brand_counts.empty:
            st.bar_chart(
                brand_counts.set_index("Hang"),
                y="Số lượng",
                color="#6584f5"
            )
        else:
            st.info("Chưa có dữ liệu thương hiệu.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    page_header(
        "LATEST RECORDS",
        "Dữ liệu đang xem",
        "Một vài bản ghi đầu tiên sau khi áp dụng bộ lọc."
    )

    st.dataframe(
        filtered.head(8),
        use_container_width=True,
        hide_index=True
    )


# ==================== TRANG DỮ LIỆU ====================
elif page == "Dữ liệu điện thoại":
    page_header(
        "DATA EXPLORER / 02",
        "Dữ liệu điện thoại",
        "Tìm kiếm, kiểm tra và tải xuống dữ liệu hiện tại."
    )

    search = st.text_input(
        "⌕ Tìm theo tên điện thoại",
        placeholder="Ví dụ: iPhone, Samsung, Xiaomi..."
    )

    table = filtered.copy()

    if search and "Ten_may" in table.columns:
        table = table[
            table["Ten_may"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    a, b = st.columns([1, 1])

    with a:
        st.markdown(f"**{len(table):,}** bản ghi phù hợp")

    with b:
        st.download_button(
            "⬇ Tải dữ liệu CSV",
            data=table.to_csv(index=False).encode("utf-8-sig"),
            file_name="du_lieu_dien_thoai.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=500
    )

    st.caption(
        "Các giá trị trống được giữ nguyên để kiểm tra và làm sạch dữ liệu."
    )


# ==================== TRANG THỐNG KÊ ====================
elif page == "Phân tích thống kê":
    page_header(
        "STATISTICS / 03",
        "Phân tích thống kê",
        "Khám phá mức giá và các đặc điểm nổi bật của dữ liệu."
    )

    if (
        "Gia_ban" not in filtered.columns
        or filtered["Gia_ban"].dropna().empty
    ):
        st.warning("Chưa có dữ liệu giá hợp lệ để thống kê.")

    else:
        prices = filtered["Gia_ban"].dropna()

        p1, p2, p3, p4 = st.columns(4, gap="medium")

        with p1:
            metric_card("GIÁ THẤP NHẤT", money(prices.min()), "Min")

        with p2:
            metric_card("GIÁ CAO NHẤT", money(prices.max()), "Max")

        with p3:
            metric_card(
                "ĐỘ LỆCH CHUẨN",
                money(prices.std()) if len(prices) > 1 else "—",
                "Standard deviation"
            )

        with p4:
            metric_card(
                "SỐ MẪU CÓ GIÁ",
                f"{len(prices):,}",
                "Bản ghi hợp lệ"
            )

        st.write("")

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)

            page_header(
                "PRICE DISTRIBUTION",
                "Phân bố giá",
                "Tần suất giá theo các khoảng."
            )

            hist = (
                pd.cut(
                    prices,
                    bins=min(10, max(1, prices.nunique())),
                    duplicates="drop"
                )
                .value_counts()
                .sort_index()
            )

            hist_df = hist.rename_axis("Khoảng giá").reset_index(
                name="Số lượng"
            )
            hist_df["Khoảng giá"] = hist_df["Khoảng giá"].astype(str)

            st.bar_chart(
                hist_df.set_index("Khoảng giá"),
                y="Số lượng",
                color="#8b7cf6"
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)

            page_header(
                "PRICE BY BRAND",
                "Giá trung bình theo hãng",
                "Chỉ tính bản ghi có giá hợp lệ."
            )

            if "Hang" in filtered.columns:
                brand_price = (
                    filtered.dropna(subset=["Gia_ban"])
                    .groupby("Hang", dropna=True)["Gia_ban"]
                    .mean()
                    .sort_values(ascending=False)
                    .head(12)
                )

                if not brand_price.empty:
                    st.bar_chart(brand_price, color="#0f9f9a")
                else:
                    st.info("Chưa có dữ liệu để so sánh.")
            else:
                st.info("Không tìm thấy cột Hang.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        page_header(
            "DESCRIPTIVE SUMMARY",
            "Bảng thống kê mô tả",
            "Các chỉ số cơ bản của cột giá."
        )

        summary = prices.describe().to_frame(name="Gia_ban").rename(
            index={
                "count": "Số lượng",
                "mean": "Trung bình",
                "std": "Độ lệch chuẩn",
                "min": "Nhỏ nhất",
                "25%": "Phân vị 25%",
                "50%": "Trung vị",
                "75%": "Phân vị 75%",
                "max": "Lớn nhất",
            }
        )

        st.dataframe(summary, use_container_width=True)


# ==================== K-MEANS / PCA / RADAR ====================
elif page == "K-means / PCA / Radar":
    page_header(
        "ADVANCED ANALYTICS / 04",
        "Phân tích nâng cao",
        "Khu vực dành cho K-means, PCA và biểu đồ Radar."
    )

    st.info(
        "Đây hiện là khung giao diện. Thuật toán và biểu đồ "
        "nâng cao chưa được tích hợp."
    )

    cards = st.columns(3, gap="medium")

    details = [
        (
            "01",
            "K-means",
            "Phân nhóm điện thoại dựa trên các thông số đã chuẩn hóa."
        ),
        (
            "02",
            "PCA",
            "Biểu diễn dữ liệu nhiều chiều trên mặt phẳng 2D."
        ),
        (
            "03",
            "Radar chart",
            "So sánh nhiều thông số của các mẫu điện thoại."
        ),
    ]

    for col, (number, title, description) in zip(cards, details):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="min-height:190px;">
                    <div class="eyebrow">{number} / MODULE</div>
                    <div style="font-size:21px;font-weight:800;
                                color:#17263d;margin-bottom:10px;">
                        {title}
                    </div>
                    <div style="font-size:12px;line-height:1.7;
                                color:#758197;">
                        {description}
                    </div>
                    <div style="margin-top:18px;font-size:11px;
                                font-weight:700;color:#b7791f;">
                        ĐANG CHỜ TÍCH HỢP
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    st.markdown(
        """
        <div class="panel">
            <b>Gợi ý dữ liệu đầu vào</b>
            <p class="small-note">
                Có thể bắt đầu từ RAM, ROM, kích thước màn hình,
                độ sáng, camera và giá. Cần xử lý giá trị thiếu,
                mã hóa biến phân loại và chuẩn hóa dữ liệu trước
                khi chạy thuật toán.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================== ƯỚC LƯỢNG GIÁ ====================
elif page == "Ước lượng giá":
    page_header(
        "PRICE ESTIMATOR / 05",
        "Ước lượng giá điện thoại",
        "Giao diện dự kiến cho mô hình dự đoán giá của nhóm."
    )

    st.info(
        "Mô hình học máy chưa được kết nối. Các trường dưới đây "
        "chỉ là giao diện minh họa, chưa tạo ra dự đoán thật."
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### Thông số điện thoại")

        brand_list = (
            sorted(df["Hang"].dropna().astype(str).unique().tolist())
            if "Hang" in df.columns
            else []
        )

        st.selectbox(
            "Hãng",
            brand_list if brand_list else ["Chưa có dữ liệu"]
        )

        ram_values = (
            sorted(df["RAM"].dropna().unique().tolist())
            if "RAM" in df.columns
            else [4, 6, 8, 12, 16]
        )

        rom_values = (
            sorted(df["ROM"].dropna().unique().tolist())
            if "ROM" in df.columns
            else [64, 128, 256, 512]
        )

        st.selectbox("RAM (GB)", ram_values)
        st.selectbox("Bộ nhớ trong (GB)", rom_values)
        st.selectbox("Hỗ trợ 5G", ["Có", "Không"])
        st.selectbox("Hệ điều hành", ["Android", "iOS", "Khác"])

        st.button(
            "Ước lượng giá",
            disabled=True,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="metric-card"
                 style="min-height:260px;display:flex;
                        flex-direction:column;justify-content:center;">
                <div class="eyebrow">MODEL OUTPUT</div>
                <div style="font-size:23px;font-weight:800;
                            color:#17263d;margin:8px 0;">
                    Kết quả sẽ hiển thị tại đây
                </div>
                <div style="font-size:13px;line-height:1.8;
                            color:#758197;">
                    Sau khi nhóm hoàn thiện mô hình, khu vực này
                    sẽ hiển thị giá dự đoán và có thể bổ sung
                    sai số hoặc khoảng giá tham khảo.
                </div>
                <div style="margin-top:20px;display:inline-block;
                            color:#b7791f;font-size:11px;font-weight:800;">
                    MODEL NOT CONNECTED
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================== CHÂN TRANG ====================
st.markdown("---")

st.markdown(
    """
    <div style="display:flex;justify-content:space-between;
                gap:12px;flex-wrap:wrap;">
        <div style="font-size:11px;color:#7c879b;">
            PHONE ANALYTICS · NHÓM 06
        </div>
        <div style="font-size:11px;color:#7c879b;">
            Phân tích dữ liệu & ước lượng giá điện thoại
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

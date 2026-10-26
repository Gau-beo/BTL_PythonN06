from pathlib import Path
import re, unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(page_title='PhoneHub | Nhóm 06', page_icon='📱', layout='wide')
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CANDIDATES = [
    BASE_DIR/'data'/'dien_thoai_viet_nam_1021.csv',
    BASE_DIR/'data'/'MockData'/'dien_thoai_viet_nam_1021.csv',
    BASE_DIR/'data'/'data_clean.csv'
]
IMAGE_DIR = BASE_DIR/'assets'/'phones'


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #142D4E;
    --teal: #0D9488;
    --bg: #F6F8FC;
    --text: #192B43;
    --muted: #6B7C93;
    --border: #E1E8F0;
}

html, body, [class*="css"] {
    font-family: 'Be Vietnam Pro', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid #243F5E;
}

section[data-testid="stSidebar"] * {
    color: #F1F6FC;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #B6C7DA;
}

/* Hero banner */
.hero {
    padding: 34px;
    border-radius: 22px;
    color: white;
    background: linear-gradient(120deg, #142D4E 0%, #18516B 58%, #0D9488 100%);
    margin-bottom: 28px;
    box-shadow: 0 12px 30px rgba(20, 45, 78, 0.12);
}

.hero h1 {
    color: white;
    font-size: clamp(28px, 3vw, 40px);
    font-weight: 800;
    margin: 10px 0;
    line-height: 1.25;
}

.hero p {
    color: #E1F1F5;
    font-size: 14px;
    line-height: 1.8;
    margin: 0;
}

/* Section headings */
.eyebrow {
    color: var(--teal);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.6px;
    margin-bottom: 7px;
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    margin-bottom: 5px;
    color: var(--navy);
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 18px;
}

/* Statistic cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    min-height: 118px;
    box-shadow: 0 4px 14px rgba(20, 45, 78, 0.035);
}

.metric-label {
    color: var(--muted);
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 9px;
}

.metric-value {
    color: var(--navy);
    font-size: clamp(19px, 1.8vw, 27px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

.metric-foot {
    color: var(--teal);
    font-size: 11px;
    margin-top: 8px;
}

/* Product cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border);
    border-radius: 18px;
}

.product-brand {
    font-size: 11px;
    font-weight: 800;
    color: var(--teal);
    letter-spacing: .7px;
    text-transform: uppercase;
}

.product-name {
    font-size: 15px;
    font-weight: 700;
    line-height: 1.5;
    min-height: 44px;
    margin: 8px 0 4px;
    color: var(--navy);
}

.product-price {
    font-size: 20px;
    font-weight: 800;
    color: var(--teal);
    margin: 8px 0;
}

.product-spec {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.7;
}

/* Inputs and dropdowns */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: var(--text) !important;
    border-color: #D8E1EC !important;
    border-radius: 10px !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #8795A8 !important;
}

.stApp label,
.stApp [data-testid="stWidgetLabel"] p {
    color: var(--text);
    font-weight: 600;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background: #FFFFFF;
    color: var(--navy);
    border: 1px solid #D8E1EC;
    border-radius: 11px;
    font-weight: 700;
    transition: all .2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #E8F7F5;
    color: #087F75;
    border-color: #81CDC4;
}

/* Primary actions */
.stButton > button[kind="primary"],
button[kind="primary"] {
    background: var(--teal);
    color: #FFFFFF;
    border-color: var(--teal);
}

.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover {
    background: #087F75;
    color: #FFFFFF;
}

/* Slider and links */
.stSlider [data-testid="stTickBar"] {
    color: var(--muted);
}

a {
    color: var(--teal);
}

/* Data tables */
.stDataFrame {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* Dividers */
hr {
    border-color: var(--border);
}
</style>
""", unsafe_allow_html=True)


def slugify(value):
    s=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9]+','_',s).strip('_').lower()[:120]

def parse_numeric(series):
    if pd.api.types.is_numeric_dtype(series): return pd.to_numeric(series,errors='coerce')
    def convert(v):
        if pd.isna(v): return float('nan')
        s=str(v).strip().lower().replace('vnd','').replace('vnđ','').replace('đ','').replace('gb','').replace('mp','')
        s=re.sub(r'\s+','',s)
        if not s: return float('nan')
        # Vietnamese CSV often uses dots/commas as thousands separators.
        if re.fullmatch(r'\d{1,3}([.,]\d{3})+',s): s=re.sub(r'[.,]','',s)
        elif ',' in s and '.' not in s: s=s.replace(',','.')
        try: return float(s)
        except ValueError: return float('nan')
    return series.map(convert)

@st.cache_data(show_spinner=False)
def load_data(path, mtime):
    d=pd.read_csv(path,na_values=['N/a','N/A','n/a',''])
    d.columns=[str(c).strip() for c in d.columns]
    aliases={'Tên máy':'Ten_may','Ten may':'Ten_may','Hãng':'Hang','Gia ban':'Gia_ban','Giá bán':'Gia_ban','RAM (GB)':'RAM','ROM (GB)':'ROM','Image_URL':'Anh','image_url':'Anh','Image':'Anh','image':'Anh','URL_anh':'Anh','Link_anh':'Anh'}
    d=d.rename(columns={k:v for k,v in aliases.items() if k in d.columns and v not in d.columns})
    for c in d.select_dtypes(include='object').columns:
        d[c]=d[c].astype(str).str.strip().replace({'':'', 'nan':pd.NA,'None':pd.NA})
    for c in ['Gia_ban','RAM','ROM','Ho_tro_5G','Kich_thuoc_man','Do_sang_nits','Cam_sau_MP','Cam_truoc_MP','Khoi_luong']:
        if c in d.columns: d[c]=parse_numeric(d[c])
    if 'Ten_may' not in d: d['Ten_may']=[f'Điện thoại {i+1}' for i in range(len(d))]
    if 'Hang' not in d: d['Hang']='Chưa phân loại'
    d['Ten_may']=d['Ten_may'].fillna('Chưa rõ tên').astype(str); d['Hang']=d['Hang'].fillna('Chưa phân loại').astype(str)
    d['Gia_ban_goc']=d['Gia_ban'] if 'Gia_ban' in d else pd.NA
    if 'Gia_ban' not in d: d['Gia_ban']=pd.NA
    # Flag implausible prices instead of presenting them as real prices.
    d.loc[(d['Gia_ban']<=0)|(d['Gia_ban']>200_000_000),'Gia_ban']=pd.NA
    return d.drop_duplicates().reset_index(drop=True)

def money(x):
    return 'Chưa có giá' if x is None or pd.isna(x) else f'{x:,.0f} đ'.replace(',','.')

def header(k,t,d): st.markdown(f'<div class="eyebrow">{k}</div><div class="section-title">{t}</div><div class="section-caption">{d}</div>',unsafe_allow_html=True)
def metric(label,value,foot=''):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',unsafe_allow_html=True)

def image_for(row):
    # Priority: URL/path in CSV, then local file named after the phone model.
    for c in ['Anh','URL_anh','Link_anh','Image_URL','image_url','Image','image','Photo','photo']:
        v=row.get(c) if c in row.index else None
        if isinstance(v,str) and v.strip().startswith(('https://','http://')): return v.strip()
        if isinstance(v,str) and v.strip() and (BASE_DIR/v.strip()).is_file(): return str(BASE_DIR/v.strip())
    if IMAGE_DIR.exists():
        for ext in ['jpg','jpeg','png','webp']:
            p=IMAGE_DIR/f'{slugify(row.get("Ten_may",""))}.{ext}'
            if p.is_file(): return str(p)
    return None

def open_phone_details(phone_name):
    st.session_state['selected_phone'] = phone_name
    st.session_state['navigation'] = 'Chi tiết điện thoại'

def product_card(row,key):
    with st.container(border=True):
        img=image_for(row)
        if img: st.image(img,use_container_width=True)
        else: st.markdown('<div style="height:150px;background:linear-gradient(135deg,#eef4f8,#e1f5f2);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:58px">📱</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="product-brand">{row.get("Hang","Chưa phân loại")}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="product-name">{row.get("Ten_may","Chưa rõ tên")}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="product-price">{money(row.get("Gia_ban"))}</div>',unsafe_allow_html=True)
        specs=[]
        for c,label in [('RAM','RAM'),('ROM','ROM'),('Kich_thuoc_man','inch')]:
            v=row.get(c)
            if pd.notna(v):
                specs.append(f'{label} {v:g} GB' if label in ['RAM','ROM'] else f'{v:g} inch')

        st.markdown(f'<div class="product-spec">{" · ".join(specs) or "Chưa đủ thông số"}</div>', unsafe_allow_html=True)

        
        st.button(
            'Xem thông tin',
            key=f'detail_{key}',
            use_container_width=True,
            on_click=open_phone_details,
            args=(str(row.get('Ten_may', '')),)
        )


source=next((p for p in DATA_CANDIDATES if p.exists()),None)
if source is None:
    st.error('Không tìm thấy dữ liệu. Kiểm tra thư mục data/ và đặt data_clean.csv hoặc dien_thoai_viet_nam_1021.csv vào đó.'); st.stop()
try: df=load_data(str(source),source.stat().st_mtime)
except Exception as e: st.error(f'Không đọc được dữ liệu: {e}'); st.stop()

st.sidebar.markdown('## 📱 PhoneHub'); st.sidebar.caption('PHÂN TÍCH DỮ LIỆU ĐIỆN THOẠI')
pages=['Khám phá điện thoại','Chi tiết điện thoại','So sánh hai máy','Tổng quan','Phân tích thống kê','K-means / PCA / Radar','Ước lượng giá']
default=st.session_state.get('navigation',pages[0]); default=default if default in pages else pages[0]
page=st.sidebar.radio('Danh mục',pages,index=pages.index(default),key='navigation')
st.sidebar.divider(); st.sidebar.markdown('### Bộ lọc nhanh')
brands=sorted(df['Hang'].dropna().astype(str).unique().tolist()); selected_brands=st.sidebar.multiselect('Hãng điện thoại',brands)
prices=df['Gia_ban'].dropna()
price_range=None
if not prices.empty:
    lo,hi=int(prices.min()),int(prices.max())
    price_range=st.sidebar.slider('Khoảng giá (VND)',lo,hi,(lo,hi),step=max(1,(hi-lo)//100)) if lo<hi else (lo,hi)
filtered=df.copy()
if selected_brands: filtered=filtered[filtered['Hang'].isin(selected_brands)]
if price_range: filtered=filtered[filtered['Gia_ban'].between(*price_range,inclusive='both')]

st.markdown('''<div class="hero"><div style="font-size:11px;font-weight:800;letter-spacing:1.5px;color:#b8fff4">PHONEHUB · DATA · INSIGHTS</div><h1>Khám phá thế giới điện thoại</h1><p>Xem các mẫu máy theo thương hiệu, tìm kiếm cấu hình, tham khảo giá và khám phá kết quả phân tích dữ liệu của Nhóm 06.</p></div>''',unsafe_allow_html=True)

if page=='Khám phá điện thoại':
    header('PHONE CATALOG / 01','Tất cả điện thoại theo thương hiệu','Chọn hãng, tìm tên máy và xem giá trên từng thẻ sản phẩm.')
    c1,c2,c3=st.columns([2,1,1]); search=c1.text_input('🔎 Tìm kiếm',placeholder='iPhone, Galaxy, Redmi...')
    brand=c2.selectbox('Thương hiệu',['Tất cả hãng']+sorted(filtered['Hang'].unique().tolist()))
    sort=c3.selectbox('Sắp xếp',['Mặc định','Giá thấp đến cao','Giá cao đến thấp','Tên A–Z'])
    catalog=filtered.copy()
    if brand!='Tất cả hãng': catalog=catalog[catalog['Hang']==brand]
    if search: catalog=catalog[catalog['Ten_may'].str.contains(search,case=False,na=False)|catalog['Hang'].str.contains(search,case=False,na=False)]
    if sort=='Giá thấp đến cao': catalog=catalog.sort_values('Gia_ban',na_position='last')
    elif sort=='Giá cao đến thấp': catalog=catalog.sort_values('Gia_ban',ascending=False,na_position='last')
    elif sort=='Tên A–Z': catalog=catalog.sort_values('Ten_may')
    a,b,c=st.columns(3)
    with a: metric('MẪU ĐIỆN THOẠI',f'{len(catalog):,}','Theo bộ lọc')
    with b: metric('THƯƠNG HIỆU',f'{catalog.Hang.nunique():,}','Đang hiển thị')
    with c: metric('MẪU CÓ GIÁ HỢP LỆ',f'{catalog.Gia_ban.notna().sum():,}','Giá dưới 200 triệu')
    st.write('')
    if catalog.empty: st.info('Không tìm thấy mẫu máy phù hợp. Thử đổi từ khóa hoặc bộ lọc.')
    else:
        per_page=12; total=max(1,(len(catalog)+per_page-1)//per_page)
        current=st.selectbox('Trang sản phẩm',range(1,total+1),format_func=lambda x:f'Trang {x}/{total}')
        shown=list(catalog.iloc[(current-1)*per_page:current*per_page].iterrows())
        for start in range(0,len(shown),3):
            cols=st.columns(3,gap='medium')
            for col,(idx,row) in zip(cols,shown[start:start+3]):
                with col: product_card(row,f'{idx}_{current}')
        st.caption('Ảnh lấy từ URL/cột ảnh trong CSV hoặc thư mục assets/phones. Nếu chưa có ảnh thật cho mẫu máy, giao diện hiển thị biểu tượng thay thế.')
        st.download_button('⬇ Tải danh sách đang lọc CSV',catalog.drop(columns=['Gia_ban_goc'],errors='ignore').to_csv(index=False).encode('utf-8-sig'),'danh_sach_dien_thoai.csv','text/csv')

elif page=='Chi tiết điện thoại':
    header('PHONE DETAILS / 02','Chi tiết điện thoại','Thông tin chi tiết của một mẫu trong dữ liệu.')
    names=sorted(df.Ten_may.unique().tolist()); default_name=st.session_state.get('selected_phone',names[0] if names else '')
    if names:
        name=st.selectbox('Chọn điện thoại',names,index=names.index(default_name) if default_name in names else 0); row=df[df.Ten_may==name].iloc[0]
        left,right=st.columns([1,1.5],gap='large')
        with left:
            img=image_for(row)
            if img: st.image(img,use_container_width=True)
            else: st.info('Chưa có ảnh: thêm URL vào cột Anh hoặc file vào assets/phones.')
            st.subheader(name); st.markdown(f'### :green[{money(row.get("Gia_ban"))}]'); st.write(f'**Hãng:** {row.get("Hang")}')
        with right:
            st.subheader('Thông số kỹ thuật'); detail=row.drop(labels=['Gia_ban_goc'],errors='ignore').dropna()
            st.dataframe(detail.rename_axis('Thuộc tính').reset_index(name='Giá trị'),use_container_width=True,hide_index=True)

elif page=='So sánh hai máy':
    header('PHONE COMPARISON / 03','So sánh hai điện thoại','Đối chiếu giá bán và thông số kỹ thuật cạnh nhau.')
    names=sorted(df.Ten_may.unique().tolist())
    if len(names)>=2:
        ca,cb=st.columns(2)
        with ca: na=st.selectbox('Điện thoại A',names,index=0)
        with cb: nb=st.selectbox('Điện thoại B',names,index=1)
        ra=df[df.Ten_may==na].iloc[0]; rb=df[df.Ten_may==nb].iloc[0]
        ia,ib=st.columns(2)
        with ia:
            img=image_for(ra)
            if img: st.image(img,use_container_width=True)
            st.subheader(na); st.markdown(f'### :green[{money(ra.get("Gia_ban"))}]')
        with ib:
            img=image_for(rb)
            if img: st.image(img,use_container_width=True)
            st.subheader(nb); st.markdown(f'### :green[{money(rb.get("Gia_ban"))}]')
        fields=['Hang','He_dieu_hanh','Chipset','RAM','ROM','Ho_tro_5G','Kich_thuoc_man','Tam_nen','Do_phan_giai','Do_sang_nits','Cam_sau_MP','Cam_truoc_MP','Kich_thuoc','Khoi_luong','Chat_lieu','Khang_nuoc_bui','Cong_ket_noi']
        rows=[{'Thông số':'Giá bán',na:money(ra.get('Gia_ban')),nb:money(rb.get('Gia_ban'))}]
        for f in fields:
            if f in df.columns: rows.append({'Thông số':f,na:ra.get(f,'—'),nb:rb.get(f,'—')})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info('Cần ít nhất hai mẫu điện thoại trong dữ liệu.')

elif page=='Tổng quan':
    header('DASHBOARD / 04','Tổng quan dữ liệu','Các chỉ số tổng hợp theo bộ lọc bên trái.')
    p=filtered.Gia_ban.dropna(); cols=st.columns(4)
    vals=[('MẪU ĐIỆN THOẠI',f'{filtered.Ten_may.nunique():,}','Số mẫu'),('THƯƠNG HIỆU',f'{filtered.Hang.nunique():,}','Số hãng'),('GIÁ TRUNG BÌNH',money(p.mean()) if not p.empty else '—','Giá hợp lệ'),('GIÁ TRUNG VỊ',money(p.median()) if not p.empty else '—','Giá hợp lệ')]
    for col,args in zip(cols,vals):
        with col: metric(*args)
    left,right=st.columns(2)
    with left:
        header('PRICE OVERVIEW','Mẫu có giá cao','Tối đa 12 mẫu có giá hợp lệ.'); plot=filtered.dropna(subset=['Gia_ban']).nlargest(12,'Gia_ban')
        if not plot.empty: st.bar_chart(plot.set_index('Ten_may')['Gia_ban'])
        else: st.info('Chưa có giá hợp lệ.')
    with right:
        header('BRAND MIX','Số mẫu theo thương hiệu','Tối đa 15 hãng.'); st.bar_chart(filtered.Hang.value_counts().head(15))
    st.dataframe(filtered.drop(columns=['Gia_ban_goc'],errors='ignore').head(15),use_container_width=True,hide_index=True)

elif page=='Phân tích thống kê':
    header('STATISTICS / 05','Phân tích thống kê','Thống kê mô tả và so sánh giá bán.')
    p=filtered.Gia_ban.dropna()
    if p.empty: st.warning('Không có giá hợp lệ trong dữ liệu đã lọc.')
    else:
        cols=st.columns(4); vals=[('GIÁ THẤP NHẤT',money(p.min()),'VND'),('GIÁ CAO NHẤT',money(p.max()),'VND'),('GIÁ TRUNG BÌNH',money(p.mean()),'VND'),('SỐ MẪU CÓ GIÁ',f'{len(p):,}','Bản ghi')]
        for col,args in zip(cols,vals):
            with col: metric(*args)
        left,right=st.columns(2)
        with left:
            header('PRICE DISTRIBUTION','Phân bố giá','Tần suất theo khoảng giá.'); hist=pd.cut(p,bins=min(10,max(1,p.nunique())),duplicates='drop').value_counts().sort_index(); h=hist.rename_axis('Khoảng giá').reset_index(name='Số lượng'); h['Khoảng giá']=h['Khoảng giá'].astype(str); st.bar_chart(h.set_index('Khoảng giá')['Số lượng'])
        with right:
            header('PRICE BY BRAND','Giá trung bình theo hãng','Tối đa 15 hãng.'); by=filtered.dropna(subset=['Gia_ban']).groupby('Hang').Gia_ban.mean().nlargest(15)
            if not by.empty: st.bar_chart(by)
        st.dataframe(p.describe().to_frame('Gia_ban'),use_container_width=True)

elif page=='K-means / PCA / Radar':
    header('ADVANCED ANALYTICS / 06','K-means, PCA và Radar','Chạy phân cụm trên dữ liệu hiện tại để quan sát nhóm điện thoại.')
    candidates=[c for c in ['Gia_ban','RAM','ROM','Kich_thuoc_man','Do_sang_nits','Cam_sau_MP','Cam_truoc_MP','Khoi_luong'] if c in filtered.columns]
    features=st.multiselect('Thuộc tính phân cụm',candidates,default=[c for c in ['Gia_ban','RAM','ROM','Kich_thuoc_man'] if c in candidates]); k=st.slider('Số cụm K',2,6,3)
    if len(features)<2: st.info('Chọn ít nhất hai thuộc tính số.')
    else:
        try:
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            from sklearn.impute import SimpleImputer
            from sklearn.preprocessing import StandardScaler
            import matplotlib.pyplot as plt
            import numpy as np
            analysis = filtered[['Ten_may', 'Hang'] + features].copy()

            for f in features:
                analysis[f] = pd.to_numeric(analysis[f], errors='coerce')

            
            analysis = analysis.replace([np.inf, -np.inf], np.nan)
            analysis = analysis.dropna(subset=features)

            # Loại giá trị RAM và ROM bất thường
            if 'ROM' in features:
                analysis = analysis[analysis['ROM'].between(1, 2048)]

            if 'RAM' in features:
                analysis = analysis[analysis['RAM'].between(1, 64)]

            if len(analysis)<k: st.warning('Số dòng hợp lệ ít hơn số cụm K.')
            else:
                X=StandardScaler().fit_transform(SimpleImputer(strategy='median').fit_transform(analysis[features])); analysis['Cụm']=KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(X).astype(str); coords=PCA(n_components=2).fit_transform(X); analysis['PCA 1']=coords[:,0]; analysis['PCA 2']=coords[:,1]
                left,right=st.columns(2)
                with left:
                    header('K-MEANS / PCA','Phân bố các cụm','Mỗi màu thể hiện một cụm.'); fig,ax=plt.subplots()
                    for cluster in sorted(analysis.Cụm.unique()):
                        part=analysis[analysis.Cụm==cluster]; ax.scatter(part['PCA 1'],part['PCA 2'],label=f'Cụm {cluster}',alpha=.75)
                    ax.set_xlabel('PCA 1'); ax.set_ylabel('PCA 2'); ax.legend(); st.pyplot(fig); plt.close(fig)
                with right:
                    header('CLUSTER SUMMARY','Mô tả cụm','Trung bình các thuộc tính trong mỗi cụm.'); st.dataframe(analysis.groupby('Cụm')[features].mean().round(2),use_container_width=True)
                header('RADAR','So sánh đặc trưng cụm','Các thuộc tính đã chuẩn hóa.'); import numpy as np
                means=pd.DataFrame(X,columns=features).assign(Cụm=analysis.Cụm.values).groupby('Cụm')[features].mean(); angles=np.linspace(0,2*np.pi,len(features),endpoint=False).tolist(); angles+=angles[:1]; fig,ax=plt.subplots(figsize=(6,6),subplot_kw={'polar':True})
                for cluster,values in means.iterrows():
                    vals=values.tolist(); vals+=vals[:1]; ax.plot(angles,vals,linewidth=2,label=f'Cụm {cluster}'); ax.fill(angles,vals,alpha=.08)
                ax.set_xticks(angles[:-1]); ax.set_xticklabels(features,fontsize=8); ax.legend(loc='upper right',bbox_to_anchor=(1.25,1.1)); st.pyplot(fig); plt.close(fig)
                st.download_button('Tải kết quả phân cụm CSV',analysis.to_csv(index=False).encode('utf-8-sig'),'ket_qua_phan_cum.csv','text/csv')
        except ImportError: st.error('Cài thư viện cần thiết bằng: pip install scikit-learn matplotlib')

elif page=='Ước lượng giá':
    header('PRICE ESTIMATOR / 07','Ước lượng giá điện thoại','Mô hình hồi quy thử nghiệm dựa trên dữ liệu có giá hợp lệ.')
    st.warning('Đây là mô hình thử nghiệm tự huấn luyện từ CSV hiện tại. Chất lượng dự đoán phụ thuộc mạnh vào độ sạch và số lượng dữ liệu.')
    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import OneHotEncoder,StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error
        candidates=[c for c in ['Hang','He_dieu_hanh','Chipset','RAM','ROM','Ho_tro_5G','Kich_thuoc_man','Tam_nen','Do_phan_giai','Do_sang_nits','Cam_sau_MP','Cam_truoc_MP','Chat_lieu','Khang_nuoc_bui','Cong_ket_noi'] if c in df.columns]
        train=df.dropna(subset=['Gia_ban']).copy(); candidates=[c for c in candidates if train[c].notna().sum()>2]
        if len(train)<15 or not candidates: st.info('Chưa đủ dữ liệu hợp lệ để huấn luyện. Cần ít nhất 15 mẫu có giá và thông số.')
        else:
            cat = [
                c for c in candidates
                if (
                    pd.api.types.is_object_dtype(train[c])
                    or pd.api.types.is_string_dtype(train[c])
                    or pd.api.types.is_bool_dtype(train[c])
                    or isinstance(train[c].dtype, pd.CategoricalDtype)
                )
            ]

            num = [c for c in candidates if c not in cat]
            prep=ColumnTransformer([('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cat)])
            model=Pipeline([('prep',prep),('regressor',RandomForestRegressor(n_estimators=160,random_state=42,min_samples_leaf=2))]); X=train[candidates]; y=train.Gia_ban
            if len(train)>=20:
                xt,xv,yt,yv=train_test_split(X,y,test_size=.2,random_state=42); model.fit(xt,yt); st.metric('MAE trên tập kiểm tra',money(mean_absolute_error(yv,model.predict(xv)))); model.fit(X,y)
            else: model.fit(X,y); st.info('Ít dữ liệu nên kết quả chỉ để minh họa, chưa đủ để kết luận độ chính xác.')
            st.subheader('Nhập thông số điện thoại'); inputs={}; cols=st.columns(2)
            for i,c in enumerate(candidates):
                with cols[i%2]:
                    if c in cat:
                        options=sorted(train[c].dropna().astype(str).unique().tolist()); inputs[c]=st.selectbox(c.replace('_',' '),options,key=f'pred_{c}')
                    else:
                        s=pd.to_numeric(train[c],errors='coerce').dropna(); default=float(s.median()) if not s.empty else 0.; mn=float(s.min()) if not s.empty else 0.; mx=float(s.max()) if not s.empty else max(default,1.); inputs[c]=st.number_input(c.replace('_',' '),min_value=mn,max_value=mx,value=min(max(default,mn),mx),key=f'pred_{c}')
            if st.button('Ước lượng giá',type='primary',use_container_width=True): st.success(f'Giá ước lượng: {money(float(model.predict(pd.DataFrame([inputs]))[0]))}')
    except ImportError: st.error('Thiếu scikit-learn. Cài bằng: pip install scikit-learn')

st.divider()
st.caption(f'PHONEHUB · NHÓM 06 | Nguồn dữ liệu: {source.relative_to(BASE_DIR)} | Giá bất thường (>200 triệu hoặc <=0) không được hiển thị như giá hợp lệ.')

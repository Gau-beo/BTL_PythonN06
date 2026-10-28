from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
import re, unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(page_title='PhoneHub | Nhóm 06', page_icon='📱', layout='wide')
BASE_DIR = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    BASE_DIR/'data'/'data_clean.csv'
]
IMAGE_DIR = BASE_DIR/'assets'/'phones'


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
:root{--ink:#111C32;--blue:#245BDB;--blue2:#3978FF;--blue-soft:#EAF0FF;--mint:#15B8A6;--bg:#F4F6FA;--muted:#738096;--line:#E4E9F2;--white:#FFF;}
html,body,[class*="css"]{font-family:'Be Vietnam Pro',sans-serif;color:var(--ink)}
.stApp{background:var(--bg)}
.block-container{max-width:1500px;padding-top:1.25rem;padding-bottom:3rem}
section[data-testid="stSidebar"]{background:#101B31;border-right:1px solid #23314A}
section[data-testid="stSidebar"] *{color:#F4F7FC}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#AEBBD0}
section[data-testid="stSidebar"] [role="radiogroup"]{gap:5px}
section[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px;border-radius:11px;border:1px solid transparent;transition:.18s}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#1C2A45;border-color:#2B4167}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#D7E0EF;font-size:12px;font-weight:700}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2{font-size:25px;letter-spacing:-.8px}
section[data-testid="stSidebar"] hr{border-color:#293750}
.store-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:7px 2px 19px;margin-bottom:4px}
.store-brand{display:flex;align-items:center;gap:11px}
.store-logo{width:43px;height:43px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#245BDB,#16B8A6);color:white;font-size:24px;box-shadow:0 8px 18px #245bdb2b}
.store-name{font-weight:800;font-size:22px;letter-spacing:-.8px;color:#111C32;line-height:1.1}
.store-sub{font-size:9px;font-weight:800;letter-spacing:1.6px;color:#7A879B;margin-top:5px}
.store-pill{padding:8px 12px;border:1px solid var(--line);border-radius:999px;background:white;color:#5B6880;font-size:11px;font-weight:700;white-space:nowrap}
.hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.55fr) minmax(200px,.75fr);gap:20px;align-items:center;padding:clamp(26px,4vw,48px);border-radius:28px;color:white;background:radial-gradient(circle at 83% 15%,#477EFF 0%,transparent 30%),linear-gradient(120deg,#101B31 0%,#173B83 58%,#245BDB 100%);margin-bottom:25px;box-shadow:0 20px 45px rgba(21,48,105,.16)}
.hero:before{content:'';position:absolute;width:330px;height:330px;border:1px solid #ffffff18;border-radius:50%;right:-100px;top:-145px;box-shadow:0 0 0 35px #ffffff08,0 0 0 70px #ffffff05;pointer-events:none}
.hero-copy,.hero-visual{position:relative;z-index:1}
.hero-kicker{display:inline-flex;align-items:center;gap:8px;padding:7px 11px;border:1px solid #ffffff30;background:#ffffff12;border-radius:999px;color:#DCE7FF;font-size:10px;font-weight:800;letter-spacing:1.5px}
.hero h1{color:#fff;font-size:clamp(30px,3.7vw,49px);font-weight:800;letter-spacing:-1.7px;line-height:1.12;margin:19px 0 14px;max-width:680px}
.hero p{color:#DCE7F9;font-size:14px;line-height:1.9;margin:0;max-width:620px}
.hero-note{margin-top:24px;display:flex;align-items:center;gap:9px;color:#E5EDFF;font-size:11px;font-weight:600}
.hero-note span{width:7px;height:7px;border-radius:50%;background:#45E0C2;box-shadow:0 0 0 5px #45e0c21c}
.hero-visual{min-height:220px;display:flex;align-items:center;justify-content:center}
.phone-art{position:relative;width:132px;height:232px;border-radius:29px;background:linear-gradient(145deg,#F9FBFF,#B9C9E7);border:5px solid #DFE8FA;box-shadow:18px 24px 35px #07152f70;transform:rotate(9deg)}
.phone-art:before{content:'';position:absolute;inset:7px;border-radius:21px;background:radial-gradient(circle at 75% 25%,#70C6FF 0%,transparent 22%),radial-gradient(circle at 35% 70%,#9C8BFF 0%,transparent 35%),linear-gradient(145deg,#0F1D3A,#245BDB 55%,#18B9AC)}
.phone-art:after{content:'';position:absolute;top:10px;left:50%;transform:translateX(-50%);width:43px;height:10px;border-radius:999px;background:#111C32}
.phone-orbit{position:absolute;width:188px;height:188px;border:1px solid #ffffff45;border-radius:50%;transform:rotate(-18deg)}
.hero-tag{position:absolute;right:2%;bottom:18%;background:#fff;color:#15213A;border:1px solid #ffffff80;padding:11px 14px;border-radius:14px;box-shadow:0 12px 25px #07152f40;font-size:11px;font-weight:800;transform:rotate(-4deg)}
.eyebrow{color:var(--blue);font-size:10px;font-weight:800;letter-spacing:1.7px;margin-bottom:8px}
.section-title{font-size:clamp(21px,2vw,28px);font-weight:800;letter-spacing:-.8px;margin-bottom:5px;color:var(--ink)}
.section-caption{color:var(--muted);font-size:13px;line-height:1.75;margin-bottom:18px}
.metric-card{position:relative;overflow:hidden;background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 21px;min-height:123px;box-shadow:0 7px 22px rgba(17,28,50,.035)}
.metric-card:after{content:'';position:absolute;width:64px;height:64px;border-radius:50%;right:-26px;top:-27px;background:var(--blue-soft)}
.metric-label{color:#7B879A;font-size:10px;font-weight:800;letter-spacing:.9px;margin-bottom:12px;position:relative;z-index:1}
.metric-value{color:var(--ink);font-size:clamp(22px,2vw,30px);font-weight:800;letter-spacing:-.8px;overflow-wrap:anywhere;position:relative;z-index:1}
.metric-foot{color:var(--blue);font-size:11px;font-weight:600;margin-top:8px;position:relative;z-index:1}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line);border-radius:20px;box-shadow:0 5px 20px rgba(17,28,50,.035);transition:transform .2s ease,box-shadow .2s ease}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{box-shadow:0 15px 34px rgba(17,28,50,.10);transform:translateY(-2px)}
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stImage"]{background:#F5F7FB;border-radius:15px;padding:7px}
div[data-testid="stImage"] img{border-radius:13px;object-fit:contain}
.product-brand{font-size:10px;font-weight:800;color:var(--blue);letter-spacing:1.1px;text-transform:uppercase;margin-top:7px}
.product-name{font-size:15px;font-weight:700;line-height:1.5;min-height:45px;margin:7px 0 3px;color:var(--ink)}
.product-price{font-size:22px;font-weight:800;color:#174BC1;margin:8px 0;letter-spacing:-.6px}
.page-indicator{text-align:center;padding:10px 14px;border:1px solid #DCE4F0;border-radius:12px;background:#FFFFFF;color:#748198;font-size:12px;letter-spacing:1.2px;font-weight:700;box-shadow:0 4px 14px rgba(20,40,80,.04)}
.page-indicator strong{color:#245BDB;font-size:18px;margin:0 7px;letter-spacing:0}
.page-indicator span{margin:0 5px;color:#A0AABC}
.product-spec{font-size:11px;color:#6D7B91;line-height:1.8;min-height:24px;padding:8px 0;border-top:1px solid #EDF0F6}
.stApp input,.stApp textarea,.stApp [data-baseweb="select"]>div{background:#fff!important;color:var(--ink)!important;border-color:#DCE3EE!important;border-radius:11px!important}
.stApp input::placeholder,.stApp textarea::placeholder{color:#8A96A8!important}
.stApp label,.stApp [data-testid="stWidgetLabel"] p{color:var(--ink);font-weight:600}
.stButton>button,.stDownloadButton>button{background:#fff;color:var(--ink);border:1px solid #DCE3EE;border-radius:11px;font-weight:700;min-height:43px;transition:all .18s ease}
.stButton>button:hover,.stDownloadButton>button:hover{background:#EDF3FF;color:#174BC1;border-color:#AFC5FF}
.stButton>button[kind="primary"],button[kind="primary"]{background:var(--blue);color:white;border-color:var(--blue);box-shadow:0 5px 12px #245bdb24}
.stButton>button[kind="primary"]:hover,button[kind="primary"]:hover{background:#174BC1;color:white}
a{color:var(--blue)}
.stDataFrame{border:1px solid var(--line);border-radius:14px;overflow:hidden}
[data-testid="stAlert"]{border-radius:14px}
hr{border-color:var(--line)}
@media(max-width:760px){.store-topbar{padding-bottom:13px}.store-pill{display:none}.hero{grid-template-columns:1fr;padding:25px}.hero-visual{display:none}.hero h1{font-size:32px}.metric-card{padding:15px}}
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
    d.loc[(d['Gia_ban']<=0)|(d['Gia_ban']>200_000_000),'Gia_ban']=pd.NA
    return d.drop_duplicates().reset_index(drop=True)

def money(x):
    return 'Chưa có giá' if x is None or pd.isna(x) else f'{x:,.0f} đ'.replace(',','.')

def header(k,t,d): st.markdown(f'<div class="eyebrow">{k}</div><div class="section-title">{t}</div><div class="section-caption">{d}</div>',unsafe_allow_html=True)
def metric(label,value,foot=''):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',unsafe_allow_html=True)

def image_for(row):
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
    st.error('Không tìm thấy dữ liệu. Kiểm tra thư mục data/ có data_clean.csv (chạy python src/process.py để tạo).'); st.stop()
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

st.markdown('<div class="store-topbar"><div class="store-brand"><div class="store-logo">⌁</div><div><div class="store-name">PhoneHub<span style="color:#245BDB">.</span></div><div class="store-sub">SMARTPHONE DISCOVERY & ANALYTICS</div></div></div><div class="store-pill">NHÓM 06&nbsp;&nbsp; · &nbsp;&nbsp;DỮ LIỆU ĐIỆN THOẠI</div></div>',unsafe_allow_html=True)
st.markdown('''<section class="hero"><div class="hero-copy"><div class="hero-kicker">✦ &nbsp; PHONEHUB STORE / DISCOVER / COMPARE</div><h1>Công nghệ phù hợp.<br>Quyết định thông minh.</h1><p>Khám phá điện thoại theo thương hiệu, so sánh cấu hình và giá bán. Từ trải nghiệm sản phẩm đến phân tích dữ liệu — tất cả trong một không gian.</p><div class="hero-note"><span></span> Khám phá · So sánh · Phân tích</div></div><div class="hero-visual"><div class="phone-orbit"></div><div class="phone-art"></div><div class="hero-tag">SMARTPHONE<br><span style="color:#245BDB;font-size:15px">YOUR NEXT PICK</span></div></div></section>''',unsafe_allow_html=True)

if page=='Khám phá điện thoại':
    header('01  /  THE COLLECTION','Khám phá bộ sưu tập','Tìm đúng mẫu máy theo tên, thương hiệu và ngân sách của bạn.')
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
        per_page = 12
        total = max(1, (len(catalog) + per_page - 1) // per_page)
        if 'catalog_page' not in st.session_state:
            st.session_state['catalog_page'] = 1
        st.session_state['catalog_page'] = min(max(1, st.session_state['catalog_page']), total)
        current = st.session_state['catalog_page']

        prev_col, page_col, next_col = st.columns([1, 2, 1], vertical_alignment='center')
        with prev_col:
            if st.button('← Trang trước', key='catalog_prev', disabled=current <= 1, use_container_width=True):
                st.session_state['catalog_page'] = max(1, current - 1)
                st.rerun()
        with page_col:
            st.markdown(
                f'<div class="page-indicator">TRANG <strong>{current}</strong><span>/</span>{total}</div>',
                unsafe_allow_html=True,
            )
        with next_col:
            if st.button('Trang sau →', key='catalog_next', disabled=current >= total, use_container_width=True):
                st.session_state['catalog_page'] = min(total, current + 1)
                st.rerun()

        shown=list(catalog.iloc[(current-1)*per_page:current*per_page].iterrows())
        for start in range(0,len(shown),3):
            cols=st.columns(3,gap='medium')
            for col,(idx,row) in zip(cols,shown[start:start+3]):
                with col: product_card(row,f'{idx}_{current}')
        st.caption('Ảnh lấy từ URL/cột ảnh trong CSV hoặc thư mục assets/phones. Nếu chưa có ảnh thật cho mẫu máy, giao diện hiển thị biểu tượng thay thế.')
        st.download_button('⬇ Tải danh sách đang lọc CSV',catalog.drop(columns=['Gia_ban_goc'],errors='ignore').to_csv(index=False).encode('utf-8-sig'),'danh_sach_dien_thoai.csv','text/csv')

elif page=='Chi tiết điện thoại':
    header('02  /  PRODUCT DETAILS','Thông tin sản phẩm','Thông số kỹ thuật và giá bán của mẫu điện thoại bạn chọn.')
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
            st.dataframe(detail.rename_axis('Thuộc tính').reset_index(name='Giá trị').astype(str),use_container_width=True,hide_index=True)

elif page=='So sánh hai máy':
    header('03  /  SIDE-BY-SIDE','Đặt hai lựa chọn lên bàn cân','So sánh giá và thông số kỹ thuật trong cùng một bảng.')
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
        st.dataframe(pd.DataFrame(rows).astype(str),use_container_width=True,hide_index=True)
    else: st.info('Cần ít nhất hai mẫu điện thoại trong dữ liệu.')

elif page=='Tổng quan':
    header('04  /  MARKET SNAPSHOT','Toàn cảnh thị trường','Những chỉ số nổi bật từ bộ dữ liệu điện thoại hiện tại.')
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
    header('05  /  DATA INSIGHTS','Phân tích thống kê','Đọc phân bố giá và khác biệt giữa các thương hiệu.')
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
    header('06  /  ADVANCED ANALYTICS','K-means · PCA · Radar','Khám phá các nhóm điện thoại và so sánh đặc trưng cấu hình.')
    candidates=[c for c in ['Gia_ban','RAM','ROM','Kich_thuoc_man','Do_sang_nits','Cam_sau_MP','Cam_truoc_MP','Khoi_luong'] if c in filtered.columns]
    features=st.multiselect('Thuộc tính phân cụm',candidates,default=[c for c in ['Gia_ban','RAM','ROM','Kich_thuoc_man','Cam_sau_MP','Cam_truoc_MP','Khoi_luong'] if c in candidates]); k=st.slider('Số cụm K',2,6,4)
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
            analysis = analysis.dropna(subset=features, how='all')

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
    header('07  /  PRICE INTELLIGENCE','Ước lượng giá điện thoại','Dùng mô hình đã huấn luyện bằng src/train_model.py (cùng mô hình trong báo cáo).')
    MODEL_FILE=BASE_DIR/'models'/'phone_price_model.pkl'; META_FILE=BASE_DIR/'models'/'model_meta.json'
    if not MODEL_FILE.exists() or not META_FILE.exists():
        st.error('Chưa có models/phone_price_model.pkl hoặc models/model_meta.json. Chạy: python src/train_model.py')
    else:
        try:
            import json, joblib
            meta=json.loads(META_FILE.read_text(encoding='utf-8')); model=joblib.load(MODEL_FILE)
            st.warning(meta.get('currency_note','Giá quy đổi từ thị trường Bangladesh, không phải giá bán tại Việt Nam.'))
            mt=meta.get('metrics_test',{}); c1,c2,c3=st.columns(3)
            with c1: metric('MÔ HÌNH',meta.get('model_name','?'),'đã huấn luyện')
            with c2: metric('R² (TẬP KIỂM THỬ)',f"{mt.get('R2',0):.3f}",'càng gần 1 càng tốt')
            with c3: metric('MAE',money(mt.get('MAE',0)),'sai số tuyệt đối TB')
            st.subheader('Nhập thông số điện thoại'); inputs={}; cols=st.columns(2)
            for i,c in enumerate(meta['features']):
                label=meta['labels'].get(c,c)
                with cols[i%2]:
                    if c in meta['categorical_features']:
                        options=meta['choices'][c]; d=meta['defaults'].get(c); idx=options.index(d) if d in options else 0
                        inputs[c]=st.selectbox(label,options,index=idx,key=f'pred_{c}')
                    else:
                        r=meta['numeric_ranges'][c]; mn,mx=float(r['min']),float(r['max']); default=min(max(float(meta['defaults'][c]),mn),mx)
                        inputs[c]=st.number_input(label,min_value=mn,max_value=mx,value=default,key=f'pred_{c}')
            if st.button('Ước lượng giá',type='primary',use_container_width=True):
                pred=float(model.predict(pd.DataFrame([inputs],columns=meta['features']))[0])
                lo,hi=meta['price_range']['min'],meta['price_range']['max']; pred=min(max(pred,lo),hi)
                st.success(f'Giá ước lượng: {money(pred)}'); st.caption(f"MAPE trung bình trên tập kiểm thử: {mt.get('MAPE',0):.0f}%. Đây không phải khoảng tin cậy cho từng dự đoán.")
        except ImportError: st.error('Thiếu thư viện. Cài bằng: pip install scikit-learn joblib')
        except Exception as e: st.error(f'Không nạp/dùng được mô hình: {e}. Hãy chạy lại python src/train_model.py bằng đúng phiên bản scikit-learn trong requirements.txt.')

st.divider()
st.caption(f'PHONEHUB · NHÓM 06 | Nguồn dữ liệu: {source.relative_to(BASE_DIR)} | Giá bất thường (>200 triệu hoặc <=0) không được hiển thị như giá hợp lệ.')

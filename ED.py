# =========================
# THƯ VIỆN BẮT BUỘC VÀ BỔ SUNG
# =========================
from datetime import datetime
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    accuracy_score,
    recall_score,
    precision_score,
    roc_auc_score,
    ConfusionMatrixDisplay,
)

# Thư viện GOOGLE GEMINI VÀ OPENAI (Giữ nguyên logic kiểm tra thư viện)
try:
    from google import genai
    from google.genai.errors import APIError
    _GEMINI_OK = True
except Exception:
    genai = None
    APIError = Exception
    _GEMINI_OK = False

try:
    from openai import OpenAI
    _OPENAI_OK = True
except Exception:
    OpenAI = None
    _OPENAI_OK = False


MODEL_NAME = "gemini-2.5-flash"

# =========================
# CẤU HÌNH TRANG (NÂNG CẤP GIAO DIỆN)
# =========================
st.set_page_config(
    page_title="Credit Risk PD & Gemini Analysis | Banking Suite",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CSS NÂNG CẤP - PHONG CÁCH NGÂN HÀNG HIỆN ĐẠI
# ========================================
st.markdown("""
<style>
/* ========== IMPORT GOOGLE FONTS ========== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=Playfair+Display:wght@700;900&display=swap');

/* ========== GENERAL SETTINGS ========== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Main content area */
.main {
    background: linear-gradient(135deg, #fff5f7 0%, #ffe8f0 100%);
    animation: fadeIn 0.8s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ========== PREMIUM HEADER BANNER ========== */
.banner-title-container {
    background: linear-gradient(135deg, #ff6b9d 0%, #ff85a1 50%, #ff6b9d 100%);
    padding: 40px 50px;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(255, 107, 157, 0.3),
                0 5px 15px rgba(255, 133, 161, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
    margin-bottom: 30px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

/* Shine effect */
.banner-title-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 30%,
        rgba(255, 255, 255, 0.1) 50%,
        transparent 70%
    );
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.banner-title-container h1 {
    color: #ffffff !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 900 !important;
    font-size: 2.8rem !important;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3),
                 0 0 30px rgba(255, 182, 193, 0.5);
    margin-bottom: 10px !important;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
    animation: titleGlow 2s ease-in-out infinite alternate;
}

@keyframes titleGlow {
    from { text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3), 0 0 30px rgba(255, 182, 193, 0.5); }
    to { text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3), 0 0 40px rgba(255, 182, 193, 0.7); }
}

.banner-title-container h3 {
    color: #fff0f5 !important;
    font-weight: 600 !important;
    font-size: 1.3rem !important;
    margin-top: 0 !important;
    border-bottom: none !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}

/* Gold accent line */
.banner-title-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 3px;
    background: linear-gradient(90deg, transparent, #ffb3c6, transparent);
    z-index: 1;
}

/* ========== SIDEBAR PREMIUM STYLING ========== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ff6b9d 0%, #e91e63 100%) !important;
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stMarkdown {
    color: #e8f4f8 !important;
}

/* File uploader trong sidebar */
div[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.05);
    border: 2px dashed #ffb3c6 !important;
    border-radius: 15px;
    padding: 20px;
    margin-top: 15px;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

div[data-testid="stFileUploader"]:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #ffc0cb !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(255, 179, 198, 0.3);
}

/* ========== TABS PREMIUM DESIGN ========== */
button[data-testid="stTab"] {
    background: linear-gradient(135deg, #ffffff 0%, #fff5f7 100%);
    border: 2px solid #ffd4dd;
    border-radius: 12px 12px 0 0 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 700;
    font-size: 1rem;
    color: #4a5568;
    padding: 15px 30px;
    margin-right: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

button[data-testid="stTab"]:hover {
    background: linear-gradient(135deg, #ffe8f0 0%, #ffd4dd 100%);
    color: #c2185b;
    border-color: #ff6b9d;
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(255, 107, 157, 0.2);
}

button[data-testid="stTab"][aria-selected="true"] {
    background: linear-gradient(135deg, #ff6b9d 0%, #ff85a1 100%) !important;
    color: #ffffff !important;
    border-color: #ffb3c6 !important;
    border-bottom: 3px solid #ffb3c6 !important;
    box-shadow: 0 8px 20px rgba(255, 107, 157, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transform: translateY(-3px);
}

/* ========== HEADINGS ========== */
h1, h2, h3, h4 {
    color: #1a2332 !important;
    font-weight: 700 !important;
}

h2 {
    color: #c2185b !important;
    border-bottom: 3px solid #ffb3c6;
    padding-bottom: 10px;
    margin-bottom: 20px !important;
}

h3 {
    color: #ff6b9d !important;
    border-bottom: 2px solid rgba(255, 179, 198, 0.3);
    padding-bottom: 8px;
    margin-bottom: 15px !important;
}

/* ========== METRIC CONTAINERS ========== */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #fff5f7 100%);
    border: 2px solid transparent;
    border-image: linear-gradient(135deg, #ffb3c6, #ff6b9d) 1;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.12),
                0 3px 10px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 35px rgba(255, 107, 157, 0.2),
                0 5px 15px rgba(255, 179, 198, 0.15);
}

/* Metric label */
div[data-testid="metric-container"] label {
    font-weight: 700 !important;
    color: #c2185b !important;
    font-size: 0.9rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Metric value */
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ff6b9d !important;
    font-weight: 900 !important;
    font-size: 2.2rem !important;
}

/* ========== BUTTONS PREMIUM ========== */
button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b9d 0%, #ff85a1 100%) !important;
    border: 2px solid #ffb3c6 !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 12px 30px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 157, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
    text-transform: uppercase;
    letter-spacing: 1px;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #e91e63 0%, #f06292 100%) !important;
    border-color: #ffc0cb !important;
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 10px 30px rgba(255, 107, 157, 0.4),
                0 5px 15px rgba(255, 179, 198, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

button[kind="primary"]:active {
    transform: translateY(0) scale(0.98);
}

/* ========== CONTAINERS & CARDS ========== */
div[data-testid="stContainer"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(0, 61, 130, 0.1);
}

/* Expander */
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 2px solid #ffd4dd;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

div[data-testid="stExpander"]:hover {
    border-color: #ff6b9d;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.15);
}

/* ========== DATAFRAMES ========== */
div[data-testid="stDataFrame"] {
    border: 2px solid #e0e6ed;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* ========== INFO/WARNING/ERROR BOXES ========== */
div[data-baseweb="notification"] {
    border-radius: 12px;
    border-left-width: 5px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 20px !important;
}

/* Info box */
div[data-baseweb="notification"][data-testid*="stInfo"] {
    background: linear-gradient(135deg, #ffe8f0 0%, #ffd4dd 100%);
    border-left-color: #ff6b9d !important;
}

/* Success box */
div[data-baseweb="notification"][data-testid*="stSuccess"] {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border-left-color: #28a745 !important;
}

/* Warning box */
div[data-baseweb="notification"][data-testid*="stWarning"] {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-left-color: #ffc107 !important;
}

/* Error box */
div[data-baseweb="notification"][data-testid*="stError"] {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    border-left-color: #dc3545 !important;
}

/* ========== DIVIDER ========== */
hr {
    border: none;
    height: 3px;
    background: linear-gradient(90deg, transparent, #ffb3c6, transparent);
    margin: 30px 0;
}

/* ========== PROGRESS BAR ========== */
div[data-testid="stProgress"] > div {
    background: linear-gradient(90deg, #ff6b9d, #ff85a1, #ffb3c6);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(255, 107, 157, 0.3);
}

/* ========== SPINNER ========== */
div[data-testid="stSpinner"] > div {
    border-top-color: #ffb3c6 !important;
}

/* ========== TOOLTIPS & CAPTIONS ========== */
.stCaption {
    color: #6b7280 !important;
    font-weight: 500 !important;
}

/* ========== RESPONSIVE ENHANCEMENTS ========== */
@media (max-width: 768px) {
    .banner-title-container {
        padding: 25px 20px;
    }

    .banner-title-container h1 {
        font-size: 2rem !important;
    }

    button[data-testid="stTab"] {
        padding: 10px 15px;
        font-size: 0.9rem;
    }
}

/* ========== SCROLL BAR ========== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f5f7fa;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff6b9d, #ff85a1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #e91e63, #f06292);
}

</style>
""", unsafe_allow_html=True)


# =========================
# HÀM GỌI GEMINI API (GIỮ NGUYÊN LOGIC)
# =========================

def get_ai_analysis(data_payload: dict, api_key: str) -> str:
    """
    Sử dụng Gemini API để phân tích chỉ số tài chính.
    """
    if not _GEMINI_OK:
        return "Lỗi: Thiếu thư viện google-genai (cần cài đặt: pip install google-genai)."

    client = genai.Client(api_key=api_key)

    sys_prompt = (
        "Bạn là chuyên gia phân tích tín dụng doanh nghiệp tại ngân hàng. "
        "Phân tích toàn diện dựa trên 14 chỉ số tài chính được cung cấp và PD nếu có. "
        "Nêu rõ: (1) Khả năng sinh lời, (2) Thanh khoản, (3) Cơ cấu nợ, (4) Hiệu quả hoạt động. "
        "Kết thúc bằng khuyến nghị in hoa: CHO VAY hoặc KHÔNG CHO VAY, kèm 2–3 điều kiện nếu CHO VAY. "
        "Viết bằng tiếng Việt súc tích, chuyên nghiệp."
    )
    
    # Gửi tên tiếng Việt dễ hiểu hơn cho AI
    user_prompt = "Bộ chỉ số tài chính và PD cần phân tích:\n" + str(data_payload) + "\n\nHãy phân tích và đưa ra khuyến nghị."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}
            ],
            config={"system_instruction": sys_prompt}
        )
        return response.text
    except APIError as e:
        return f"Lỗi gọi API Gemini: {e}"
    except Exception as e:
        return f"Lỗi không xác định: {e}"


# =========================
# TÍNH X1..X14 TỪ 3 SHEET (CDKT/BCTN/LCTT) - SỬ DỤNG TÊN TIẾNG VIỆT (GIỮ NGUYÊN)
# =========================

# Bảng ánh xạ Tên chỉ số tiếng Việt
COMPUTED_COLS = [
    "Biên Lợi nhuận Gộp (X1)", "Biên Lợi nhuận Tr.Thuế (X2)", "ROA Tr.Thuế (X3)", 
    "ROE Tr.Thuế (X4)", "Tỷ lệ Nợ/TTS (X5)", "Tỷ lệ Nợ/VCSH (X6)", 
    "Thanh toán Hiện hành (X7)", "Thanh toán Nhanh (X8)", "Khả năng Trả lãi (X9)", 
    "Khả năng Trả nợ Gốc (X10)", "Tỷ lệ Tiền/VCSH (X11)", "Vòng quay HTK (X12)", 
    "Kỳ thu tiền BQ (X13)", "Hiệu suất Tài sản (X14)"
]

# Alias các dòng quan trọng trong từng sheet (GIỮ NGUYÊN)
ALIAS_IS = {
    "doanh_thu_thuan": ["Doanh thu thuần", "Doanh thu bán hàng", "Doanh thu thuần về bán hàng và cung cấp dịch vụ"],
    "gia_von": ["Giá vốn hàng bán"],
    "loi_nhuan_gop": ["Lợi nhuận gộp"],
    "chi_phi_lai_vay": ["Chi phí lãi vay", "Chi phí tài chính (trong đó: chi phí lãi vay)"],
    "loi_nhuan_truoc_thue": ["Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Lợi nhuận trước thuế thu nhập DN"],
}
ALIAS_BS = {
    "tong_tai_san": ["Tổng tài sản"],
    "von_chu_so_huu": ["Vốn chủ sở hữu", "Vốn CSH"],
    "no_phai_tra": ["Nợ phải trả"],
    "tai_san_ngan_han": ["Tài sản ngắn hạn"],
    "no_ngan_han": ["Nợ ngắn hạn"],
    "hang_ton_kho": ["Hàng tồn kho"],
    "tien_tdt": ["Tiền và các khoản tương đương tiền", "Tiền và tương đương tiền"],
    "phai_thu_kh": ["Phải thu ngắn hạn của khách hàng", "Phải thu khách hàng"],
    "no_dai_han_den_han": ["Nợ dài hạn đến hạn trả", "Nợ dài hạn đến hạn"],
}
ALIAS_CF = {
    "khau_hao": ["Khấu hao TSCĐ", "Khấu hao", "Chi phí khấu hao"],
}

def _pick_year_cols(df: pd.DataFrame):
    """Chọn 2 cột năm gần nhất từ sheet (ưu tiên cột có nhãn là năm)."""
    numeric_years = []
    for c in df.columns[1:]:
        try:
            y = int(float(str(c).strip()))
            if 1990 <= y <= 2100:
                numeric_years.append((y, c))
        except Exception:
            continue
    if numeric_years:
        numeric_years.sort(key=lambda x: x[0])
        return numeric_years[-2][1], numeric_years[-1][1]
    # fallback: 2 cột cuối
    cols = df.columns[-2:]
    return cols[0], cols[1]

def _get_row_vals(df: pd.DataFrame, aliases: list[str]):
    """Tìm dòng theo alias. Trả về (prev, cur) theo 2 cột năm gần nhất."""
    label_col = df.columns[0]
    prev_col, cur_col = _pick_year_cols(df)
    mask = False
    for alias in aliases:
        mask = mask | df[label_col].astype(str).str.contains(alias, case=False, na=False)
    rows = df[mask]
    if rows.empty:
        return np.nan, np.nan
    row = rows.iloc[0]

    def to_num(x):
        try:
            # Xóa dấu phẩy, khoảng trắng
            return float(str(x).replace(",", "").replace(" ", ""))
        except Exception:
            return np.nan

    return to_num(row[prev_col]), to_num(row[cur_col])

def compute_ratios_from_three_sheets(xlsx_file) -> pd.DataFrame:
    """Đọc 3 sheet CDKT/BCTN/LCTT và tính X1..X14 theo yêu cầu."""
    bs = pd.read_excel(xlsx_file, sheet_name="CDKT", engine="openpyxl")
    is_ = pd.read_excel(xlsx_file, sheet_name="BCTN", engine="openpyxl")
    cf = pd.read_excel(xlsx_file, sheet_name="LCTT", engine="openpyxl")

    # ---- Tính toán các biến số tài chính (GIỮ NGUYÊN CÁCH TÍNH)
    DTT_prev, DTT_cur         = _get_row_vals(is_, ALIAS_IS["doanh_thu_thuan"])
    GVHB_prev, GVHB_cur = _get_row_vals(is_, ALIAS_IS["gia_von"])
    LNG_prev, LNG_cur         = _get_row_vals(is_, ALIAS_IS["loi_nhuan_gop"])
    LNTT_prev, LNTT_cur = _get_row_vals(is_, ALIAS_IS["loi_nhuan_truoc_thue"])
    LV_prev, LV_cur           = _get_row_vals(is_, ALIAS_IS["chi_phi_lai_vay"])
    TTS_prev, TTS_cur           = _get_row_vals(bs, ALIAS_BS["tong_tai_san"])
    VCSH_prev, VCSH_cur         = _get_row_vals(bs, ALIAS_BS["von_chu_so_huu"])
    NPT_prev, NPT_cur           = _get_row_vals(bs, ALIAS_BS["no_phai_tra"])
    TSNH_prev, TSNH_cur         = _get_row_vals(bs, ALIAS_BS["tai_san_ngan_han"])
    NNH_prev, NNH_cur           = _get_row_vals(bs, ALIAS_BS["no_ngan_han"])
    HTK_prev, HTK_cur           = _get_row_vals(bs, ALIAS_BS["hang_ton_kho"])
    Tien_prev, Tien_cur         = _get_row_vals(bs, ALIAS_BS["tien_tdt"])
    KPT_prev, KPT_cur           = _get_row_vals(bs, ALIAS_BS["phai_thu_kh"])
    NDH_prev, NDH_cur           = _get_row_vals(bs, ALIAS_BS["no_dai_han_den_han"])
    KH_prev, KH_cur = _get_row_vals(cf, ALIAS_CF["khau_hao"])

    if pd.notna(GVHB_cur): GVHB_cur = abs(GVHB_cur)
    if pd.notna(LV_cur):      LV_cur     = abs(LV_cur)
    if pd.notna(KH_cur):      KH_cur     = abs(KH_cur)

    def avg(a, b):
        if pd.isna(a) and pd.isna(b): return np.nan
        if pd.isna(a): return b
        if pd.isna(b): return a
        return (a + b) / 2.0
    TTS_avg    = avg(TTS_cur,    TTS_prev)
    VCSH_avg = avg(VCSH_cur, VCSH_prev)
    HTK_avg    = avg(HTK_cur,    HTK_prev)
    KPT_avg    = avg(KPT_cur,    KPT_prev)

    EBIT_cur = (LNTT_cur + LV_cur) if (pd.notna(LNTT_cur) and pd.notna(LV_cur)) else np.nan
    NDH_cur = 0.0 if pd.isna(NDH_cur) else NDH_cur

    def div(a, b):
        return np.nan if (b is None or pd.isna(b) or b == 0) else a / b

    # ==== TÍNH X1..X14 ==== (GIỮ NGUYÊN CÔNG THỨC)
    X1  = div(LNG_cur, DTT_cur)
    X2  = div(LNTT_cur, DTT_cur)
    X3  = div(LNTT_cur, TTS_avg)
    X4  = div(LNTT_cur, VCSH_avg)
    X5  = div(NPT_cur,  TTS_cur)
    X6  = div(NPT_cur,  VCSH_cur)
    X7  = div(TSNH_cur, NNH_cur)
    X8  = div((TSNH_cur - HTK_cur) if pd.notna(TSNH_cur) and pd.notna(HTK_cur) else np.nan, NNH_cur)
    X9  = div(EBIT_cur, LV_cur)
    X10 = div((EBIT_cur + (KH_cur if pd.notna(KH_cur) else 0.0)), (LV_cur + NDH_cur) if pd.notna(LV_cur) else np.nan)
    X11 = div(Tien_cur, VCSH_cur)
    X12 = div(GVHB_cur, HTK_avg)
    turnover = div(DTT_cur, KPT_avg)
    X13 = div(365.0, turnover) if pd.notna(turnover) and turnover != 0 else np.nan
    X14 = div(DTT_cur, TTS_avg)

    # Khởi tạo DataFrame với tên cột tiếng Việt mới
    ratios = pd.DataFrame([[X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11, X12, X13, X14]],
                          columns=COMPUTED_COLS)
                          
    # Thêm cột X_1..X_14 ẩn để phục vụ việc dự báo mô hình
    ratios[[f"X_{i}" for i in range(1, 15)]] = ratios.values
    return ratios

# =========================
# UI & TRAIN MODEL
# =========================
np.random.seed(0)

# ========================================
# PREMIUM BANKING HEADER
# ========================================
st.markdown('<div class="banner-title-container">', unsafe_allow_html=True)

# Thêm logo nếu có (optional)
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo-agribank.jpg", width=120)
    except:
        st.markdown("🏦")

with col_title:
    st.markdown("""
        <h1 style='margin: 0; padding: 0;'>CHƯƠNG TRÌNH ĐÁNH GIÁ RỦI RO TÍN DỤNG</h1>
        <h3 style='margin: 5px 0 0 0;'>Dự báo Xác suất Vỡ nợ KHDN (PD) & Phân tích AI Chuyên sâu</h3>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Load dữ liệu huấn luyện (CSV có default, X_1..X_14) - Giữ nguyên logic load data
try:
    df = pd.read_csv('DATASET.csv', encoding='latin-1')
    # Tên cột cho việc huấn luyện (phải giữ nguyên X_1..X_14)
    MODEL_COLS = [f"X_{i}" for i in range(1, 15)]
except Exception:
    df = None

# DI CHUYỂN UPLOADER VỀ ĐẦU SIDEBAR (Không còn selectbox)
uploaded_file = st.sidebar.file_uploader("📂 Tải CSV Dữ liệu Huấn luyện", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin-1')
    MODEL_COLS = [f"X_{i}" for i in range(1, 15)]
    
# Định nghĩa các Tabs
# ------------------------------------------------------------------------------------------------
# THAY ĐỔI 4: Vị trí Tabs được giữ nguyên, CSS mới sẽ đảm bảo Tabs có màu
# ------------------------------------------------------------------------------------------------
tab_predict, tab_build, tab_goal = st.tabs([
    "🚀 Sử dụng mô hình để dự báo", 
    "🛠️ Xây dựng mô hình", 
    "🎯 Mục tiêu của mô hình"
])

# --- Logic xử lý khi chưa có data huấn luyện ---
if df is None:
    st.sidebar.info("💡 Hãy tải file CSV huấn luyện (có cột 'default' và X_1...X_14) để xây dựng mô hình.")
    
    # Logic cho các tab khi thiếu data huấn luyện
    with tab_predict:
        st.header("⚡ Dự báo PD & Phân tích AI cho Hồ sơ mới")
        st.warning("⚠️ **Không thể dự báo PD**. Vui lòng tải file **CSV Dữ liệu Huấn luyện** ở sidebar để xây dựng mô hình Logistic Regression.")
        up_xlsx = st.file_uploader("Tải **ho_so_dn.xlsx**", type=["xlsx"], key="ho_so_dn")
        if up_xlsx is None:
            st.info("Hãy tải **ho_so_dn.xlsx** (đủ 3 sheet) để tính X1…X14 và phân tích AI.")

    with tab_goal:
        st.header("🎯 Mục tiêu của Mô hình")
        st.info("Ứng dụng này cần dữ liệu huấn luyện để bắt đầu hoạt động.")
    
    with tab_build:
          st.header("🛠️ Xây dựng & Đánh giá Mô hình LogReg")
          st.error("❌ **Không thể xây dựng mô hình**. Vui lòng tải file **CSV Dữ liệu Huấn luyện** ở sidebar để bắt đầu.")
          
    st.stop()
# ------------------------------------------------------------------------------------------------

# Hiển thị trạng thái thư viện AI (Sử dụng cột để bố trí đẹp hơn)
col_ai_status, col_date = st.columns([3, 1])
with col_ai_status:
    ai_status = ("✅ sẵn sàng (cần 'GEMINI_API_KEY' trong Secrets)" if _GEMINI_OK else "⚠️ Thiếu thư viện google-genai.")
    st.caption(f"🔎 Trạng thái Gemini AI: **<span style='color: #004c99; font-weight: bold;'>{ai_status}</span>**", unsafe_allow_html=True)
with col_date:
    st.caption(f"📅 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.divider()

# Kiểm tra cột cần thiết
required_cols = ['default'] + MODEL_COLS
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ Thiếu cột: **{missing}**. Vui lòng kiểm tra lại file CSV huấn luyện.")
    st.stop()


# Train model (GIỮ NGUYÊN)
X = df[MODEL_COLS] # Chỉ lấy các cột X_1..X_14
y = df['default'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
model = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced", solver="lbfgs")
model.fit(X_train, y_train)

# Dự báo & đánh giá (GIỮ NGUYÊN)
y_pred_in = model.predict(X_train)
y_proba_in = model.predict_proba(X_train)[:, 1]
y_pred_out = model.predict(X_test)
y_proba_out = model.predict_proba(X_test)[:, 1]

metrics_in = {
    "accuracy_in": accuracy_score(y_train, y_pred_in),
    "precision_in": precision_score(y_train, y_pred_in, zero_division=0),
    "recall_in": recall_score(y_train, y_pred_in, zero_division=0),
    "f1_in": f1_score(y_train, y_pred_in, zero_division=0),
    "auc_in": roc_auc_score(y_train, y_proba_in),
}
metrics_out = {
    "accuracy_out": accuracy_score(y_test, y_pred_out),
    "precision_out": precision_score(y_test, y_pred_out, zero_division=0),
    "recall_out": recall_score(y_test, y_pred_out, zero_division=0),
    "f1_out": f1_score(y_test, y_pred_out, zero_division=0),
    "auc_out": roc_auc_score(y_test, y_proba_out),
}

# --- CÁC PHẦN UI DỰA TRÊN TABS ---

with tab_goal:
    st.header("🎯 Mục tiêu của Mô hình")
    st.markdown("**Dự báo xác suất vỡ nợ (PD) của khách hàng doanh nghiệp** dựa trên bộ chỉ số $\text{X1}–\text{X14}$ (tính từ Bảng Cân đối Kế toán, Báo cáo Kết quả Kinh doanh và Báo cáo Lưu chuyển Tiền tệ).")
    
    with st.expander("🖼️ Mô tả trực quan mô hình"):
        st.markdown("### Các hình ảnh minh họa cho mô hình Hồi quy Logistic và quy trình đánh giá rủi ro")

        # Hiển thị hình ảnh trong columns để layout đẹp hơn
        col_img1, col_img2 = st.columns(2)

        for idx, img in enumerate(["hinh2.jpg", "LogReg_1.png", "hinh3.png"]):
            try:
                if idx == 0:
                    with col_img1:
                        st.image(img, caption=f"Mô tả {idx+1}: Quy trình đánh giá", use_container_width=True)
                elif idx == 1:
                    with col_img2:
                        st.image(img, caption=f"Mô tả {idx+1}: Mô hình Logistic Regression", use_container_width=True)
                else:
                    st.image(img, caption=f"Mô tả {idx+1}: Kết quả phân tích", use_container_width=True)
            except Exception:
                # Nếu không tìm thấy file, hiển thị message thân thiện
                st.info(f"📊 Hình ảnh minh họa '{img}' sẽ được hiển thị ở đây")

with tab_build:
    st.header("🛠️ Xây dựng & Đánh giá Mô hình LogReg")
    st.info("Mô hình Hồi quy Logistic đã được huấn luyện trên **20% dữ liệu Test (chưa thấy)**.")
    
    # Hiển thị Metrics quan trọng bằng st.metric
    st.subheader("1. Tổng quan Kết quả Đánh giá (Test Set)")
    col_acc, col_auc, col_f1 = st.columns(3)
    
    col_acc.metric(label="Độ chính xác (Accuracy)", value=f"{metrics_out['accuracy_out']:.2%}")
    # Đảm bảo logic delta vẫn đúng
    col_auc.metric(label="Diện tích dưới đường cong (AUC)", value=f"{metrics_out['auc_out']:.3f}", delta=f"{metrics_in['auc_in'] - metrics_out['auc_out']:.3f}", delta_color="inverse")
    col_f1.metric(label="Điểm F1-Score", value=f"{metrics_out['f1_out']:.3f}")
    
    st.divider()

    # Thống kê chi tiết & Biểu đồ
    st.subheader("2. Dữ liệu và Trực quan hóa")
    
    with st.expander("📊 Thống kê Mô tả và Dữ liệu Mẫu"):
        st.markdown("##### Thống kê Mô tả các biến $X_1..X_{14}$")
        st.dataframe(df[MODEL_COLS].describe().style.format("{:.4f}"))
        st.markdown("##### 6 Dòng dữ liệu huấn luyện mẫu (Đầu/Cuối)")
        st.dataframe(pd.concat([df.head(3), df.tail(3)]))

    st.markdown("##### Biểu đồ Phân tán (Scatter Plot) với Đường Hồi quy Logisitc")
    col = st.selectbox('🔍 Chọn biến X muốn vẽ', options=MODEL_COLS, index=0, key="select_build_col")
    
    # Biểu đồ Scatter Plot và Đường Hồi quy Logisitc (GIỮ NGUYÊN LOGIC, CẢI THIỆN MÀU SẮC)
    if col in df.columns:
        try:
            # Dùng Streamlit.pyplot với theme banking hiện đại
            fig, ax = plt.subplots(figsize=(12, 7))

            # Set background color
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')

            # Scatter plot với màu sắc pink rose theme
            sns.scatterplot(data=df, x=col, y='default', alpha=0.65, ax=ax, hue='default',
                          palette=['#ff6b9d', '#ffb3c6'], s=80, edgecolor='white', linewidth=0.5)

            # Vẽ đường logistic regression theo 1 biến
            x_range = np.linspace(df[col].min(), df[col].max(), 100).reshape(-1, 1)
            X_temp = df[[col]].copy()
            y_temp = df['default']
            lr_temp = LogisticRegression(max_iter=1000)
            lr_temp.fit(X_temp, y_temp)
            x_test = pd.DataFrame({col: x_range[:, 0]})
            y_curve = lr_temp.predict_proba(x_test)[:, 1]
            ax.plot(x_range, y_curve, color='#c2185b', linewidth=4, label='Đường LogReg',
                   linestyle='-', alpha=0.9)

            # Styling cho tiêu đề và labels
            ax.set_title(f'Quan hệ giữa {col} và Xác suất Vỡ nợ', fontsize=16, fontweight='bold', color='#c2185b', pad=20)
            ax.set_ylabel('Xác suất Default (0: Non-Default, 1: Default)', fontsize=13, fontweight='600', color='#4a5568')
            ax.set_xlabel(col, fontsize=13, fontweight='600', color='#4a5568')

            # Grid styling
            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.8, color='#ff6b9d')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#d0d0d0')
            ax.spines['bottom'].set_color('#d0d0d0')

            # Legend styling
            legend = ax.legend(title='Default Status', title_fontsize=11, fontsize=10,
                             frameon=True, fancybox=True, shadow=True)
            legend.get_frame().set_facecolor('#f8f9fa')
            legend.get_frame().set_alpha(0.9)

            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Lỗi khi vẽ biểu đồ: {e}")
    else:
        st.warning("Biến không tồn tại trong dữ liệu.")
    
    st.divider()

    st.subheader("3. Ma trận Nhầm lẫn và Bảng Metrics Chi tiết")
    col_cm, col_metrics_table = st.columns(2)
    
    with col_cm:
        st.markdown("##### Ma trận Nhầm lẫn (Test Set)")
        cm = confusion_matrix(y_test, y_pred_out)

        # Tạo custom colormap cho pink rose theme
        from matplotlib.colors import LinearSegmentedColormap
        colors_pink = ['#fff5f7', '#ffe8f0', '#ffd4dd', '#ff85a1', '#ff6b9d']
        n_bins = 100
        cmap_pink = LinearSegmentedColormap.from_list('pink_rose', colors_pink, N=n_bins)

        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Non-Default (0)', 'Default (1)'])
        fig2, ax = plt.subplots(figsize=(7, 7))
        fig2.patch.set_facecolor('#f8f9fa')

        disp.plot(ax=ax, cmap=cmap_pink, colorbar=True)

        # Styling
        ax.set_title('Ma trận Nhầm lẫn', fontsize=14, fontweight='bold', color='#c2185b', pad=15)
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='600', color='#4a5568')
        ax.set_ylabel('True Label', fontsize=12, fontweight='600', color='#4a5568')

        st.pyplot(fig2)
        plt.close(fig2)
        
    with col_metrics_table:
        st.markdown("##### Bảng Metrics Chi tiết")
        dt = pd.DataFrame({
            "Metric": ["Accuracy", "Precision", "Recall", "F1-Score", "AUC"],
            "Train Set": [metrics_in['accuracy_in'], metrics_in['precision_in'], metrics_in['recall_in'], metrics_in['f1_in'], metrics_in['auc_in']],
            "Test Set": [metrics_out['accuracy_out'], metrics_out['precision_out'], metrics_out['recall_out'], metrics_out['f1_out'], metrics_out['auc_out']],
        }).set_index("Metric")
        # Thêm styling để làm nổi bật kết quả tốt nhất
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: #e0f0ff' if v else '' for v in is_max]

        st.dataframe(dt.style.format("{:.4f}").apply(highlight_max, axis=1), use_container_width=True)

with tab_predict:
    # Trang này được hiển thị mặc định
    st.header("⚡ Dự báo PD & Phân tích AI cho Hồ sơ mới")
    
    # Sử dụng st.container và st.expander để tổ chức khu vực upload
    input_container = st.container(border=True)
    with input_container:
        st.markdown("##### 📥 Tải lên Hồ sơ Doanh nghiệp (Excel)")
        st.caption("File phải có đủ **3 sheet**: **CDKT** (Bảng Cân đối Kế toán) ; **BCTN** (Báo cáo Kết quả Kinh doanh) ; **LCTT** (Báo cáo Lưu chuyển Tiền tệ).")
        up_xlsx = st.file_uploader("Tải **ho_so_dn.xlsx**", type=["xlsx"], key="ho_so_dn_main", label_visibility="collapsed")
    
    if up_xlsx is not None:
        # Tính X1..X14 từ 3 sheet (GIỮ NGUYÊN)
        try:
            # Hiển thị thanh tiến trình giả lập (thêm hiệu ứng động)
            with st.spinner('Đang đọc và xử lý dữ liệu tài chính...'):
                ratios_df = compute_ratios_from_three_sheets(up_xlsx)
            
            # Tách riêng 14 cột tiếng Việt (hiển thị) và 14 cột tiếng Anh (dự báo)
            # ratios_display là DataFrame 1 cột: Index (Tên chỉ số) | Giá trị
            ratios_display = ratios_df[COMPUTED_COLS].T.rename(columns={0: 'Giá trị'})
            ratios_predict = ratios_df[MODEL_COLS]
            
        except Exception as e:
            st.error(f"❌ Lỗi tính chỉ số tài chính: Vui lòng kiểm tra lại cấu trúc 3 sheet trong file Excel. Chi tiết lỗi: {e}")
            st.stop()

        st.divider()
        st.markdown("### 1. 🔢 Các Chỉ số Tài chính Đã tính")
        
        # Tạo payload data cho AI (Sử dụng tên tiếng Việt)
        data_for_ai = ratios_display.to_dict()['Giá trị']
        
        # (Tuỳ chọn) dự báo PD nếu mô hình đã huấn luyện đúng cấu trúc X_1..X_14
        probs = np.nan
        preds = np.nan
        # Kiểm tra mô hình có sẵn sàng dự báo không (đã train và cột khớp)
        if set(X.columns) == set(ratios_predict.columns):
            try:
                # Đảm bảo thứ tự cột cho predict đúng như thứ tự cột huấn luyện
                probs = model.predict_proba(ratios_predict[X.columns])[:, 1]
                preds = (probs >= 0.5).astype(int)
                # Thêm PD vào payload AI
                data_for_ai['Xác suất Vỡ nợ (PD)'] = probs[0]
                data_for_ai['Dự đoán PD'] = "Default (Vỡ nợ)" if preds[0] == 1 else "Non-Default (Không vỡ nợ)"
            except Exception as e:
                # Nếu có lỗi dự báo, chỉ cảnh báo, không dừng app
                st.warning(f"Không dự báo được PD: {e}")
        
        # ------------------------------------------------------------------------------------------------
        # ĐIỀU CHỈNH CỦA CHUYÊN GIA PYTHON: Bỏ .T để hiển thị đúng Tên Biến | Con số
        # ------------------------------------------------------------------------------------------------
        pd_col_1, pd_col_2, pd_col_pd = st.columns([2, 2, 1]) # Chia làm 3 cột, 2 cột giữa hiển thị ratios, 1 cột cuối hiển thị PD
        
        ratios_list = ratios_display.index.tolist()
        mid_point = len(ratios_list) // 2
        # ratios_display đã có cấu trúc đúng: Index (Tên biến) | Giá trị (Con số)
        ratios_part1 = ratios_display.iloc[:mid_point]
        ratios_part2 = ratios_display.iloc[mid_point:]
        
        # Hàm styling (GIỮ NGUYÊN)
        def color_ratios(val):
            """Ánh xạ màu dựa trên tên chỉ số và giá trị (tạm thời để hiển thị đẹp)"""
            # Chỉ số Thanh khoản (X7, X8) - Green/Yellow
            if "Thanh toán" in val.name and val.values[0] < 1.0: return ['background-color: #ffcccc' for _ in val] # Dưới 1: Báo động đỏ
            if "Thanh toán" in val.name and val.values[0] > 1.5: return ['background-color: #ccffcc' for _ in val] # Trên 1.5: Tốt
            # Chỉ số Nợ (X5, X6) - Red/Green
            if "Tỷ lệ Nợ/" in val.name and val.values[0] > 1.0: return ['background-color: #ffcccc' for _ in val] # Trên 1: Rủi ro cao
            if "Tỷ lệ Nợ/" in val.name and val.values[0] < 0.5: return ['background-color: #ccffcc' for _ in val] # Dưới 0.5: Tốt
            # Chỉ số Sinh lời (X1, X2, X3, X4) - Green/Yellow
            if "Lợi nhuận" in val.name or "ROA" in val.name or "ROE" in val.name:
                if val.values[0] <= 0: return ['background-color: #ffcccc' for _ in val]
                if val.values[0] > 0.1: return ['background-color: #ccffcc' for _ in val]
            return [''] * len(val)

        with pd_col_1:
             # Đảm bảo hiển thị Tên biến | Giá trị
             st.markdown("##### **Chỉ số Tài chính (1/2)**") 
             st.dataframe(
                 ratios_part1.style.apply(color_ratios, axis=1).format("{:.4f}").set_properties(**{'font-size': '14px'}),
                 use_container_width=True
             )

        with pd_col_2:
            # Đảm bảo hiển thị Tên biến | Giá trị
            st.markdown("##### **Chỉ số Tài chính (2/2)**")
            st.dataframe(
                ratios_part2.style.apply(color_ratios, axis=1).format("{:.4f}").set_properties(**{'font-size': '14px'}),
                use_container_width=True
            )
        
        with pd_col_pd:
            pd_value = f"{probs[0]:.2%}" if pd.notna(probs) else "N/A"
            pd_delta = "⬆️ Rủi ro cao" if pd.notna(preds) and preds[0] == 1 else "⬇️ Rủi ro thấp"
            
            st.metric(
                label="**Xác suất Vỡ nợ (PD)**",
                value=pd_value,
                delta=pd_delta if pd.notna(probs) else None,
                # Đảo ngược màu sắc delta cho PD: Rủi ro cao là màu đỏ (inverse), rủi ro thấp là màu xanh (normal)
                delta_color=("inverse" if pd.notna(preds) and preds[0] == 1 else "normal")
            )
        # ------------------------------------------------------------------------------------------------

        st.divider()

        # ========================================
        # THÊM BIỂU ĐỒ VISUALIZATION CHO CÁC CHỈ SỐ TÀI CHÍNH
        # ========================================
        st.markdown("### 2. 📊 Trực quan hóa Các Chỉ số Tài chính")

        # Tạo 2 cột cho 2 loại biểu đồ
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### 📈 Biểu đồ Cột - Giá trị các Chỉ số")
            # Tạo bar chart
            fig_bar, ax_bar = plt.subplots(figsize=(8, 10))
            fig_bar.patch.set_facecolor('#fff5f7')
            ax_bar.set_facecolor('#ffffff')

            # Chuẩn bị data cho bar chart
            indicators = ratios_display.index.tolist()
            values = ratios_display['Giá trị'].values

            # Tạo màu gradient cho các bars
            colors = plt.cm.RdPu(np.linspace(0.3, 0.9, len(indicators)))

            # Vẽ horizontal bar chart
            bars = ax_bar.barh(indicators, values, color=colors, edgecolor='white', linewidth=1.5)

            # Thêm giá trị vào cuối mỗi bar
            for i, (bar, val) in enumerate(zip(bars, values)):
                width = bar.get_width()
                ax_bar.text(width, bar.get_y() + bar.get_height()/2,
                           f' {val:.3f}', ha='left', va='center',
                           fontsize=9, fontweight='600', color='#c2185b')

            # Styling
            ax_bar.set_xlabel('Giá trị', fontsize=12, fontweight='600', color='#4a5568')
            ax_bar.set_title('Các Chỉ số Tài chính', fontsize=14, fontweight='bold', color='#c2185b', pad=15)
            ax_bar.grid(True, alpha=0.2, linestyle='--', linewidth=0.8, color='#ff6b9d', axis='x')
            ax_bar.spines['top'].set_visible(False)
            ax_bar.spines['right'].set_visible(False)
            ax_bar.spines['left'].set_color('#d0d0d0')
            ax_bar.spines['bottom'].set_color('#d0d0d0')

            # Điều chỉnh layout để labels không bị cắt
            plt.tight_layout()
            st.pyplot(fig_bar)
            plt.close(fig_bar)

        with chart_col2:
            st.markdown("#### 🎯 Biểu đồ Radar - Phân tích Đa chiều")
            # Tạo radar chart (spider chart)
            fig_radar = plt.figure(figsize=(10, 10))
            fig_radar.patch.set_facecolor('#fff5f7')
            ax_radar = fig_radar.add_subplot(111, projection='polar')

            # Chuẩn bị data cho radar chart
            # Normalize các giá trị về khoảng 0-1 để dễ visualize
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            normalized_values = scaler.fit_transform(values.reshape(-1, 1)).flatten()

            # Tạo các góc cho mỗi chỉ số
            angles = np.linspace(0, 2 * np.pi, len(indicators), endpoint=False).tolist()
            normalized_values = normalized_values.tolist()

            # Đóng vòng tròn
            angles += angles[:1]
            normalized_values += normalized_values[:1]

            # Vẽ radar chart
            ax_radar.plot(angles, normalized_values, 'o-', linewidth=2.5, color='#ff6b9d', label='Chỉ số')
            ax_radar.fill(angles, normalized_values, alpha=0.25, color='#ffb3c6')

            # Thêm labels
            ax_radar.set_xticks(angles[:-1])
            # Rút ngắn tên chỉ số để dễ đọc
            short_labels = [label.split('(')[0].strip()[:20] for label in indicators]
            ax_radar.set_xticklabels(short_labels, size=8, color='#4a5568', fontweight='600')

            # Styling
            ax_radar.set_ylim(0, 1)
            ax_radar.set_title('Phân tích Đa chiều các Chỉ số\n(Normalized 0-1)',
                              fontsize=14, fontweight='bold', color='#c2185b', pad=20)
            ax_radar.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, color='#ff6b9d')
            ax_radar.set_facecolor('#ffffff')

            plt.tight_layout()
            st.pyplot(fig_radar)
            plt.close(fig_radar)

        # Thêm expander với thông tin bổ sung
        with st.expander("ℹ️ Giải thích về Biểu đồ"):
            st.markdown("""
            **Biểu đồ Cột (Bar Chart):**
            - Hiển thị giá trị thực tế của từng chỉ số tài chính
            - Màu sắc gradient từ nhạt đến đậm để dễ phân biệt
            - Giá trị cụ thể được hiển thị bên cạnh mỗi cột

            **Biểu đồ Radar (Spider Chart):**
            - Hiển thị cân bằng tổng thể giữa các chỉ số
            - Giá trị được chuẩn hóa về thang 0-1 để dễ so sánh
            - Diện tích vùng phủ thể hiện độ mạnh của các chỉ số
            - Hình dạng đều = tốt, hình dạng lệch = cần cân bằng
            """)

        st.divider()

        # Khu vực Phân tích AI
        st.markdown("### 3. 🧠 Phân tích AI & Khuyến nghị Tín dụng")
        
        ai_container = st.container(border=True)
        with ai_container:
            st.markdown("Sử dụng AI để phân tích toàn diện các chỉ số và đưa ra khuyến nghị chuyên nghiệp.")
            
            if st.button("✨ Yêu cầu AI Phân tích & Đề xuất", use_container_width=True, type="primary"):
                # Kiểm tra API Key: ưu tiên lấy từ secrets
                api_key = st.secrets.get("GEMINI_API_KEY") 
                
                if api_key:
                    # Thêm thanh tiến trình đẹp mắt
                    progress_bar = st.progress(0, text="Đang gửi dữ liệu và chờ Gemini phân tích...")
                    for percent_complete in range(100):
                        import time
                        time.sleep(0.01) # Giả lập thời gian xử lý
                        progress_bar.progress(percent_complete + 1, text=f"Đang gửi dữ liệu và chờ Gemini phân tích... {percent_complete+1}%")
                    
                    ai_result = get_ai_analysis(data_for_ai, api_key)
                    progress_bar.empty() # Xóa thanh tiến trình
                    
                    st.markdown("**Kết quả Phân tích Chi tiết từ Gemini AI:**")
                    
                    if "KHÔNG CHO VAY" in ai_result.upper():
                        st.error("🚨 **KHUYẾN NGHỊ CUỐI CÙNG: KHÔNG CHO VAY**")
                        st.snow() 
                    elif "CHO VAY" in ai_result.upper():
                        st.success("✅ **KHUYẾN NGHỊ CUỐI CÙNG: CHO VAY**")
                        st.balloons() 
                    else:
                        st.info("💡 **KHUYẾN NGHỊ CUỐI CÙNG**")
                        
                    st.info(ai_result)
                else:
                    st.error("❌ **Lỗi Khóa API**: Không tìm thấy Khóa API. Vui lòng cấu hình Khóa **'GEMINI_API_KEY'** trong Streamlit Secrets.")

    else:
        st.info("Hãy tải **ho_so_dn.xlsx** (đủ 3 sheet) để tính X1…X14, dự báo PD và phân tích AI.")

# ========================================
# PREMIUM BANKING FOOTER
# ========================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 1])

with footer_col1:
    st.markdown("""
    <div style='padding: 15px; text-align: left;'>
        <h4 style='color: #ff6b9d; margin-bottom: 10px;'>🏦 Chương Trình Đánh Giá Rủi Ro Tín Dụng</h4>
        <p style='color: #6b7280; font-size: 0.9rem; margin: 5px 0;'>
            Giải pháp AI tiên tiến cho phân tích tài chính doanh nghiệp
        </p>
        <p style='color: #6b7280; font-size: 0.85rem; margin: 5px 0;'>
            Powered by <strong>Gemini AI</strong> & <strong>Machine Learning</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("""
    <div style='padding: 15px; text-align: left;'>
        <h4 style='color: #ff6b9d; margin-bottom: 10px;'>📊 Tính Năng Chính</h4>
        <ul style='color: #6b7280; font-size: 0.85rem; margin: 5px 0; padding-left: 20px;'>
            <li>Phân tích 14 chỉ số tài chính tự động</li>
            <li>Dự báo xác suất vỡ nợ (PD) chính xác</li>
            <li>Khuyến nghị tín dụng từ Gemini AI</li>
            <li>Trực quan hóa dữ liệu chuyên nghiệp</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown(f"""
    <div style='padding: 15px; text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 10px;'>💖</div>
        <p style='color: #ffb3c6; font-weight: 700; font-size: 0.9rem; margin: 5px 0;'>
            SWEET ANALYTICS
        </p>
        <p style='color: #6b7280; font-size: 0.75rem;'>
            Version 2.0 Premium
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align: center; padding: 20px; margin-top: 20px;
            background: linear-gradient(135deg, #ff6b9d 0%, #ff85a1 100%);
            border-radius: 15px; box-shadow: 0 4px 15px rgba(255, 107, 157, 0.2);'>
    <p style='color: #ffffff; margin: 5px 0; font-size: 0.9rem; font-weight: 600;'>
        © {datetime.now().year} Credit Risk Assessment System | Developed with ❤️ using Streamlit
    </p>
    <p style='color: #fff0f5; margin: 5px 0; font-size: 0.85rem;'>
        🔒 Secure • 🚀 Fast • 🎯 Accurate • ✨ AI-Powered
    </p>
</div>
""", unsafe_allow_html=True)

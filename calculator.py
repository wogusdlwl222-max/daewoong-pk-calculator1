import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

# 앱 제목 및 레이아웃 설정
st.set_page_config(page_title="Formulation & PK 통합 계산기", layout="wide")

# =========================================================================
# 🎨 글로벌 메디컬 스타일 전용 커스텀 CSS 인젝션 (클라우드 다크테마 강제 방어)
# =========================================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        /* 메인 백그라운드 및 기본 서체 고정 */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f8fafc !important;
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
        }
        
        /* 인풋 상자 전체 라벨 가독성 블랙 교정 */
        div[data-testid="stWidgetLabel"] p {
            color: #1e293b !important;
            font-weight: 700 !important;
            font-size: 14px !important;
        }
        
        /* 인풋 박스 내부 텍스트와 숫자는 무조건 진한 블랙으로 고정 */
        .stNumberInput div div input {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            background-color: #ffffff !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            color: #1e293b !important;
        }
        
        /* 탭 바 전체 레이아웃 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #ffffff;
            padding: 8px 16px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            margin-bottom: 20px;
        }
        
        /* 기본 선택 안 된 일반 탭 스타일 및 글씨색 선명화 */
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            white-space: pre-wrap;
            background-color: #f1f5f9;
            border-radius: 6px;
            color: #334155 !important;
            font-weight: 500;
            padding: 0px 20px;
            transition: all 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e2e8f0;
            color: #0f172a !important;
        }
        
        /* 활성화된(선택된) 탭 제목 글씨를 선명한 화이트로 강제 고정 */
        .stTabs [aria-selected="true"] {
            background-color: #002b5c !important;
            box-shadow: 0 4px 6px rgba(0,43,92,0.15);
        }
        .stTabs [aria-selected="true"] span, 
        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] div {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        /* 안내 상자 */
        .guide-box {
            background: linear-gradient(135deg, #f0f4f8 0%, #e6eef5 100%);
            padding: 18px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-size: 13.5px;
            color: #1e293b;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        
        /* 데이터프레임 가독성 폰트 제어 */
        div[data-testid="stDataFrame"] table td {
            color: #000000 !important;
            font-size: 13px !important;
        }
        div[data-testid="stDataFrame"] table th {
            background-color: #f1f5f9 !important;
            color: #1e293b !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)

# 💡 상단 메인 블루 헤더 내부 서브타이틀 글씨색을 순수 span 태그를 써서 강제 쌩화이트(#ffffff) 박멸 완료!
st.markdown("""
    <div style="background: linear-gradient(135deg, #002b5c 0%, #0056b3 100%); padding: 35px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">🧪 Formulation & PK Intelligence Integrated Platform</h1>
        <div style="margin-top: 14px;">
            <span style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 15px; font-weight: 400; letter-spacing: 0.5px; opacity: 1.0 !important;">
                Daewoong Formulation Planning Team • 실무용 예측 시뮬레이터
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 🗂️ 탭 정의부
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "다회 투여 축적률 및 SS 예측", 
    "Flip-Flop Kinetics 제형 방출 역학 분석", 
    "HED 역산기 (인간 용량 ➡️ 동물 투여 용량 예측)",
    "임상 시험 적합성 통계적 n수 계산기",
    "MW - mg/mL - mM 몰농도 직관 변환기"
])

# =========================================================================
# [Tab 1] 다회 투여 축적률 계산기
# =========================================================================
with tab1:
    st.markdown("<h3 style='color:#002b5c; margin-bottom:20px;'>단회 Cmax 기반 다회 투여 축적률(R_acc) 및 정상상태(SS) 농도 예측</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#0056b3; margin-top:0;'>[INPUT] PK 파라미터 및 단회 Cmax</p>", unsafe_allow_html=True)
            thalf = st.number_input("약물 고유 반감기 (t1/2, hours)", min_value=0.1, value=53.0, step=1.0, help="미니피그 세마글루타이드 기준 기본 세팅", key="thalf_1")
            tau = st.number_input("투여 간격 (Tau, hours)", min_value=1.0, value=168.0, step=1.0, key="tau_1")
            cmax_1 = st.number_input("단회 투여 최고 혈중 농도 (Cmax,1, ng/mL)", min_value=0.1, value=50.0, step=5.0, key="cmax_1_input")
        
        ke = 0.693 / thalf
        r_acc = 1 / (1 - np.exp(-ke * tau)) if tau > 0 else 1.0
        cmax_ss = cmax_1 * r_acc
        
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#ba3c46; margin-top:0;'>[OUTPUT] 예측 결과 리포트</p>", unsafe_allow_html=True)
            st.metric(label="소실 속도 상수 (k_e)", value=f"{ke:.4f} /hr")
            st.metric(label="예상 축적비 (R_acc)", value=f"{r_acc:.2f} 배")
            st.metric(label="정상상태 최고 혈중 농도 (Cmax,ss)", value=f"{cmax_ss:.2f} ng/mL")
        
    with col2:
        with st.container(border=True):
            st.subheader("정상상태(Steady-State) 농도 도달 프로파일 시뮬레이션")
            t = np.linspace(0, tau * 4, 1000)
            cp = np.zeros_like(t)
            for n in range(4):
                t_dose = n * tau
                cp += np.where(t >= t_dose, cmax_1 * np.exp(-ke * (t - t_dose)), 0)
                
            fig, ax = plt.subplots(figsize=(10, 4.4))
            ax.plot(t, cp, color="#0056b3", linewidth=2.5, label="Predicted Cp Profile")
            ax.axhline(cmax_ss, color="#ba3c46", linestyle="--", linewidth=1.5, label=f"Theoretical Cmax,ss ({cmax_ss:.2f} ng/mL)")
            ax.set_xlabel("Time (hours)", fontsize=10, fontweight='bold', color='#475569')
            ax.set_ylabel("Drug Concentration (ng/mL)", fontsize=10, fontweight='bold', color='#475569')
            ax.grid(True, linestyle=":", alpha=0.5)
            ax.legend(loc="lower right", frameon=True, facecolor='#ffffff')
            st.pyplot(fig)

# =========================================================================
# [Tab 2] Flip-Flop Kinetics 계산기
# =========================================================================
with tab2:
    st.markdown("<h3 style='color:#002b5c; margin-bottom:5px;'>속도 상수 3배 마진선 기반 Flip-Flop Kinetics 검증기</h3>", unsafe_allow_html=True)
    st.write("소실 속도 상수(ke)와 NCA 역산 흡수 속도 상수(ka) 간의 3배 이상 벌어짐을 판단하여 서방화를 검증합니다.")
    
    st.markdown("""
        <div class="guide-box">
            <b>Flip-Flop Kinetics 판정 매커니즘:</b><br>
            서방형 제형(Depot, Microneedle)은 체내 약물 방출 및 흡수가 극단적으로 지연되어야 제

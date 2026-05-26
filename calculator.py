import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

# 앱 제목 및 레이아웃 설정
st.set_page_config(page_title="Formulation & PK 통합 계산기", layout="wide")

# =========================================================================
# 🎨 글로벌 메디컬 스타일 전용 커스텀 CSS 인젝션
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

# ★ [보정 완료] 상단 메인 블루 헤더 내부의 서브타이틀 글씨색을 선명한 화이트로 강제 고정
st.markdown("""
    <div style="background: linear-gradient(135deg, #002b5c 0%, #0056b3 100%); padding: 35px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">🧪 Formulation & PK Intelligence Integrated Platform</h1>
        <p style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 12px 0 0 0; font-size: 14.5px; font-weight: 500; opacity: 1.0; letter-spacing: 0.5px;">Daewoong Formulation Planning Team • 실무용 예측 시뮬레이터</p>
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
            서방형 제형(Depot, Microneedle)은 체내 약물 방출 및 흡수가 극단적으로 지연되어야 제 기능을 발휘합니다. 
            NCA 레포트의 MRT값과 고유 반감기를 연계하여 디컨볼루션했을 때, <b>약물 고유의 소실 속도(ke)가 제형 흡수 속도(ka)보다 3배 이상 빨라야 (ke/ka ≥ 3.0)</b> 플립플롭 기전이 완벽하게 확립되었다고 판단합니다.
        </div>
    """, unsafe_allow_html=True)
    
    col_ff1, col_ff2 = st.columns([1, 1])
    with col_ff1:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#0056b3; margin-top:0;'>[INPUT] NCA 데이터 및 고유 반감기</p>", unsafe_allow_html=True)
            mrt_sc = st.number_input("1. 데포제 SC 단회 투여 평균 체류 시간 (MRT_INF_obs, hours)", min_value=0.1, value=250.0, step=10.0, help="WinNonlin 결과창의 MRT 값")
            thalf_iv = st.number_input("2. 종별 세마글루타이드 고유 IV 반감기 (hours)", min_value=0.1, value=53.0, step=1.0, help="미니피그 고유 IV 반감기 규격값")
        
        met = thalf_iv / 0.693
        mat = mrt_sc - met if mrt_sc > met else 0.001
        ke_calc = 1.0 / met
        ka_calc = 1.0 / mat
        rate_ratio = ke_calc / ka_calc if ka_calc > 0 else 0.0
        
    with col_ff2:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#ba3c46; margin-top:0;'>[OUTPUT] 실무 3배 마진선 판정 리포트</p>", unsafe_allow_html=True)
            
            if rate_ratio >= 3.0:
                ff_status = f"서방화 검증 통과 (PASS) — {rate_ratio:.1f}배 지연"
                ff_color = "green"
                ff_desc = f"성공입니다. 약물 소실 속도({ke_calc:.4f}/hr)가 제형 방출 속도({ka_calc:.4f}/hr)보다 <b>{rate_ratio:.1f}배 빠릅니다.</b> 흡수가 타겟 마진인 3배 이상으로 늦춰져 완벽한 Flip-Flop 기전이 성립됩니다."
            else:
                ff_status = f"서방화 미달성 (FAIL) — {rate_ratio:.1f}배 차이"
                ff_color = "#ba3c46"
                ff_desc = f"현재 속도 상수 차이가 <b>{rate_ratio:.1f}배</b>로 실무 기준선(3배)에 미달합니다. 폴리머 배합비를 조정하여 방출 속도(ka)를 더 낮춰야 롱액팅이 성립됩니다."
                
            st.markdown(f"<h4>제형 서방화 판정: <span style='color:{ff_color}; font-weight:bold;'>{ff_status}</span></h4>", unsafe_allow_html=True)
            
            ff_nca_summary = {
                "Kinetics 속도 상수 분석 지표": ["약물 고유 소실 속도 상수 (k_e)", "제형 방출 흡수 속도 상수 (k_a)", "속도 상수 간 배수 차이 (k_e / k_a)"],
                "산출 연산값": [f"{ke_calc:.4f} /hr", f"{ka_calc:.4f} /hr", f"{rate_ratio:.2f} 배 벌어짐"],
                "실무 적합성 규격": ["약물 고유 청소율 마진", "연구원님 제형의 방출 제어력", "★ 최소 3배 이상 벌어져야 PASS"]
            }
            st.dataframe(pd.DataFrame(ff_nca_summary), width="stretch", hide_index=True)
            st.markdown(f"<p style='font-size:12px; color:#475569; margin-top:10px; line-height:1.4;'><b>연구진 제언:</b> {ff_desc}</p>", unsafe_allow_html=True)

# =========================================================================
# [Tab 3] HED 역산기
# =========================================================================
with tab3:
    st.markdown("<h3 style='color:#002b5c; margin-bottom:5px;'>Human Equivalent Dose (HED) 역산 환산기</h3>", unsafe_allow_html=True)
    st.write("FDA 가이드라인 기준: 인간 목표 투여 용량을 기반으로 역종별 비임상 동물 실험 투여 용량을 도출합니다.")
    
    km_table = {"Mouse (마우스)": 3, "Rat (래트)": 6, "Rabbit (토끼)": 12, "Dog (비글견)": 20, "Minipig (미니피그)": 35}
    km_human = 37
    
    col_hed1, col_hed2 = st.columns([1, 1])
    with col_hed1:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#0056b3; margin-top:0;'>[INPUT] 인간 목표 용량 설정</p>", unsafe_allow_html=True)
            input_mode = st.radio("임상 타겟 용량 입력 방식 선택", ["체중당 용량 직접 입력 (mg/kg)", "60kg 성인 기준 총 용량 입력 (mg)"])
            if input_mode == "체중당 용량 직접 입력 (mg/kg)":
                human_dose = st.number_input("인간 목표 투여 용량 (mg/kg)", min_value=0.01, value=1.6216, step=0.1, key="hd_direct")
            else:
                total_mg = st.number_input("60kg 성인 기준 총 투여량 (mg)", min_value=1.0, value=97.3, step=1.0, key="hd_total")
                human_dose = total_mg / 60.0
                st.caption(f"산출된 체중당 용량: {human_dose:.4f} mg/kg")

    with col_hed2:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#ba3c46; margin-top:0;'>[OUTPUT] 비임상 동물별 필요 투여 용량 (mg/kg)</p>", unsafe_allow_html=True)
            animal_results = []
            for name, km_val in km_table.items():
                calc_dose = human_dose * (km_human / km_val)
                animal_results.append({"동물 종": name, "Km Factor": km_val, "필요 투여 용량 (mg/kg)": f"{calc_dose:.4f} mg/kg"})
            st.dataframe(pd.DataFrame(animal_results), width="stretch", hide_index=True)

# =========================================================================
# [Tab 4] 임상 시험 적합성 통계적 n수 계산기
# =========================================================================
with tab4:
    st.markdown("<h3 style='color:#002b5c; margin-bottom:5px;'>임상 및 생동성(BE) 통계적 피험자 수(Sample Size) 산출 모듈</h3>", unsafe_allow_html=True)
    st.write("Chow and Liu 표준 통계 공식을 활용한 규제 기관 검증용 n수 역산기")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#0056b3; margin-top:0;'>[INPUT] 통계적 파라미터 세팅</p>", unsafe_allow_html=True)
            cv_val = st.number_input("약물의 개체내 변동계수 (Intra-subject CV, %)", min_value=5.0, max_value=80.0, value=20.0, step=1.0)
            gmr_val = st.number_input("예상 기하평균비 (Test/Reference GMR, %)", min_value=80.0, max_value=125.0, value=95.0, step=1.0)
            power_choice = st.selectbox("목표 통계적 검정력 (Statistical Power)", ["80% 검정력", "90% 검정력"])
            dropout_rate = st.slider("임상 탈락률 보정 (Dropout, %)", min_value=0, max_value=30, value=15, step=5)

        z_alpha = 1.6449
        z_beta = 0.8416 if power_choice == "80% 검정력" else 1.2816
        sigma = math.sqrt(math.log((cv_val / 100.0) ** 2 + 1))
        diff = math.fabs(math.log(gmr_val / 100.0))
        margin = math.log(1.25)
        
        if margin > diff:
            n_raw = 2 * ((z_alpha + z_beta) ** 2) * (sigma ** 2) / ((margin - diff) ** 2)
            n_stat = int(math.ceil(n_raw))
        else:
            n_stat = 12
            
        n_final_base = max(12, n_stat)
        n_total_recruitment = int(math.ceil(n_final_base / (1 - (dropout_rate / 100.0))))

    with col_stat2:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#ba3c46; margin-top:0;'>[OUTPUT] 통계학적 IND 승인 가이드라인 리포트</p>", unsafe_allow_html=True)
            st.metric(label="순수 통계학적 필요 n수 (최소 피험자 수)", value=f"{n_final_base} 명", delta=f"계산 원본: {n_stat}명")
            st.metric(label="탈락율 보정 최종 권장 모집 인원", value=f"{n_total_recruitment} 명")
            
            st.markdown(f"""
                <div style="background-color:#f8fafc; padding:12px; border:1px solid #cbd5e1; border-radius:6px; font-size:12px; color:#334155; line-height:1.5; margin-top:15px;">
                    <b>계획서 인용 문구 가이드:</b><br>
                    본 임상 시험은 변동계수(CV) {cv_val:.1f}%, 예상 기하평균비 {gmr_val:.1f}% 조건 하에서 
                    유의수준 5% 및 검정력 {80 if power_choice=="80% 검정력" else 90}%를 만족하기 위해 산출되었습니다. 
                    탈락률 {dropout_rate}%를 반영한 최종 권장 모집 인원은 총 <b>{n_total_recruitment}명</b>입니다.
                </div>
            """, unsafe_allow_html=True)

# =========================================================================
# [Tab 5] MW - mg/mL - mM 몰농도 변환기
# =========================================================================
with tab5:
    st.markdown("<h3 style='color:#002b5c; margin-bottom:5px;'>MW(분자량) - 중량 농도(mg/mL) - 몰 농도(mM) 상호 환산기</h3>", unsafe_allow_html=True)
    st.write("제형 설계(Formulation) 및 시약 조제 시 직관적인 인풋/아웃풋 제공")
    
    col_mw1, col_mw2 = st.columns(2)
    with col_mw1:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#0056b3; margin-top:0;'>[INPUT] 파라미터 및 환산 모드 선택</p>", unsafe_allow_html=True)
            mw_value = st.number_input("Target 약물 분자량 (MW, g/mol)", min_value=1.0, value=415.22, step=0.01, key="mw_5")
            calc_mode = st.radio("원하는 연산 방향을 선택하세요.", ["중량 농도(mg/mL) ➡️ 몰 농도(mM) 도출", "몰 농도(mM) ➡️ 중량 농도(mg/mL) 도출"])
            
            st.markdown("---")
            if calc_mode == "중량 농도(mg/mL) ➡️ 몰 농도(mM) 도출":
                input_mg = st.number_input("내가 조제한 중량 농도 입력 (mg/mL)", min_value=0.0, value=16.9659, step=0.1)
                output_mm = (input_mg / mw_value) * 1000
            else:
                input_mm = st.number_input("내가 타겟팅하는 몰 농도 입력 (mM)", min_value=0.0, value=40.86, step=0.01)
                output_mg = (input_mm * mw_value) / 1000

    with col_mw2:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px; font-weight:bold; color:#ba3c46; margin-top:0;'>[OUTPUT] 최종 환산 결과 확인</p>", unsafe_allow_html=True)
            if calc_mode == "중량 농도(mg/mL) ➡️ 몰 농도(mM) 도출":
                st.metric(label="도출된 최종 몰 농도", value=f"{output_mm:.4f} mM")
                report_mw = {
                    "약물 분자량 (MW)": [f"{mw_value:.2f} g/mol"], 
                    "내가 입력한 중량농도": [f"{input_mg:.4f} mg/mL"], 
                    "시스템 도출 몰농도": [f"{output_mm:.4f} mM"]
                }
            else:
                st.metric(label="도출된 최종 중량 농도", value=f"{output_mg:.4f} mg/mL")
                report_mw = {
                    "약물 분자량 (MW)": [f"{mw_value:.2f} g/mol"], 
                    "내가 입력한 몰농도": [f"{input_mm:.2f} mM"], 
                    "시스템 도출 필요중량": [f"{output_mg:.4f} mg/mL"]
                }
                
            st.dataframe(pd.DataFrame(report_mw), width="stretch", hide_index=True)

# 글로벌 테이블 폰트 제어 스타일 마감
st.markdown("<style>div[data-testid='stDataFrame'] table td {color: #000000 !important; font-family: 'Malgun Gothic', sans-serif !important;}</style>", unsafe_allow_html=True)

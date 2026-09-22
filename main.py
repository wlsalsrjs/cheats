import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="중고거래 소액사기 위험도 진단기",
    page_icon="🚨",
    layout="centered"
)

# 타이틀 및 안내
st.title("🚨 중고거래 소액사기 위험도 진단기")
st.markdown("""
거래하려는 **품목의 가격**과 **본인의 소액거래 경험 횟수**, 그리고 **거래 상황**을 입력하여 사기 위험도를 미리 체크해보세요!
""")

st.divider()

# 사용자 입력 섹션
st.header("1. 기본 정보 입력")

col1, col2 = st.columns(2)

with col1:
    price = st.number_input(
        "판매 품목 가격 (원)",
        min_value=0,
        value=50000,
        step=5000,
        help="구매하려는 물품의 거래 가격을 입력하세요."
    )

with col2:
    trade_count = st.number_input(
        "본인의 소액거래 경험 횟수 (회)",
        min_value=0,
        value=3,
        step=1,
        help="최근 1~2년간 중고거래를 진행해 본 횟수를 입력하세요."
    )

st.header("2. 거래 정황 체크리스트 (해당 사항 선택)")

# 위험 패턴 체크박스
check_messenger = st.checkbox("상대방이 앱 내부 채팅이 아닌 외부 메신저(카카오톡, 오픈채팅 등)로 이동을 요청하나요?")
check_link = st.checkbox("상대방이 직접 안전결제/네이버페이 등의 URL 링크를 보내왔나요?")
check_urgency = st.checkbox("다른 구매자가 있다며 '지금 즉시 입금'을 독촉하거나 급매를 강조하나요?")
check_non_face = st.checkbox("직거래를 거부하거나, '선입금 후 문 앞 수령/비대면'을 고집하나요?")
check_cheap = st.checkbox("해당 물품이 시세보다 현저히 저렴하게 나왔나요?")

# 위험도 계산 로직
risk_score = 0

# 1. 가격 요인 (소액사기 고위험 구간: 1만 원 ~ 15만 원)
if 10000 <= price <= 150000:
    risk_score += 20
elif 150000 < price <= 300000:
    risk_score += 10

# 2. 거래 경험 요인 (경험이 적을수록 사기 노출 위험 증가)
if trade_count == 0:
    risk_score += 15
elif trade_count <= 2:
    risk_score += 10
elif trade_count <= 5:
    risk_score += 5

# 3. 정황 체크리스트 요인 (가장 강력한 위험 신호)
if check_link:
    risk_score += 45  # 가짜 안전결제 링크는 거의 100% 사기
if check_messenger:
    risk_score += 20
if check_urgency:
    risk_score += 15
if check_non_face:
    risk_score += 15
if check_cheap:
    risk_score += 10

# 점수 캡핑 (최대 100점)
risk_score = min(risk_score, 100)

st.divider()

# 결과 출력 섹션
st.header("3. 진단 결과")

if st.button("위험도 진단하기", type="primary", use_container_width=True):
    st.subheader(f"위험도 점수: **{risk_score}점 / 100점**")
    st.progress(risk_score / 100)

    # 위험도 단계 분기
    if risk_score >= 70:
        st.error("🚨 **[위험등급: 매우 위험] 거래를 즉시 중단하세요!**")
        st.markdown("""
        * **분석:** 사기범들이 사용하는 전형적인 고위험 패턴이 다수 감지되었습니다.
        * **경고:** 특히 **외부 링크(URL)를 통한 결제 요구**나 **외부 메신저 이동 유도**는 99% 이상 사기 수법입니다. 절대로 입금하거나 링크에 계정 정보를 입력하지 마세요.
        """)
    elif risk_score >= 40:
        st.warning("⚠️ **[위험등급: 주의] 신중한 확인이 필요합니다.**")
        st.markdown("""
        * **분석:** 소액사기 위험 요소가 포함되어 있습니다.
        * **경고:** 소액 거래(1~10만 원)는 경찰 신고나 추적이 어렵다는 점을 악용하는 경우가 많습니다. 입금 전 **더치트**나 **사이버캅**을 통해 상대방 연락처/계좌를 반드시 조회하세요.
        """)
    else:
        st.success("✅ **[위험등급: 비교적 안전] 기본 수칙을 준수하며 거래하세요.**")
        st.markdown("""
        * **분석:** 현재까지는 전형적인 사기 패턴이 크게 눈에 띄지 않습니다.
        * **경고:** 다만, 방심은 금물입니다. 반드시 중고거래 플랫폼 내부 결제/채팅 시스템을 이용하시고, 택배 거래 시 선입금에 유의하세요.
        """)

    # 종합 예방 팁
    with st.expander("💡 소액 사기 예방 4대 철칙 보기"):
        st.write("""
        1. **플랫폼 이탈 금지:** 당근, 중고나라, 번개장터 등의 자체 채팅망만 이용하세요.
        2. **외부 링크 접속 절대 금지:** 상대방이 보낸 '안전결제 링크'는 피싱 사이트입니다.
        3. **사기 이력 조회:** 입금 전 [더치트(The Cheat)] 앱에서 계좌번호/전화번호를 검색하세요.
        4. **시세보다 너무 싸면 의심:** 미개봉 신품이나 인기도서/상품권을 시세의 반값에 파는 거래는 유의하세요.
        """)

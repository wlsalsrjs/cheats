import streamlit as st
import re
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="중고거래 대화 기반 사기 위험도 진단기",
    page_icon="💬",
    layout="centered"
)

# 특수 공백 정제 함수 (복사/붙여넣기 오류 방지)
def sanitize_text(text):
    return text.replace('\xa0', ' ').strip()

# 사이드바: 모드 선택 (구매자 / 판매자)
st.sidebar.title("👥 역할 선택")
mode = st.sidebar.radio(
    "본인의 거래 역할을 선택하세요:",
    ["🛒 구매자 시점 (내가 물건을 살 때)", "🏷️ 판매자 시점 (내가 물건을 팔 때)"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("""
💡 **역할별 진단 안내**
* **구매자 시점**: 판매자가 제시하는 거래 조건/대화(외부 링크, 카톡 유도 등)를 분석하여 판매자의 사기 위험도를 진단합니다.
* **판매자 시점**: 가상 구매자가 제시하는 소액 상품 거래 요청 및 대화(선송장 요구, 외부 채널 유도 등)를 분석하여 구매자의 사기 가능성을 모의 진단합니다.
""")

# ==============================================================================
# 1. 구매자 시점 (사용자가 구매자 - 상대방 판매자의 대화 검증)
# ==============================================================================
if mode == "🛒 구매자 시점 (내가 물건을 살 때)":
    st.title("🛒 구매자용: 판매자 사기 위험도 진단기")
    st.markdown("""
    구매하려는 물품의 정보와 **판매자(상대방)**가 보낸 대화 내용을 입력하세요.  
    판매자들의 전형적인 피싱/사기 패턴(가짜 안전결제 링크, 외부 메신저 유도 등)을 감지해 드립니다!
    """)

    st.divider()

    # 1. 거래 기본 정보 입력
    st.header("1. 거래 기본 정보")
    col1, col2 = st.columns(2)

    with col1:
        price = st.number_input(
            "구매하려는 물품 가격 (원)",
            min_value=0,
            value=50000,
            step=5000,
            help="구매하려는 물품의 가격을 입력하세요."
        )

    with col2:
        trade_count = st.number_input(
            "본인의 중고거래 경험 횟수 (회)",
            min_value=0,
            value=3,
            step=1,
            help="거래 경험이 적을수록 경각심 가이드를 강화해 드립니다."
        )

    # 2. 대화 내용 입력 및 샘플 테스트
    st.header("2. 판매자와 주고받은 대화 내용")

    if "buyer_chat_text" not in st.session_state:
        st.session_state["buyer_chat_text"] = ""

    st.write("💡 **테스트용 샘플 판매자 대화 불러오기:**")
    sample_col1, sample_col2, sample_col3 = st.columns(3)

    with sample_col1:
        if st.button("🚨 가짜 안전결제 피싱", use_container_width=True):
            st.session_state["buyer_chat_text"] = "안녕하세요. 물건 지방이라 택배거래만 됩니다. 제가 네이버페이 안전결제 생성해서 링크 보내드릴 테니 접속하셔서 결제 진행해 주세요. http://naverpay-safety.com"

    with sample_col2:
        if st.button("📲 외부 메신저 유도", use_container_width=True):
            st.session_state["buyer_chat_text"] = "앱 알림이 잘 안 와서 그러는데 카톡으로 문의주세요. 카톡 ID: scammer123 입니다. 오시면 사진 더 보내드릴게요."

    with sample_col3:
        if st.button("✅ 정상 판매자 예시", use_container_width=True):
            st.session_state["buyer_chat_text"] = "안녕하세요! 거래 가능합니다. 내일 오후 3시에 강남역 4번 출구 쪽에서 직거래 가능할까요? 물건 직접 확인하시고 입금해주세요."

    user_chat = st.text_area(
        "판매자가 보낸 메시지를 복사해서 붙여넣으세요:",
        value=st.session_state["buyer_chat_text"],
        height=180,
        placeholder="예시:\n- 앱 알림이 안 와서 카톡으로 문의주세요 ID: abc1234\n- 안전거래 링크 보내드릴 테니 접속해서 결제하시면 됩니다."
    )

    st.divider()

    # 3. 진단 버튼 및 분석 로직
    st.header("3. 판매자 사기 위험도 진단 결과")

    if st.button("판매자 대화 분석 및 위험도 진단하기", type="primary", use_container_width=True):
        clean_chat = sanitize_text(user_chat)
        if not clean_chat:
            st.warning("⚠️ 분석할 대화 내용을 입력해 주세요.")
        else:
            risk_score = 0
            detected_patterns = []

            # 패턴 정의
            pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|앱이\s*이상|아이디|ID|톡주|톡으로)", re.IGNORECASE)
            pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|중고나라페이|링크|URL|http|https|사이트|페이지|수수료|오류|재입금|환불)", re.IGNORECASE)
            pattern_urgency = re.compile(r"(지금\s*바로|즉시|다른\s*분|먼저\s*입금|급매|오늘만|택배\s*붙이|택배\s*보내|송장|편의점)", re.IGNORECASE)
            pattern_non_face = re.compile(r"(출장|지방|근무|비대면|문\s*앞|현관|비밀번호|동호수|대신|선입금)", re.IGNORECASE)

            if pattern_link.search(clean_chat):
                risk_score += 45
                detected_patterns.append("🔗 **외부 웹 피싱/가짜 안전결제 링크 유도** (100% 사기 위험)")

            if pattern_messenger.search(clean_chat):
                risk_score += 25
                detected_patterns.append("📲 **앱 외부 메신저(카카오톡/오픈채팅 등) 이동 유도**")

            if pattern_urgency.search(clean_chat):
                risk_score += 15
                detected_patterns.append("⏰ **즉시 입금 독촉 및 타 구매자 대기 상황 연출**")

            if pattern_non_face.search(clean_chat):
                risk_score += 15
                detected_patterns.append("🚪 **직거래 회피 (지방/출장 핑계) 및 택배 거래 강요**")

            if 10000 <= price <= 150000:
                risk_score += 10
            if trade_count <= 1:
                risk_score += 5

            risk_score = min(risk_score, 100)

            # 게이지 색상
            if risk_score >= 70:
                gauge_color = "#FF2B2B"
            elif risk_score >= 45:
                gauge_color = "#FF8C00"
            elif risk_score >= 25:
                gauge_color = "#FFC107"
            else:
                gauge_color = "#28A745"

            st.subheader(f"판매자 위험도 점수: **{risk_score}점 / 100점**")
            st.markdown(f"""
            <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
                <div style="background-color: {gauge_color}; width: {risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
            </div>
            """, unsafe_allow_html=True)

            if detected_patterns:
                st.markdown("### 🔍 감지된 판매자 사기 의심 패턴:")
                for pattern in detected_patterns:
                    st.write(f"- {pattern}")
                st.write("")

            if risk_score >= 65:
                st.error("🚨 **[위험등급: 매우 위험] 결제를 중단하세요!**")
                st.markdown("""
                * **분석:** 판매자가 중고거래 피싱 사기의 전형적인 수법을 사용하고 있습니다.
                * **경고:** 판매자가 보낸 URL 접속 또는 외부 메신저 입금 요구는 99% 사기입니다. 절대로 입금하지 마세요.
                """)
            elif risk_score >= 35:
                st.warning("⚠️ **[위험등급: 주의] 판매자 신원 확인이 필요합니다.**")
                st.markdown("""
                * **분석:** 거래 대화 중 사기 의심 키워드가 감지되었습니다.
                * **경고:** 입금 전 **더치트**나 **경찰청 사이버캅**에서 판매자의 계좌번호와 전화번호를 조회하세요.
                """)
            else:
                st.success("✅ **[위험등급: 비교적 안전] 안전 거래 수칙을 준수하세요.**")
                st.markdown("""
                * **분석:** 전형적인 판매자 사기 대화 패턴이 감지되지 않았습니다.
                * **경고:** 외부 링크 결제를 피하고 플랫폼 내부 정식 거래망만 이용하세요.
                """)


# ==============================================================================
# 2. 판매자 시점 (사용자가 판매자 - 상대방 구매자의 대화 시뮬레이션)
# ==============================================================================
else:
    st.title("🏷️ 판매자용: 가상 구매자 사기 위험도 시뮬레이터")
    st.markdown("""
    사용자님이 **판매자**로서 $1,000\text{원} \sim 5,000\text{원}$ 상당의 소액 물품을 판매하는 상황입니다.  
    가상의 구매자가 보내온 메시지를 바탕으로 **소액 거래 사기 위험도**를 모의 진단합니다.
    """)

    st.divider()

    # 가상 세션 데이터 초기화
    if "sim_price" not in st.session_state:
        st.session_state["sim_price"] = random.randint(1000, 5000)

    if "sim_chat" not in st.session_state:
        st.session_state["sim_chat"] = "안녕하세요! 거래 잘 부탁드립니다. 혹시 직거래 가능할까요?"

    # 가상 구매자 대화 풀 (사기형 vs 정상형)
    scam_buyer_chats = [
        "지금 바로 5000원 입금할 테니 편의점 택배 송장 먼저 뽑아서 사진 보내주시면 확인하고 입금해 드릴게요!",
        "제가 알림이 잘 안 와서 카카오톡으로 진행하고 싶습니다. 카톡 ID: buyer_fast 로 톡 주세요!",
        "제가 지금 출장 중이라 물건 문 앞에 둬주시면 확인 후 바로 계좌로 선입금해 드릴게요.",
        "네이버페이 안전결제로 거래하고 싶은데 구매자용 링크 생성해서 보내주실 수 있나요?"
    ]

    normal_buyer_chats = [
        "안녕하세요! 거래 잘 부탁드립니다. 혹시 어디서 직거래 가능하신가요?",
        "안녕하세요 구매 희망합니다! 당근페이로 결제하면 될까요?",
        "안녕하세요, 아직 판매 중인가요? 거래 가능한 시간 알려주시면 맞춰서 입금할게요!"
    ]

    # 가상 상황 새로고침 버튼
    if st.button("🎲 새로운 가상 구매자 대화 불러오기", use_container_width=True):
        st.session_state["sim_price"] = random.randint(1000, 5000)
        is_scam_buyer = random.choice([True, False])
        if is_scam_buyer:
            st.session_state["sim_chat"] = random.choice(scam_buyer_chats)
        else:
            st.session_state["sim_chat"] = random.choice(normal_buyer_chats)

    # 1. 가상 매칭 정보
    st.header("1. 내가 올린 상품 정보")
    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.metric("판매 중인 물품 가격", f"{st.session_state['sim_price']:,} 원")

    with sim_col2:
        st.metric("거래 유형", "소액 상품 무작위 매칭")

    # 2. 가상 구매자가 보낸 메시지
    st.header("2. 구매자(상대방)가 보낸 대화")
    st.info(f"💬 **구매자:** \"{st.session_state['sim_chat']}\"")

    st.divider()

    # 3. 진단 결과 분석
    st.header("3. 구매자 사기 위험도 종합 분석 결과")

    sim_chat_text = sanitize_text(st.session_state["sim_chat"])
    sim_risk_score = 0
    sim_reasons = []

    pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|아이디|ID)", re.IGNORECASE)
    pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|링크|URL|http|https)", re.IGNORECASE)
    pattern_urgency = re.compile(r"(송장|편의점|선발송|택배\s*먼저)", re.IGNORECASE)
    pattern_non_face = re.compile(r"(출장|지방|문\s*앞|비대면|선입금)", re.IGNORECASE)

    if pattern_urgency.search(sim_chat_text):
        sim_risk_score += 45
        sim_reasons.append("📦 **입금 전 송장 우선 발송(선발송) 유도** (소액 물품 입금 먹튀 사기 가능성)")

    if pattern_link.search(sim_chat_text):
        sim_risk_score += 40
        sim_reasons.append("🔗 **안전결제 링크 요구** (판매자 개인정보/계좌 탈취 목적 피싱 가능성)")

    if pattern_messenger.search(sim_chat_text):
        sim_risk_score += 30
        sim_reasons.append("📲 **앱 외부 메신저로 이동 요구** (플랫폼 신고 차단 회피 시도)")

    if pattern_non_face.search(sim_chat_text):
        sim_risk_score += 20
        sim_reasons.append("🚪 **비대면 수령 및 출장 핑계 요구**")

    sim_risk_score = min(sim_risk_score, 100)

    # 색상 산정
    if sim_risk_score >= 70:
        sim_gauge_color = "#FF2B2B"
    elif sim_risk_score >= 40:
        sim_gauge_color = "#FF8C00"
    elif sim_risk_score >= 20:
        sim_gauge_color = "#FFC107"
    else:
        sim_gauge_color = "#28A745"

    st.subheader(f"구매자 위험도 점수: **{sim_risk_score}점 / 100점**")

    st.markdown(f"""
    <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
        <div style="background-color: {sim_gauge_color}; width: {sim_risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
    </div>
    """, unsafe_allow_html=True)

    if sim_risk_score >= 40:
        st.error("🚨 **[위험도 높음] 구매자의 요구 조건이 의심스럽습니다!**")
        st.markdown(f"""
        * **감지된 의심 요소:** {', '.join(sim_reasons)}
        * **판매자 경고 가이드:** {st.session_state['sim_price']:,}원 상당의 소액 상품일지라도 **"송장 먼저 뽑아주면 입금하겠다"**는 식의 거래 요구나 외부 채널 이동 요구는 100% 거부하세요. 반드시 대금 입금 확인 후 물품을 발송해야 합니다.
        """)
    else:
        st.success("✅ **[위험도 낮음] 구매자의 정상적인 거래 대화 패턴입니다.**")
        st.markdown(f"""
        * **분석 내용:** 송장 선발송 강요, 외부 결제 링크 요구, 외부 메신저 유도 등의 이상 패턴이 발견되지 않았습니다.
        * **판매자 가이드:** 정해진 안심 결제 수단 및 채팅창 내부 안내에 따라 안전하게 거래를 진행하세요.
        """)

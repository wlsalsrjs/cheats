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

# 사이드바: 모드 선택 (판매자 / 구매자)
st.sidebar.title("👥 역할 선택")
mode = st.sidebar.radio(
    "본인의 거래 역할을 선택하세요:",
    ["🏷️ 판매자 시점 (내가 물건을 팔 때)", "🛒 구매자 시점 (내가 물건을 살 때)"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("""
💡 **역할별 진단 안내**
* **판매자 시점**: 구매하려는 상대방이 보낸 대화 내용(선송장 요구, 외부 메신저 유도 등)을 입력하여 구매자의 사기 위험도를 진단합니다.
* **구매자 시점**: 가상 판매자가 제시하는 조건과 대화(가짜 안전결제 링크, 외부 채널 이동 등)를 통해 판매자의 사기 가능성을 모의 진단합니다.
""")

# ==============================================================================
# 1. 판매자 시점 (내가 물건을 팔 때 - 상대방 구매자의 대화 분석)
# ==============================================================================
if mode == "🏷️ 판매자 시점 (내가 물건을 팔 때)":
    st.title("🏷️ 판매자용: 구매자 사기 위험도 진단기")
    st.markdown("""
    판매하려는 물품의 정보와 **구매자(상대방)**가 보낸 대화 내용을 입력하세요.  
    구매자들의 전형적인 사기 패턴(입금 전 송장 우선 발송 요구, 외부 메신저 이동 유도 등)을 감지해 드립니다!
    """)

    st.divider()

    # 1. 거래 기본 정보 입력
    st.header("1. 거래 기본 정보")
    col1, col2 = st.columns(2)

    with col1:
        price = st.number_input(
            "판매하려는 물품 가격 (원)",
            min_value=0,
            value=50000,
            step=5000,
            help="판매하려는 물품의 가격을 입력하세요."
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
    st.header("2. 구매자와 주고받은 대화 내용")

    if "seller_chat_text" not in st.session_state:
        st.session_state["seller_chat_text"] = ""

    st.write("💡 **테스트용 샘플 구매자 대화 불러오기:**")
    sample_col1, sample_col2, sample_col3 = st.columns(3)

    with sample_col1:
        if st.button("🚨 송장 선발송 요구", use_container_width=True):
            st.session_state["seller_chat_text"] = "지금 바로 입금할 테니 편의점 택배 송장 먼저 뽑아서 사진 보내주세요. 송장 확인되는 대로 바로 입금해 드릴게요!"

    with sample_col2:
        if st.button("📲 외부 메신저 유도", use_container_width=True):
            st.session_state["seller_chat_text"] = "앱 알림이 잘 안 와서 그러는데 카톡으로 거래 진행해 주세요. 카톡 ID: buyer123 입니다."

    with sample_col3:
        if st.button("✅ 정상 구매자 예시", use_container_width=True):
            st.session_state["seller_chat_text"] = "안녕하세요! 거래 가능할까요? 내일 오후 3시에 강남역 4번 출구 쪽에서 직거래 가능할까요? 현장에서 직접 확인하고 입금드릴게요."

    user_chat = st.text_area(
        "구매자가 보낸 메시지를 복사해서 붙여넣으세요:",
        value=st.session_state["seller_chat_text"],
        height=180,
        placeholder="예시:\n- 지금 바로 입금할 테니 편의점 택배 송장 먼저 보내주세요.\n- 앱 알림이 안 와서 카톡으로 문의주세요 ID: abc1234"
    )

    st.divider()

    # 3. 진단 버튼 및 분석 로직
    st.header("3. 구매자 사기 위험도 진단 결과")

    if st.button("구매자 대화 분석 및 위험도 진단하기", type="primary", use_container_width=True):
        clean_chat = sanitize_text(user_chat)
        if not clean_chat:
            st.warning("⚠️ 분석할 대화 내용을 입력해 주세요.")
        else:
            risk_score = 0
            detected_patterns = []

            pattern_urgency = re.compile(r"(송장|편의점|선발송|택배\s*먼저|보내주시면|사진\0s*보내)", re.IGNORECASE)
            pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|아이디|ID|톡주)", re.IGNORECASE)
            pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|링크|URL|http|https)", re.IGNORECASE)
            pattern_non_face = re.compile(r"(출장|지방|근무|비대면|문\s*앞|현관|선입금)", re.IGNORECASE)

            if pattern_urgency.search(clean_chat):
                risk_score += 45
                detected_patterns.append("📦 **입금 전 송장 우선 발송 요구** (소액/중고거래 전형적 먹튀 패턴)")

            if pattern_messenger.search(clean_chat):
                risk_score += 25
                detected_patterns.append("📲 **앱 외부 메신저(카카오톡/오픈채팅 등) 이동 유도**")

            if pattern_link.search(clean_chat):
                risk_score += 20
                detected_patterns.append("🔗 **구매자 측의 비정상 안전결제 링크 요구**")

            if pattern_non_face.search(clean_chat):
                risk_score += 10
                detected_patterns.append("🚪 **비대면 수령 및 선입금 무조건 고집**")

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

            st.subheader(f"구매자 위험도 점수: **{risk_score}점 / 100점**")
            st.markdown(f"""
            <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
                <div style="background-color: {gauge_color}; width: {risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
            </div>
            """, unsafe_allow_html=True)

            if detected_patterns:
                st.markdown("### 🔍 감지된 구매자 사기 의심 패턴:")
                for pattern in detected_patterns:
                    st.write(f"- {pattern}")
                st.write("")

            if risk_score >= 65:
                st.error("🚨 **[위험등급: 매우 위험] 거래를 거절하세요!**")
                st.markdown("""
                * **분석:** 입금 전 송장 선발송 요구나 외부 채널 이동 등 위험한 대화 패턴이 감지되었습니다.
                * **경고:** 물품 발송 또는 송장 발행은 반드시 내 계좌로 입금이 완결된 것을 확인한 후 진행하세요.
                """)
            elif risk_score >= 35:
                st.warning("⚠️ **[위험등급: 주의] 신중한 입금 확인이 필요합니다.**")
                st.markdown("""
                * **분석:** 사기 의심 키워드가 일부 포함되어 있습니다.
                * **경고:** 구매자가 정식 플랫폼 채팅창 내에서 거래를 진행하는지 확인하세요.
                """)
            else:
                st.success("✅ **[위험등급: 비교적 안전] 안전 거래 수칙을 준수하세요.**")
                st.markdown("""
                * **분석:** 전형적인 구매자 사기 패턴이 감지되지 않았습니다.
                * **경고:** 항상 계좌 입금 내역을 직접 확인한 뒤 상품을 보내세요.
                """)


# ==============================================================================
# 2. 구매자 시점 (내가 물건을 살 때 - 상대방 가상 판매자의 대화 시뮬레이션)
# ==============================================================================
else:
    st.title("🛒 구매자용: 가상 판매자 사기 위험도 시뮬레이터")
    st.markdown("""
    사용자님이 **구매자**로서 1,000원 ~ 5,000원 상당의 소액 물품을 구매하려는 상황입니다.  
    가상의 판매자가 보내온 메시지를 바탕으로 **판매자 사기 위험도**를 모의 진단합니다.
    """)

    st.divider()

    # 가상 세션 데이터 초기화
    if "sim_price" not in st.session_state:
        st.session_state["sim_price"] = random.randint(1000, 5000)

    if "sim_chat" not in st.session_state:
        st.session_state["sim_chat"] = "안녕하세요! 구매 가능하십니다. 직거래 원하시나요?"

    # 가상 판매자 대화 풀 (사기형 vs 정상형)
    scam_seller_chats = [
        "안녕하세요. 물건 지방이라 택배거래만 됩니다. 제가 네이버페이 안전결제 생성해서 링크 보내드릴 테니 접속해서 결제해 주세요. http://naverpay-safe.xyz",
        "앱 알림이 잘 안 와서 그러는데 카카오톡으로 문의주세요! ID: fastpay99 오시면 상세 사진 보내드릴게요.",
        "지금 바로 입금하시면 5분 안에 편의점 택배 송장 바로 뽑아드릴게요!",
        "제가 지금 출장 중이라 비대면 택배만 가능합니다. 계좌 알려드릴 테니 선입금 부탁드려요."
    ]

    normal_seller_chats = [
        "안녕하세요! 거래 가능합니다. 혹시 어디서 직거래 가능하신가요?",
        "안녕하세요 구매 가능하십니다. 안전하게 당근페이로 결제해 주시면 됩니다!",
        "안녕하세요, 오늘 저녁에 시간 맞춰주시면 직거래 또는 편의점 반값택배 가능합니다."
    ]

    # 가상 상황 새로고침 버튼
    if st.button("🎲 새로운 가상 판매자 대화 불러오기", use_container_width=True):
        st.session_state["sim_price"] = random.randint(1000, 5000)
        is_scam_seller = random.choice([True, False])
        if is_scam_seller:
            st.session_state["sim_chat"] = random.choice(scam_seller_chats)
        else:
            st.session_state["sim_chat"] = random.choice(normal_seller_chats)

    # 1. 가상 매칭 정보
    st.header("1. 구매하려는 상품 정보")
    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.metric("구매 대상 물품 가격", f"{st.session_state['sim_price']:,} 원")

    with sim_col2:
        st.metric("거래 유형", "소액 상품 무작위 매칭")

    # 2. 가상 판매자가 보낸 메시지
    st.header("2. 판매자(상대방)가 보낸 대화")
    st.info(f"💬 **판매자:** \"{st.session_state['sim_chat']}\"")

    st.divider()

    # 3. 진단 결과 분석
    st.header("3. 판매자 사기 위험도 종합 분석 결과")

    sim_chat_text = sanitize_text(st.session_state["sim_chat"])
    sim_risk_score = 0
    sim_reasons = []

    pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|링크|URL|http|https)", re.IGNORECASE)
    pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|아이디|ID)", re.IGNORECASE)
    pattern_urgency = re.compile(r"(지금\s*바로|즉시|급하게|오늘만)", re.IGNORECASE)
    pattern_non_face = re.compile(r"(출장|지방|문\s*앞|비대면|선입금)", re.IGNORECASE)

    if pattern_link.search(sim_chat_text):
        sim_risk_score += 55
        sim_reasons.append("🔗 **외부 웹 피싱/가짜 안전결제 링크 유도** (100% 사기 위험)")

    if pattern_messenger.search(sim_chat_text):
        sim_risk_score += 30
        sim_reasons.append("📲 **앱 외부 메신저 이동 유도** (플랫폼 보호 시스템 회피 시도)")

    if pattern_urgency.search(sim_chat_text):
        sim_risk_score += 20
        sim_reasons.append("⏰ **즉시 입금 독촉 및 긴급 거래 연출**")

    if pattern_non_face.search(sim_chat_text):
        sim_risk_score += 20
        sim_reasons.append("🚪 **직거래 회피 및 비대면 택배거래 강요**")

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

    st.subheader(f"판매자 위험도 점수: **{sim_risk_score}점 / 100점**")

    st.markdown(f"""
    <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
        <div style="background-color: {sim_gauge_color}; width: {sim_risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
    </div>
    """, unsafe_allow_html=True)

    if sim_risk_score >= 40:
        st.error("🚨 **[위험도 높음] 판매자의 대화 및 조건이 사기 패턴입니다!**")
        st.markdown(f"""
        * **감지된 의심 요소:** {', '.join(sim_reasons)}
        * **구매자 경고 가이드:** {st.session_state['sim_price']:,}원 상당의 소액 거래라 하더라도 외부 링크 결제 접속이나 카카오톡 유도는 피싱 사기일 위험이 큽니다. 입금을 중단하고 거래를 취소하세요.
        """)
    else:
        st.success("✅ **[위험도 낮음] 판매자의 정상적인 거래 대화 패턴입니다.**")
        st.markdown(f"""
        * **분석 내용:** 외부 메신저 유도, 피싱 링크 전송, 직거래 거부 등의 의심 패턴이 감지되지 않았습니다.
        * **구매자 가이드:** 정식 앱 내부 채팅창과 안전한 결제 시스템을 이용해 거래를 진행하세요.
        """)

import streamlit as st
import re
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="중고거래 대화 기반 사기 위험도 진단기",
    page_icon="💬",
    layout="centered"
)

# 사이드바: 모드 선택 (구매자 / 판매자)
st.sidebar.title("👥 역할 선택")
mode = st.sidebar.radio(
    "진단받을 시점을 선택하세요:",
    ["🛒 구매자 시점 (대화 직접 분석)", "🏷️ 판매자 시점 (가상 거래 시뮬레이션)"],
    index=0
)

st.sidebar.divider()
st.sidebar.info("""
💡 **모드 안내**
* **구매자 시점**: 상대방과 직접 나눈 대화를 입력하여 사기 위험도를 분석합니다.
* **판매자 시점**: 가상 구매자가 제시하는 조건과 대화를 통해 사기 가능성을 모의 진단합니다.
""")

# ==============================================================================
# 1. 구매자 시점 (기존 대화 입력 분석 기능)
# ==============================================================================
if mode == "🛒 구매자 시점 (대화 직접 분석)":
    st.title("💬 중고거래 대화 내용 기반 사기 진단기 (구매자용)")
    st.markdown("""
    상대방과 주고받은 **대화 내용(텍스트)**과 **거래 정보**를 입력해 보세요.  
    AI 키워드 분석 로직이 대화 속 사기범들의 전형적인 멘트 패턴을 감지하여 위험도를 분석해 드립니다!
    """)

    st.divider()

    # 1. 기본 정보 입력
    st.header("1. 거래 기본 정보")
    col1, col2 = st.columns(2)

    with col1:
        price = st.number_input(
            "판매 품목 가격 (원)",
            min_value=0,
            value=50000,
            step=5000,
            help="구매하려는 물품의 가격을 입력하세요."
        )

    with col2:
        trade_count = st.number_input(
            "본인의 소액거래 경험 횟수 (회)",
            min_value=0,
            value=3,
            step=1,
            help="중고거래 경험이 적을수록 경각심 가이드를 강화해 드립니다."
        )

    # 2. 대화 내용 입력 및 샘플 테스트
    st.header("2. 상대방과의 대화 내용 입력")

    if "chat_text" not in st.session_state:
        st.session_state["chat_text"] = ""

    st.write("💡 **테스트용 샘플 대화 불러오기:**")
    sample_col1, sample_col2, sample_col3 = st.columns(3)

    with sample_col1:
        if st.button("🚨 가짜 안전결제 사기", use_container_width=True):
            st.session_state["chat_text"] = "안녕하세요. 물건 지방이라 택배거래만 됩니다. 제가 네이버페이 안전결제 생성해서 링크 보내드릴 테니 접속하셔서 결제 진행해 주세요. http://naverpay-safety.com"

    with sample_col2:
        if st.button("📲 외부 메신저 유도", use_container_width=True):
            st.session_state["chat_text"] = "앱 알림이 잘 안 와서 그러는데 카톡으로 문의주세요. 카톡 ID: scammer123 입니다. 오시면 사진 더 보내드릴게요."

    with sample_col3:
        if st.button("✅ 정상 거래 예시", use_container_width=True):
            st.session_state["chat_text"] = "안녕하세요! 아직 구매 가능한가요? 내일 오후 3시에 강남역 4번 출구 쪽에서 직거래 가능할까요? 물건 직접 보고 입금드릴게요."

    user_chat = st.text_area(
        "카톡, 문자, 당근챗 등에서 상대방과 주고받은 대화를 복사해서 붙여넣으세요:",
        value=st.session_state["chat_text"],
        height=200,
        placeholder="예시:\n- 앱 알림이 안 와서 카톡으로 문의주세요 ID: abc1234\n- 지금 바로 입금하시면 편의점 택배로 송장 바로 뽑아드릴게요.\n- 안전거래 링크 보내드릴 테니 접속해서 결제하시면 됩니다."
    )

    st.divider()

    # 3. 진단 버튼 및 분석 로직
    st.header("3. 분석 결과")

    if st.button("대화 분석 및 위험도 진단하기", type="primary", use_container_width=True):
        if not user_chat.strip():
            st.warning("⚠️ 분석할 대화 내용을 입력해 주세요.")
        else:
            risk_score = 0
            detected_patterns = []

            # 사기 패턴 정규식
            pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|앱이\s*이상|아이디|ID|톡주|톡으로)", re.IGNORECASE)
            pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|중고나라페이|링크|URL|http|https|사이트|페이지|수수료|오류|재입금|환불)", re.IGNORECASE)
            pattern_urgency = re.compile(r"(지금\s*바로|즉시|다른\s*분|먼저\s*입금|급매|오늘만|택배\s*붙이|택배\s*보내|송장|편의점)", re.IGNORECASE)
            pattern_non_face = re.compile(r"(출장|지방|근무|비대면|문\s*앞|현관|비밀번호|동호수|대신|선입금)", re.IGNORECASE)

            if pattern_link.search(user_chat):
                risk_score += 45
                detected_patterns.append("🔗 **외부 링크/안전결제 접속 유도** (가짜 피싱 사이트 가능성 극히 높음)")

            if pattern_messenger.search(user_chat):
                risk_score += 25
                detected_patterns.append("📲 **외부 메신저(카카오톡/오픈채팅 등) 이동 유도**")

            if pattern_urgency.search(user_chat):
                risk_score += 15
                detected_patterns.append("⏰ **즉시 입금 독촉 및 상황 급박 연출** (택배 즉시 발송, 타 구매자 대기 등)")

            if pattern_non_face.search(user_chat):
                risk_score += 15
                detected_patterns.append("🚪 **직거래 회피 또는 선입금 후 비대면 수령 조건 요구**")

            if 10000 <= price <= 150000:
                risk_score += 10
            if trade_count <= 1:
                risk_score += 5

            risk_score = min(risk_score, 100)

            # 색상 결정
            if risk_score >= 70:
                gauge_color = "#FF2B2B"
            elif risk_score >= 45:
                gauge_color = "#FF8C00"
            elif risk_score >= 25:
                gauge_color = "#FFC107"
            else:
                gauge_color = "#28A745"

            st.subheader(f"위험도 점수: **{risk_score}점 / 100점**")
            st.markdown(f"""
            <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
                <div style="background-color: {gauge_color}; width: {risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
            </div>
            """, unsafe_allow_html=True)

            if detected_patterns:
                st.markdown("### 🔍 대화 속에서 감지된 사기 의심 패턴:")
                for pattern in detected_patterns:
                    st.write(f"- {pattern}")
                st.write("")

            if risk_score >= 65:
                st.error("🚨 **[위험등급: 매우 위험] 거래를 즉시 중단하세요!**")
                st.markdown("""
                * **분석:** 전형적인 중고거래 사기범들의 대화 패턴이 대거 감지되었습니다.
                * **주의사항:** 외부 링크 접속 및 외부 메신저 이동 요구는 99% 이상 사기 수법입니다.
                """)
            elif risk_score >= 35:
                st.warning("⚠️ **[위험등급: 주의] 신중한 확인이 필요합니다.**")
                st.markdown("""
                * **분석:** 사기 의심 키워드가 일부 포함되어 있습니다.
                * **주의사항:** 입금 전 계좌/전화번호 사기 이력을 더치트에서 반드시 조회해 보세요.
                """)
            else:
                st.success("✅ **[위험등급: 비교적 안전] 기본 거래 수칙을 준수하세요.**")
                st.markdown("""
                * **분석:** 전형적인 사기 대화 패턴이 감지되지 않았습니다.
                * **주의사항:** 플랫폼 내부 채팅 및 정식 결제 시스템만 이용하세요.
                """)

            with st.expander("💡 소액 사기 예방 필수 체크리스트"):
                st.write("""
                1. **플랫폼 내부 채팅만 이용**
                2. **URL 링크 클릭 금지**
                3. **더치트 계좌/전화번호 조회 필수**
                4. **선입금 비대면 거래 주의**
                """)


# ==============================================================================
# 2. 판매자 시점 (가상 상대방 거래 시뮬레이션 기능)
# ==============================================================================
else:
    st.title("🏷️ 가상 구매자 대화 사기 위험도 진단기 (판매자용)")
    st.markdown("""
    가상의 구매자가 무작위 조건으로 거래를 요청해 옵니다.  
    **소액 상품 거래(1,000원~5,000원)**에서 발생하는 사기 수법과 안전 거래를 모의 체험해 보세요!
    """)

    st.divider()

    # 가상 세션 데이터 초기화
    if "sim_price" not in st.session_state:
        st.session_state["sim_price"] = random.randint(1000, 5000)

    if "sim_chat" not in st.session_state:
        st.session_state["sim_chat"] = "안녕하세요! 거래 잘 부탁드립니다. 직거래 가능할까요?"

    if "sim_is_scam" not in st.session_state:
        st.session_state["sim_is_scam"] = False

    # 가상 사기 / 정상 대화 풀(Pool)
    scam_chats = [
        "지금 바로 입금할 테니 네이버페이 안전결제 링크로 결제 진행해 주실 수 있나요? http://safe-pay.xyz",
        "앱 알림이 안 와서 그러는데 카카오톡으로 문의주세요! ID: fastpay99 거래 빠르게 진행해 드릴게요.",
        "제가 지금 지방 출장 중이라 문 앞에 물건 놔둬 주시면 확인 후 바로 선입금해 드리겠습니다.",
        "급하게 필요해서 그런데 지금 편의점 택배로 송장 먼저 뽑아 보내주시면 즉시 5,000원 입금해 드릴게요!"
    ]

    normal_chats = [
        "안녕하세요! 거래 잘 부탁드립니다. 혹시 어디서 직거래 가능하신가요?",
        "안녕하세요 구매 희망합니다! 당근페이로 결제하면 될까요?",
        "안녕하세요, 아직 판매 중인가요? 거래 조건 알려주시면 맞춰서 입금할게요!"
    ]

    # 가상 상황 생성 버튼
    if st.button("🎲 새로운 가상 구매자 대화 불러오기", use_container_width=True):
        st.session_state["sim_price"] = random.randint(1000, 5000)
        st.session_state["sim_is_scam"] = random.choice([True, False])
        if st.session_state["sim_is_scam"]:
            st.session_state["sim_chat"] = random.choice(scam_chats)
        else:
            st.session_state["sim_chat"] = random.choice(normal_chats)

    # 가상 거래 정보 출력
    st.header("1. 가상 거래 매칭 정보")
    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.metric("판매 지정 품목 가격", f"{st.session_state['sim_price']:,} 원")

    with sim_col2:
        st.metric("거래 유형", "소액 상품 무작위 거래")

    st.header("2. 가상 구매자가 보낸 대화 내용")
    st.info(f"💬 **가상 구매자:** \"{st.session_state['sim_chat']}\"")

    st.divider()

    st.header("3. 가상 상대방 사기 위험도 진단 결과")

    sim_chat_text = st.session_state["sim_chat"]
    sim_risk_score = 0
    sim_reasons = []

    # 정규식 패턴 분석
    pattern_messenger = re.compile(r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|아이디|ID)", re.IGNORECASE)
    pattern_link = re.compile(r"(안전결제|안전거래|네이버페이|링크|URL|http|https)", re.IGNORECASE)
    pattern_urgency = re.compile(r"(지금\s*바로|즉시|송장|편의점|급하게)", re.IGNORECASE)
    pattern_non_face = re.compile(r"(출장|지방|문\s*앞|비대면|선입금)", re.IGNORECASE)

    if pattern_link.search(sim_chat_text):
        sim_risk_score += 55
        sim_reasons.append("🔗 **외부 웹 피싱 링크 접속 유도** (가짜 결제창 위험)")

    if pattern_messenger.search(sim_chat_text):
        sim_risk_score += 30
        sim_reasons.append("📲 **앱 외 외부 메신저 유도** (플랫폼 보호 시스템 회피 시도)")

    if pattern_urgency.search(sim_chat_text):
        sim_risk_score += 20
        sim_reasons.append("⏰ **송장 우선 발송 및 선입금 유도**")

    if pattern_non_face.search(sim_chat_text):
        sim_risk_score += 20
        sim_reasons.append("🚪 **비대면 수령 및 정황상 의심 핑계**")

    # 소액 구간 경고 메시지 반영
    sim_risk_score = min(sim_risk_score, 100)

    # 게이지 색상 산정
    if sim_risk_score >= 70:
        sim_gauge_color = "#FF2B2B"  # 빨강
    elif sim_risk_score >= 40:
        sim_gauge_color = "#FF8C00"  # 주황
    elif sim_risk_score >= 20:
        sim_gauge_color = "#FFC107"  # 노랑
    else:
        sim_gauge_color = "#28A745"  # 연두

    st.subheader(f"종합 위험도 점수: **{sim_risk_score}점 / 100점**")

    # 프로그래스 바 출력
    st.markdown(f"""
    <div style="background-color: #E0E0E0; border-radius: 12px; height: 24px; width: 100%; overflow: hidden; margin-bottom: 20px;">
        <div style="background-color: {sim_gauge_color}; width: {sim_risk_score}%; height: 100%; border-radius: 12px; transition: width 0.6s ease-in-out;"></div>
    </div>
    """, unsafe_allow_html=True)

    # 진단 결과 판정
    if sim_risk_score >= 50:
        st.error(f"🚨 **[위험도 높음] 해당 가상 거래는 사기 가능성이 매우 높은 패턴입니다!**")
        st.markdown(f"""
        * **위험 요인:** {', '.join(sim_reasons)}
        * **경고 가이드:** {st.session_state['sim_price']:,}원 상당의 소액 상품 거래라 할지라도, 제3자 사기나 가짜 안전결제 피싱 링크를 이용한 개인정보 탈취 시도일 수 있습니다. 해당 거래 요청을 즉시 거절하세요.
        """)
    else:
        st.success("✅ **[위험도 낮음] 소액 사기 패턴이 발견되지 않은 일상적인 거래 대화입니다.**")
        st.markdown(f"""
        * **분석 내용:** 대화 속에 외부 메신저 유도, 피싱 URL 링크, 송장 선발송 요구나 비정상적 요구가 없습니다.
        * **거래 가이드:** 안전한 거래를 위해 항상 앱 내 결제 수단 및 채팅창을 통해서만 거래를 이어 나가세요.
        """)

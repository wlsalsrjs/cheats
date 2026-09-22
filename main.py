import streamlit as st
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="중고거래 대화 기반 사기 위험도 진단기",
    page_icon="💬",
    layout="centered"
)

st.title("💬 중고거래 대화 내용 기반 사기 진단기")
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

# 2. 대화 내용 입력
st.header("2. 상대방과의 대화 내용 입력")
user_chat = st.text_area(
    "카톡, 문자, 당근챗 등에서 상대방과 주고받은 대화를 복사해서 붙여넣으세요:",
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

        # --- 사기 패턴 키워드 정규식 규칙 정의 ---
        
        # 1. 외부 메신저 유도 패턴
        pattern_messenger = re.compile(
            r"(카톡|카카오톡|오픈채팅|오픈톡|문자|라인|텔레그램|알림이\s*안|앱이\s*이상|아이디|ID|톡주|톡으로)",
            re.IGNORECASE
        )
        # 2. 가짜 안전결제 및 링크 유도 패턴
        pattern_link = re.compile(
            r"(안전결제|안전거래|네이버페이|중고나라페이|링크|URL|http|https|사이트|페이지|수수료|오류|재입금|환불)",
            re.IGNORECASE
        )
        # 3. 시간 압박 및 입금 독촉 패턴
        pattern_urgency = re.compile(
            r"(지금\s*바로|즉시|다른\s*분|먼저\s*입금|급매|오늘만|택배\s*붙이|택배\s*보내|송장|편의점)",
            re.IGNORECASE
        )
        # 4. 회피형 직거래 핑계 및 비대면 선입금 패턴
        pattern_non_face = re.compile(
            r"(출장|지방|근무|비대면|문\s*앞|현관|비밀번호|동호수|대신|선입금)",
            re.IGNORECASE
        )

        # --- 대화 내용 분석 ---
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

        # --- 가공 조건 반영 (가격 및 거래 경험) ---
        if 10000 <= price <= 150000:
            risk_score += 10  # 소액사기 다발 구간

        if trade_count <= 1:
            risk_score += 5  # 초보자 가산점

        # 점수 캡핑 (최대 100점)
        risk_score = min(risk_score, 100)

        # --- 결과 출력 ---
        st.subheader(f"위험도 점수: **{risk_score}점 / 100점**")
        st.progress(risk_score / 100)

        # 감지된 패턴 표시
        if detected_patterns:
            st.markdown("### 🔍 대화 속에서 감지된 사기 의심 패턴:")
            for pattern in detected_patterns:
                st.write(f"- {pattern}")
            st.write("")

        # 위험도 단계별 가이드
        if risk_score >= 65:
            st.error("🚨 **[위험등급: 매우 위험] 거래를 즉시 중단하세요!**")
            st.markdown("""
            * **분석:** 전형적인 중고거래 사기범들의 대화 패턴이 대거 감지되었습니다.
            * **주의사항:** 특히 외부 링크를 통한 안전결제 요구나 카카오톡 등 외부 메신저로 대화를 유도하는 행위는 99% 이상 사기 수법입니다. 절대로 입금하지 마세요.
            """)
        elif risk_score >= 35:
            st.warning("⚠️ **[위험등급: 주의] 신중한 확인이 필요합니다.**")
            st.markdown("""
            * **분석:** 대화 내용 중 사기 의심 키워드가 일부 포함되어 있습니다.
            * **주의사항:** 입금 전 반드시 **더치트**나 **경찰청 사이버캅**에서 상대방 계좌/전화번호를 검색해 보세요.
            """)
        else:
            st.success("✅ **[위험등급: 비교적 안전] 기본 거래 수칙을 준수하세요.**")
            st.markdown("""
            * **분석:** 전형적인 사기 대화 패턴이 뚜렷하게 감지되지 않았습니다.
            * **주의사항:** 다만 대화 외적인 정황이 있을 수 있으니, 항상 앱 내부 채팅망과 정식 거래 시스템만 이용해 주세요.
            """)

        # 종합 예방 팁
        with st.expander("💡 소액 사기 예방 필수 체크리스트"):
            st.write("""
            1. **플랫폼 내부 채팅만 이용:** 카톡 ID나 오픈채팅 이동 요구는 거절하세요.
            2. **메시지로 받은 URL 링크 클릭 금지:** 네이버페이/중고나라 안전결제 링크는 100% 피싱입니다.
            3. **계좌 조회 필수:** 입금 전 더치트(The Cheat) 앱에서 사기 이력을 조회하세요.
            4. **선입금 비대면 직거래 금지:** "문 앞에 뒀으니 입금하라"는 식의 거래는 응하지 마세요.
            """)

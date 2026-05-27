import streamlit as st
from konlpy.tag import Okt
import os
from PIL import Image

# 1. 페이지 설정 (웹사이트 제목 및 아이콘)
st.set_page_config(page_title="마음 레시피 챗봇", page_icon="❤️")

# 2. 형태소 분석기 초기화
@st.cache_resource
def load_okt():
    return Okt()

okt = load_okt()

# 3. 화면 구성
st.title("❤️ 마음 레시피 챗봇")
st.write("아이들의 마음을 읽고, 따뜻한 레시피를 전해줍니다.")

user_input = st.text_input("지금 기분이 어때요? 마음을 들려주세요.", placeholder="예: 오늘 친구랑 싸워서 너무 슬퍼요")

if user_input:
    # 1. 입력값 앞뒤 공백 제거 및 소문자화
    user_input = user_input.strip().lower()
    
    # 2. 현재 폴더의 모든 파일 목록 가져오기 및 한글 정규화(맥북 호환)
    import os
    import unicodedata
    all_files = os.listdir(".")
    
    file_dict = {}
    for f in all_files:
        normalized_name = unicodedata.normalize('NFC', f)
        name_without_ext, ext = os.path.splitext(normalized_name)
        if ext.lower() in [".png", ".jpg", ".jpeg"]:
            file_dict[name_without_ext.strip().lower()] = f # { '파일명': '실제파일명.png' }

    matched_actual_file = None
    target_emotion = None

    # --- [핵심] '감동적', '감동적임'을 위한 최우선 예외 처리 ---
    if "감동적" in user_input:
        target_emotion = "감동적"
        if "감동적" in file_dict:
            matched_actual_file = file_dict["감동적"]

    # --- 만약 '감동적'이 아니라면 원래대로 형태소 분석 진행 ---
    if not matched_actual_file:
        words = okt.pos(user_input, stem=True)
        emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
        
        for word, pos in words:
            target = emotion_map.get(word, word).lower()
            if target in file_dict:
                matched_actual_file = file_dict[target]
                target_emotion = target
                break

    # --- 최종 결과 출력 ---
    if matched_actual_file:
        st.success(f"▶ '{target_emotion if target_emotion else user_input}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
        img = Image.open(matched_actual_file)
        st.image(img, use_container_width=True)
    else:
        st.warning("미안해요, 그 마음에 대한 재료는 아직 준비 중이에요.")
        
        # 디버깅용: 인식이 안 될 때 서버에 저장된 이미지 파일 목록을 화면에 띄워줍니다.
        st.write("---")
        st.write("💡 **현재 서버에 있는 이미지 파일 목록:**")
        st.write(list(file_dict.keys()))

# 하단 정보
st.info("본 프로그램은 감정 어휘 교육용 챗봇입니다.")

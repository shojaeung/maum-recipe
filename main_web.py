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
    # 1. 입력값의 앞뒤 공백 제거 및 소문자화, 띄어쓰기 제거 버전도 준비
    user_input = user_input.strip().lower()
    user_input_no_space = user_input.replace(" ", "")
    
    # 2. 현재 폴더의 모든 파일 목록 가져오기 및 한글 정규화
    import os
    import unicodedata
    all_files = os.listdir(".")
    
    matched_actual_file = None
    matched_emotion_name = ""
    
    # --- 1단계: 완벽하게 일치하거나 포함되는 파일이 있는지 먼저 검사 ---
    for f in all_files:
        normalized_f = unicodedata.normalize('NFC', f)
        name_without_ext, ext = os.path.splitext(normalized_f)
        
        # 이미지 파일만 검사
        if ext.lower() in [".png", ".jpg", ".jpeg"]:
            pure_file_name = name_without_ext.strip().lower()
            pure_file_no_space = pure_file_name.replace(" ", "")
            
            # [규칙] 입력어가 파일명에 포함되거나, 파일명이 입력어에 포함되는 경우 (띄어쓰기 무시)
            if (user_input_no_space in pure_file_no_space) or (pure_file_no_space in user_input_no_space):
                matched_actual_file = f  # 실제 확장자가 붙은 파일명 저장 (.png 포함)
                matched_emotion_name = name_without_ext # 화면 표시용 이름
                break

    # --- 2단계: 만약 그래도 못 찾았다면 형태소 분석기 최종 가동 ---
    if not matched_actual_file:
        words = okt.pos(user_input, stem=True)
        emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
        
        for word, pos in words:
            target = emotion_map.get(word, word).lower()
            for f in all_files:
                normalized_f = unicodedata.normalize('NFC', f)
                name_without_ext, ext = os.path.splitext(normalized_f)
                
                if ext.lower() in [".png", ".jpg", ".jpeg"]:
                    pure_file_name = name_without_ext.strip().lower()
                    if target in pure_file_name:
                        matched_actual_file = f
                        matched_emotion_name = name_without_ext
                        break
            if matched_actual_file:
                break

    # --- 3단계: 결과 출력 ---
    if matched_actual_file:
        st.success(f"▶ '{matched_emotion_name}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
        img = Image.open(matched_actual_file)
        st.image(img, use_container_width=True)
    else:
        st.warning("미안해요, 그 마음에 대한 재료는 아직 준비 중이에요.")
        
        # 디버깅용 파일 목록 표시
        st.write("---")
        st.write("💡 **현재 서버에 있는 실제 이미지 파일 목록:**")
        image_files = [unicodedata.normalize('NFC', f) for f in os.listdir(".") if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        st.write(image_files)

# 하단 정보
st.info("본 프로그램은 감정 어휘 교육용 챗봇입니다.")

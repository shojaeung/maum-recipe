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
st.title("❤마음 메뉴판❤")
st.write("3학년 학생들이 제작에 참여한 마음 메뉴판(디지털 감정 사전)입니다.")

user_input = st.text_input("알아보고 싶은 감정 재료(감정 어휘)를 입력해주세요.", placeholder="예: 감동적")

if user_input:
    # 1. 입력값의 앞뒤 공백을 제거하고 형태소 분석 진행
    user_input = user_input.strip()
    words = okt.pos(user_input, stem=True)
    
    emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
    
    # 2. 현재 폴더에 있는 모든 파일 목록을 가져옵니다.
    import unicodedata
    all_files = os.listdir(".")
    
    # 비교를 위해 파일 목록의 한글 형식을 통일(정규화)합니다.
    file_dict = {}
    for f in all_files:
        normalized_name = unicodedata.normalize('NFC', f)
        file_dict[normalized_name] = f  # { 정규화된이름: 실제파일명 }
    
    found = False
    
    for word, pos in words:
        # 3. 매핑 단어가 있으면 바꾸고, 없으면 분석된 단어를 그대로 씁니다.
        target = emotion_map.get(word, word)
        
        # 4. 파일 목록 중에서 target 이름과 확장자가 맞는 파일이 있는지 찾습니다.
        extensions = [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG"]
        matched_actual_file = None
        
        for ext in extensions:
            expected_filename = f"{target}{ext}"
            if expected_filename in file_dict:
                matched_actual_file = file_dict[expected_filename]
                break
        
        # 5. 파일이 매칭되었다면 화면에 표시
        if matched_actual_file:
            st.success(f"▶ '{target}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
            img = Image.open(matched_actual_file)
            st.image(img, use_container_width=True)
            found = True
            break
            
    # 6. 만약 형태소 분석 결과로 못 찾았다면, 사용자가 입력한 텍스트 그대로 파일이 있는지 마지막으로 확인합니다.
    if not found:
        for ext in extensions:
            expected_filename = f"{user_input}{ext}"
            if expected_filename in file_dict:
                matched_actual_file = file_dict[expected_filename]
                st.success(f"▶ '{user_input}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
                img = Image.open(matched_actual_file)
                st.image(img, use_container_width=True)
                found = True
                break

    if not found:
        st.warning("미안해요, 그 마음에 대한 재료는 아직 준비 중이에요.")
        # 디버깅용 힌트: 실제로 분석된 단어가 무엇인지 화면에 살짝 띄워줍니다.
        st.write("🔍 시스템이 인식한 단어 후보:", [word for word, pos in words])

# 하단 정보
st.info("본 프로그램은 감정 어휘 교육용 챗봇입니다.")

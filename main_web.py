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
    # 형태소 분석
    words = okt.pos(user_input, stem=True)
    
    found = False
    emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
    
    for word, pos in words:
        target = emotion_map.get(word, word)
        file_path = f"{target}.jpg" # 이미지 파일명
        
        if os.path.exists(file_path):
            st.success(f"▶ '{target}'(이)라는 마음을 발견했어요! 레시피를 보여줄게요.")
            img = Image.open(file_path)
            st.image(img, use_container_width=True) # 웹 화면에 이미지 표시
            found = True
            break
            
    if not found:
        st.warning("미안해요, 그 마음에 대한 레시피는 아직 준비 중이에요.")

# 하단 정보
st.info("본 프로그램은 AI-TPACK 모델을 기반으로 제작된 교육용 챗봇입니다.")

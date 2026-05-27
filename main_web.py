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
    # 1. 입력값 공백 제거 및 소문자화(혹시 모를 영문 대비)
    user_input = user_input.strip().lower()
    words = okt.pos(user_input, stem=True)
    
    emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
    
    # 2. 현재 폴더의 모든 파일 목록 가져오기 및 한글 정규화(맥북 호환)
    import unicodedata
    all_files = os.listdir(".")
    
    file_list = [] # (정규화된 파일명, 확장자를 제외한 순수 파일명, 실제 파일명) 구조로 저장
    for f in all_files:
        normalized_name = unicodedata.normalize('NFC', f)
        name_without_ext, ext = os.path.splitext(normalized_name)
        file_list.append({
            "pure_name": name_without_ext.strip().lower(), # 확장자 뗀 이름 (예: '감동적')
            "actual_name": f # 실제 파일명 (예: '감동적.png')
        })
    
    found = False
    matched_actual_file = None
    matched_target_name = ""

    # --- 1단계: 형태소 분석 및 매핑 단어로 완벽 일치하는지 먼저 확인 ---
    for word, pos in words:
        target = emotion_map.get(word, word).lower()
        for f_info in file_list:
            if f_info["pure_name"] == target:
                matched_actual_file = f_info["actual_name"]
                matched_target_name = target
                found = True
                break
        if found:
            break

    # --- 2단계: (실패 시) 사용자가 입력한 문장과 파일 이름 간의 포함 관계 조사 ---
    if not found:
        for f_info in file_list:
            pure_file_name = f_info["pure_name"]
            
            # 예: 파일명이 '감동적'인데 입력이 '감동'인 경우, 또는 파일명이 '감동적'인데 입력이 '감동적임'인 경우
            if (pure_file_name in user_input) or (user_input in pure_file_name):
                matched_actual_file = f_info["actual_name"]
                matched_target_name = pure_file_name
                found = True
                break

    # --- 3단계: 결과 출력 ---
    if found and matched_actual_file:
        st.success(f"▶ '{user_input}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
        img = Image.open(matched_actual_file)
        st.image(img, use_container_width=True)
    else:
        st.warning("미안해요, 그 마음에 대한 재료는 아직 준비 중이에요.")
        # 디버깅용 힌트
        st.write("🔍 시스템이 인식한 단어 후보:", [word for word, pos in words])

# 하단 정보
st.info("본 프로그램은 감정 어휘 교육용 챗봇입니다.")

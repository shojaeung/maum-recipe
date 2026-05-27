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
    # 1. 입력값의 앞뒤 공백을 제거하고 소문자로 통일
    user_input = user_input.strip().lower()
    
    # 2. 현재 폴더에 있는 모든 파일 목록을 가져와서 한글 정규화(맥북 호환)
    import unicodedata
    all_files = os.listdir(".")
    
    file_list = []
    for f in all_files:
        normalized_name = unicodedata.normalize('NFC', f)
        name_without_ext, ext = os.path.splitext(normalized_name)
        
        # 이미지 파일 확장자만 골라내기
        if ext.lower() in [".png", ".jpg", ".jpeg"]:
            file_list.append({
                "pure_name": name_without_ext.strip().lower(), # 확장자 뺀 파일명 (예: '감동적', '약이 오름')
                "actual_name": f # 실제 파일명 (예: '감동적.png')
            })
            
    matched_actual_file = None
    max_match_length = 0  # 가장 많이 겹치는 글자 수를 저장할 변수

    # --- [핵심 로직] 전체 파일 목록을 돌면서 가장 정확한 파일 찾기 ---
    for f_info in file_list:
        pure_file_name = f_info["pure_name"]
        actual_name = f_info["actual_name"]
        
        # 1) 입력값과 파일명이 100% 똑같다면 이게 정답입니다. (예: '감동적' 입력 -> '감동적.png')
        if pure_file_name == user_input:
            matched_actual_file = actual_name
            break  # 완벽히 일치하면 더 볼 것도 없이 종료
            
        # 2) 100% 일치가 아니라면 포함 관계를 따집니다.
        # 공백을 없애고 비교하여 '약이오름'과 '약이 오름'도 매칭되도록 만듭니다.
        pure_file_no_space = pure_file_name.replace(" ", "")
        user_input_no_space = user_input.replace(" ", "")
        
        if (pure_file_no_space in user_input_no_space) or (user_input_no_space in pure_file_no_space):
            # 겹치는 글자의 길이를 구합니다.
            # 이 과정이 있어야 '약이 오름'을 입력했을 때 '약'이 아니라 글자 수가 더 많이 겹치는 '약이 오름' 파일이 선택됩니다.
            match_length = len(pure_file_name)
            
            if match_length > max_match_length:
                max_match_length = match_length
                matched_actual_file = actual_name

    # --- 3단계: 결과 출력 ---
    if matched_actual_file:
        st.success(f"▶ '{user_input}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
        img = Image.open(matched_actual_file)
        st.image(img, use_container_width=True)
    else:
        # 혹시나 위의 검사로도 못 찾았다면 마지막 보루로 형태소 분석기 작동
        words = okt.pos(user_input, stem=True)
        emotion_map = {"슬프다": "슬픔", "기쁘다": "기쁨", "화나다": "분노", "당황하다": "당황"}
        
        found_by_okt = False
        for word, pos in words:
            target = emotion_map.get(word, word).lower()
            for f_info in file_list:
                if f_info["pure_name"] == target:
                    st.success(f"▶ '{user_input}'(이)라는 감정재료를 발견했어요! 지금 보여줄게요.")
                    img = Image.open(f_info["actual_name"])
                    st.image(img, use_container_width=True)
                    found_by_okt = True
                    break
            if found_by_okt:
                break
                
        if not found_by_okt:
            st.warning("미안해요, 그 마음에 대한 재료는 아직 준비 중이에요.")
            st.write("🔍 시스템이 인식한 단어 후보:", [word for word, pos in words])

# 하단 정보
st.info("본 프로그램은 감정 어휘 교육용 챗봇입니다.")

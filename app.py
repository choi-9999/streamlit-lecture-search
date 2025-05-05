import streamlit as st
import pandas as pd
import base64
import os

st.set_page_config(page_title="이투스247 인강&교재 검색기", layout="wide")

# ------------------------
# 스타일
# ------------------------
st.markdown('''
<style>
.card-box {
    background-color: var(--background-color, #f9f9f9);
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card-box:hover {
    transform: scale(1.01);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
.highlight-title {
    background-color: #C4F500;
    display: inline-block;
    padding: 6px 10px;
    font-weight: 700;
    font-size: 1.2rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.card-list {
    padding-left: 1.2rem;
}
.card-list li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
}
.meta-button {
    background-color: #f1f1f1;
    border: none;
    border-radius: 20px;
    padding: 0.4rem 1.2rem;
    margin: 0.2rem;
    font-size: 0.9rem;
    font-weight: 500;
    display: inline-block;
    transition: all 0.2s ease-in-out;
}
.meta-button:hover {
    background-color: #C4F500;
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(196, 245, 0, 0.3);
}
.button-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}
:root {
  --background-color: #f9f9f9;
  --text-color: #222222;
}
@media (prefers-color-scheme: dark) {
  :root {
    --background-color: #1e1e1e;
    --text-color: #dddddd;
  }

  .meta-button {
    background-color: #2c2c2c !important;
    color: #eeeeee !important;
    border: 1px solid #444444;
  }

  .meta-button:hover {
    background-color: #C4F500 !important;
    color: black !important;
  }
}
div.stButton > button:hover {
    border: 1px solid #C4F500 !important;
    color: #000000 !important;
    background-color: #ecffb6 !important;
    transition: all 0.2s ease-in-out;            
}
div.stButton > button:active {
    color: #C4F500 !important;      
    background-color: inherit !important;
    border: 1px solid #C4F500 !important;
}
</style>
''', unsafe_allow_html=True)

# ------------------------
# 로고 출력
# ------------------------
# 🔶 로고 base64로 변환하여 중앙 정렬 표시
def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_base64_image(path, width=250):
    try:
        img_base64 = image_to_base64(path)
        img_html = f"<img src='data:image/png;base64,{img_base64}' width='{width}'/>"
        st.markdown(img_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.write("🖼 이미지 파일을 찾을 수 없습니다.")

logo_base64 = image_to_base64("이투스247학원 BI(기본형).png")

# 가로 정렬된 로고 + 텍스트 헤더
st.markdown(f"""
<div style='display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; margin-bottom: 2rem;'>
    <img src='data:image/png;base64,{logo_base64}' width='150' style='vertical-align: middle;' />
    <h1 style='margin: 0; font-size: 2.2rem;'>인강&교재 검색기 🔍</h1>
</div>
""", unsafe_allow_html=True)

# ------------------------
# 데이터 로딩
# ------------------------
@st.cache_data
def load_lecture_data():
    return pd.read_excel("lecture_data.xlsx", sheet_name="인강")

@st.cache_data
def load_textbook_data():
    return pd.read_excel("textbook_data.xlsx")

df = load_lecture_data()
tdf = load_textbook_data()

# ------------------------
# 탭 구성
# ------------------------
tabs = st.tabs(["🧑‍🏫 인강 검색기", "📘 교재 검색기"])

# ------------------------
# 🔍 인강 검색기 탭
# ------------------------
with tabs[0]:
    # 🔶 데이터 불러오기
    @st.cache_data
    def load_data():
        return pd.read_excel("lecture_data.xlsx", sheet_name="인강")

    df = load_data()

    if "selected_lecture" not in st.session_state:
        st.session_state["selected_lecture"] = None

    # 🔶 필터 입력
    with st.markdown("""
        <div style='display: flex; justify-content: center;'>
            <div style='width: 320px;'>
        """, unsafe_allow_html=True):
        
        강사명 = st.text_input(
            "강사 검색", 
            placeholder="강사명을 입력하세요 (예: 정승제)", 
            key="강사입력", 
            label_visibility="collapsed"
        )

    st.markdown("</div></div>", unsafe_allow_html=True)
    if not 강사명:
        st.session_state["selected_lecture"] = None

    if 강사명:
        filtered = df[df["강사명"].str.contains(강사명, na=False)]

        if filtered.empty:
            st.warning("해당 강사의 강의가 없습니다.")
        else:
            st.markdown("<div class='highlight-title'>📚 강의 목록</div>", unsafe_allow_html=True)
            
            if st.session_state.get("selected_lecture") is None or (
                st.session_state["selected_lecture"]["강사명"] != 강사명
            ):
                st.session_state["selected_lecture"] = filtered.iloc[0]
                
            chunk_size = 3
            rows = [filtered.iloc[i:i+chunk_size] for i in range(0, len(filtered), chunk_size)]
            for row in rows:
                cols = st.columns(chunk_size)
                for i, (_, r) in enumerate(row.iterrows()):
                    with cols[i]:
                        if st.button(r["강좌명"], key=f"lecture_button_{r.name}"):
                            st.session_state["selected_lecture"] = r

    # 🔶 카드 상세 보기
    selected = st.session_state["selected_lecture"]
    if selected is not None:
        col1, col2 = st.columns([1, 2])

        with col1:
            img_path = selected["강사 이미지"]

            if isinstance(img_path, str):
                if img_path.startswith("http"):
                    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                    st.image(img_path, width=400)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                    render_base64_image(img_path, width=400)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.write("🖼 강사 이미지 없음")

            label_map = {
                "과목": "과목",
                "사이트": "사이트명",
                "추천시기": "추천시기",
                "추천레벨": "추천레벨",
                "강의성격": "강의성격"
            }
            button_html = '<div class="button-wrap">'
            for label, col in label_map.items():
                val = selected[col] if col in selected and pd.notna(selected[col]) else ""
                button_html += f'<span class="meta-button">{val}</span>'
            button_html += '</div>'
            st.markdown(button_html, unsafe_allow_html=True)

        with col2:
            def make_card(title, content):
                items = ''.join(f"<li>{line.strip()}</li>" for line in content.splitlines() if line.strip())
                return f'''
                <div class="card-box">
                    <div class="highlight-title">{title}</div>
                    <ul class="card-list">{items}</ul>
                </div>
                '''
            구성 = make_card("📘 강의 구성 및 커리큘럼", f"{selected['총강의수/평균런닝타임']}\n커리큘럼: {selected['커리큘럼']}")
            수강 = make_card("🎯 추천 학생", selected["수강대상"])
            특징 = make_card("📝 강의 내용 및 특징", selected["내용/특징"])
            st.markdown(구성, unsafe_allow_html=True)
            st.markdown(수강, unsafe_allow_html=True)
            st.markdown(특징, unsafe_allow_html=True)

# ------------------------
# 📘 교재 검색기 탭
# ------------------------
with tabs[1]:
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        custom_subject_order = ["국어", "수학", "영어", "한국사", "물리학", "화학", "생명과학", "지구과학", "사회문화", "생활과윤리", "윤리와사상", "한국지리", "세계지리", "동아시아사", "세계사", "정치와법", "경제", "통합사회", "통합과학"]
        과목목록 = [과목 for 과목 in custom_subject_order if 과목 in tdf["과목"].dropna().unique()]
        선택과목 = st.selectbox("과목 선택 (선택 시 해당 과목만 표시)", ["전체"] + 과목목록)
    with col_filter2:
        custom_publisher_order = ["ETOOS", "메가스터디", "대성", "시대인재", "EBS", "기타"]
        출판사목록 = [출판사 for 출판사 in custom_publisher_order if 출판사 in tdf["출판사"].dropna().unique()]
        선택출판사 = st.selectbox("출판사 선택 (선택 시 해당 출판사만 표시)", ["전체"] + 출판사목록)

    # 과목과 출판사 필터링 적용
    filtered_df = tdf.copy()
    if 선택과목 != "전체":
        filtered_df = filtered_df[filtered_df["과목"] == 선택과목]
    if 선택출판사 != "전체":
        filtered_df = filtered_df[filtered_df["출판사"] == 선택출판사]
    
    교재목록 = sorted(filtered_df["교재명"].dropna().unique())
    
    if len(교재목록) == 0:
        st.warning("해당 조건에 맞는 교재가 없습니다.")
        교재명 = None
    else:
        교재명 = st.selectbox("교재명 선택 또는 검색", 교재목록, index=None, placeholder="교재명을 입력하거나 선택하세요")

    if 교재명:
        selected = tdf[tdf["교재명"] == 교재명].iloc[0]
        col1, col2 = st.columns([1, 2])

        with col1:
            img_path = selected["도서 이미지"]

            if isinstance(img_path, str):
                st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                
                if img_path.startswith("http"):
                    st.image(img_path, width=400)
                elif os.path.exists(img_path):
                    img_base64 = image_to_base64(img_path)
                    st.markdown(f"<img src='data:image/png;base64,{img_base64}' width='400'>", unsafe_allow_html=True)
                else:
                    st.write("🖼 이미지 없음")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.write("🖼 이미지 없음")

            label_map = {
                "과목": "과목", "출판사": "출판사", "추천시기": "추천시기", "추천등급": "추천등급", "교재성격": "교재성격"
            }
            button_html = '<div class="button-wrap">'
            for label, col in label_map.items():
                val = selected.get(col, "")
                button_html += f'<span class="meta-button">{val}</span>'
            button_html += '</div>'
            st.markdown(button_html, unsafe_allow_html=True)

        with col2:
            def make_card(title, content):
                items = ''.join(f"<li>{line.strip()}</li>" for line in content.splitlines() if line.strip())
                return f'''<div class="card-box"><div class="highlight-title">{title}</div><ul class="card-list">{items}</ul></div>'''

            구성 = make_card("📘 문제구성 난이도", selected["문제구성 난이도"])
            수강 = make_card("🎯 추천 학생", selected["추천 학생"])
            특징 = make_card("📖 도서 특징", selected["도서 특징"])

            st.markdown(구성, unsafe_allow_html=True)
            st.markdown(수강, unsafe_allow_html=True)
            st.markdown(특징, unsafe_allow_html=True)

import streamlit as st
import pdfplumber
import random
import re

st.set_page_config(page_title="랜덤 텍스트 피드", layout="centered")
st.title("📖 랜덤 텍스트 피드 (속도 최적화 + PDF/텍스트 지원)")

# 세션 상태 초기화
if 'texts' not in st.session_state:
    st.session_state.texts = []  # (title, sentence)
if 'feed' not in st.session_state:
    st.session_state.feed = []

# 문장 단위 분할 함수
def split_into_sentences(text, max_len=280):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(sent) <= max_len:
            chunks.append(sent)
        else:
            for i in range(0, len(sent), max_len):
                chunks.append(sent[i:i+max_len].strip())
    return chunks

# PDF 처리 + 캐싱
@st.cache_data(show_spinner=False)
def extract_sentences_from_pdf(file):
    pdf_title = file.name
    sentences = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                chunks = split_into_sentences(text)
                sentences.extend([(pdf_title, s) for s in chunks])
    return sentences

# TXT 처리 + 캐싱
@st.cache_data(show_spinner=False)
def extract_sentences_from_txt(file):
    txt_title = file.name
    text = file.read().decode("utf-8")
    sentences = split_into_sentences(text)
    return [(txt_title, s) for s in sentences]

# 파일 업로드
uploaded_files = st.file_uploader(
    "📄 PDF 또는 TXT 업로드 (여러 개 가능)", 
    type=["pdf","txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            sentences = extract_sentences_from_pdf(uploaded_file)
        else:
            sentences = extract_sentences_from_txt(uploaded_file)
        st.session_state.texts.extend(sentences)
    st.success(f"{len(st.session_state.texts)} 문장 추출 완료!")

# 버튼 영역
col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 랜덤 텍스트 추가"):
        if st.session_state.texts:
            title, new_text = random.choice(st.session_state.texts)
            st.session_state.feed.insert(0, (title, new_text))
            st.session_state.feed = st.session_state.feed[:10]

with col2:
    if st.button("🔁 연속 랜덤 5개 추가"):
        if st.session_state.texts:
            for _ in range(min(5, len(st.session_state.texts))):
                st.session_state.feed.insert(0, random.choice(st.session_state.texts))
            st.session_state.feed = st.session_state.feed[:10]

# 피드 출력: 카드에는 텍스트만, 클릭하면 출처 확인
if st.session_state.feed:
    st.markdown("### 📰 최신 랜덤 텍스트 (최대 10개)")
    for title, txt in st.session_state.feed:
        with st.expander(txt):
            st.markdown(f"**출처:** {title}")
else:
    st.info("PDF 또는 TXT 파일을 업로드하세요.")

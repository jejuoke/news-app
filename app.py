import streamlit as st
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
from dateutil import parser 
from datetime import datetime, timedelta
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="News Insights", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .block-container { padding-top: 3.5rem !important; padding-bottom: 1rem !important; }
    .main-title { font-size: 1.4rem !important; font-weight: 800; color: #1a1a1a; margin-bottom: 1.2rem; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0078D4; color: white; height: 3em; font-weight: bold; border: none; }
    .news-card { background-color: white; padding: 12px 15px; border-radius: 10px; box-shadow: 0px 1px 3px rgba(0,0,0,0.05); margin-bottom: 10px; border: 1px solid #eee; }
    .news-title { font-size: 0.95rem !important; font-weight: 600; line-height: 1.4; margin-bottom: 5px; }
    .news-title a { text-decoration: none; color: #1a1a1a; }
    .kst-time { color: #999; font-size: 0.7rem; margin-top: 2px; }
    .sentiment-tag { font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-bottom: 6px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# --- [추가] 경제/원전 특화 사전 로직 ---
def get_custom_sentiment(title, base_score):
    # 호재 키워드 (+점수)
    pos_words = ['수주', '계약', '체결', '승인', '확정', '최초', '돌파', '상승', '협력', 'MOU', '착공', '국산화', '러브콜', '흑자전환', '추가증설', '대거']
    # 악재 키워드 (-점수)
    neg_words = ['중단', '해지', '취소', '검찰', '조사', '압수수색', '적자', '하락', '폭락', '지연', '결함', '사고', '유지보수', '논란']
    
    score = base_score
    for word in pos_words:
        if word in title: score += 0.4  # 호재 단어 발견 시 점수 대폭 상승
    for word in neg_words:
        if word in title: score -= 0.4  # 악재 단어 발견 시 점수 대폭 하락
    return score

# 대제목 및 검색
st.markdown('<div class="main-title">🚀 실시간 뉴스 분석</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("검색어", value="원전", placeholder="키워드 입력", label_visibility="collapsed")
with col2:
    search_btn = st.button("검색")

if search_btn or query:
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    
    if not feed.entries:
        st.error("결과가 없습니다.")
    else:
        analyzed_list = []
        for e in feed.entries:
            raw_dt = parser.parse(e.published).replace(tzinfo=None)
            kst_dt = raw_dt + timedelta(hours=9)
            title = e.title.split(' - ')[0]
            
            # 감성 분석 + 커스텀 사전 적용
            try:
                en_title = translator.translate(title)
                base_score = analyzer.polarity_scores(en_title)['compound']
                final_score = get_custom_sentiment(title, base_score)
            except: final_score = 0
            
            if final_score >= 0.15: # 기준치를 약간 높여서 더 명확히 구분
                tag, bg, txt = "📈 호재", "#e1f5fe", "#01579b"
            elif final_score <= -0.15:
                tag, bg, txt = "📉 악재", "#ffebee", "#c62828"
            else:
                tag, bg, txt = "😐 중립", "#f5f5f5", "#424242"
            
            st.markdown(f"""
                <div class="news-card">
                    <div class="sentiment-tag" style="background-color: {bg}; color: {txt};">{tag}</div>
                    <div class="news-title"><a href="{e.link}" target="_blank">{title}</a></div>
                    <div class="kst-time">⏰ {kst_dt.strftime('%m-%d %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)

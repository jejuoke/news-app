import streamlit as st
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
from dateutil import parser 
from datetime import datetime, timedelta
import urllib.parse

# 1. 페이지 설정 및 디자인 최적화
st.set_page_config(page_title="News Insights", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 상단 여백 압축 */
    .main { background-color: #f5f7f9; }
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; }
    
    /* 대제목 스타일 수정 (크기 축소) */
    .main-title { 
        font-size: 1.4rem !important; 
        font-weight: 800; 
        color: #1a1a1a; 
        margin-bottom: 0.5rem;
        letter-spacing: -0.05rem;
    }
    
    /* 검색창과 버튼 디자인 */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0078D4; color: white; height: 3em; font-weight: bold; border: none; }
    .stTextInput>div>div>input { border-radius: 8px !important; }

    /* 뉴스 카드 디자인 */
    .news-card { 
        background-color: white; 
        padding: 12px 15px; 
        border-radius: 10px; 
        box-shadow: 0px 1px 3px rgba(0,0,0,0.05); 
        margin-bottom: 10px; 
        border: 1px solid #eee;
    }
    
    /* 뉴스 제목 스타일 (한 층 더 최적화) */
    .news-title { 
        font-size: 0.95rem !important; 
        font-weight: 600; 
        line-height: 1.4;
        margin-bottom: 5px;
        display: block;
    }
    .news-title a { text-decoration: none; color: #1a1a1a; }
    
    .kst-time { color: #999; font-size: 0.7rem; }
    .sentiment-tag { 
        font-size: 0.65rem; 
        padding: 1px 5px; 
        border-radius: 4px; 
        font-weight: bold; 
        margin-bottom: 6px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# 수정된 대제목 (HTML로 직접 제어)
st.markdown('<div class="main-title">🚀 실시간 뉴스 분석</div>', unsafe_allow_html=True)

# 검색 영역
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("", value="원전", placeholder="키워드 입력", label_visibility="collapsed")
with col2:
    search_btn = st.button("검색")

if search_btn or query:
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    now_pc = datetime.now()
    
    if not feed.entries:
        st.error("결과가 없습니다.")
    else:
        analyzed_list = []
        for e in feed.entries:
            raw_dt = parser.parse(e.published).replace(tzinfo=None)
            kst_dt = raw_dt + timedelta(hours=9)
            analyzed_list.append({'title': e.title.split(' - ')[0], 'link': e.link, 'kst_dt': kst_dt})
        
        sorted_list = sorted(analyzed_list, key=lambda x: x['kst_dt'], reverse=True)

        for item in sorted_list[:15]:
            try:
                en_title = translator.translate(item['title'])
                score = analyzer.polarity_scores(en_title)['compound']
            except: score = 0
            
            if score >= 0.05:
                tag, bg, txt = "📈 호재", "#e1f5fe", "#01579b"
            elif score <= -0.05:
                tag, bg, txt = "📉 악재", "#ffebee", "#c62828"
            else:
                tag, bg, txt = "😐 중립", "#f5f5f5", "#424242"
            
            st.markdown(f"""
                <div class="news-card">
                    <span class="sentiment-tag" style="background-color: {bg}; color: {txt};">{tag}</span>
                    <span class="news-title">
                        <a href="{item['link']}" target="_blank">{item['title']}</a>
                    </span>
                    <div class="kst-time">⏰ {item['kst_dt'].strftime('%m-%d %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)

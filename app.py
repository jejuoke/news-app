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
    /* 전체 배경색 */
    .main { background-color: #f5f7f9; }
    
    /* 상단 여백 조절: 너무 붙지 않게 3rem으로 조정 */
    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 대제목 스타일: 잘리지 않도록 여백 확보 */
    .main-title { 
        font-size: 1.4rem !important; 
        font-weight: 800; 
        color: #1a1a1a; 
        margin-bottom: 1.2rem;
        letter-spacing: -0.05rem;
        line-height: 1.2;
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
        display: flex;
        flex-direction: column;
    }
    
    /* 뉴스 제목 스타일 */
    .news-title { 
        font-size: 0.95rem !important; 
        font-weight: 600; 
        line-height: 1.4;
        margin-bottom: 5px;
    }
    .news-title a { text-decoration: none; color: #1a1a1a; }
    
    .kst-time { color: #999; font-size: 0.7rem; margin-top: 2px; }
    .sentiment-tag { 
        font-size: 0.65rem; 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-weight: bold; 
        margin-bottom: 6px;
        width: fit-content;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# 대제목 출력
st.markdown('<div class="main-title">🚀 실시간 뉴스 분석</div>', unsafe_allow_html=True)

# 검색 영역 (레이아웃 최적화)
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
                    <div class="sentiment-tag" style="background-color: {bg}; color: {txt};">{tag}</div>
                    <div class="news-title">
                        <a href="{item['link']}" target="_blank">{item['title']}</a>
                    </div>
                    <div class="kst-time">⏰ {item['kst_dt'].strftime('%m-%d %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)

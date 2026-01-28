import streamlit as st
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
from dateutil import parser 
from datetime import datetime, timedelta
import urllib.parse

# 1. 페이지 설정 및 모바일 최적화 디자인
st.set_page_config(page_title="News Insights", layout="wide")

# CSS 수정: 글자 크기를 줄이고 한 줄 제한(ellipsis) 옵션 추가
st.markdown("""
    <style>
    /* 전체 배경색 */
    .main { background-color: #f5f7f9; }
    
    /* 검색창과 버튼 가로 정렬 및 크기 조절 */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0078D4; color: white; height: 3.2em; font-weight: bold; }
    
    /* 뉴스 카드 디자인 */
    .news-card { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05); 
        margin-bottom: 12px; 
        border: 1px solid #eee;
    }
    
    /* 제목 스타일: 모바일에 맞춰 크기 줄임 및 줄간격 조절 */
    .news-title { 
        font-size: 1rem !important; 
        font-weight: 600; 
        line-height: 1.3;
        margin-bottom: 8px;
        display: block;
    }
    .news-title a { text-decoration: none; color: #1a1a1a; }
    
    /* 시간 및 태그 스타일 */
    .kst-time { color: #888; font-size: 0.75rem; margin-top: 5px; }
    .sentiment-tag { 
        font-size: 0.7rem; 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-weight: bold; 
        margin-bottom: 8px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# 헤더
st.title("🚀 실시간 뉴스 분석")

# 검색창 영역 (모바일에서 한 줄로 보이도록 배치)
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
    
    st.markdown(f"##### 🔍 '{query}' 결과")
    
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
            
            # 카드 출력 (글자 크기 및 간격 최적화)
            st.markdown(f"""
                <div class="news-card">
                    <span class="sentiment-tag" style="background-color: {bg}; color: {txt};">{tag}</span>
                    <span class="news-title">
                        <a href="{item['link']}" target="_blank">{item['title']}</a>
                    </span>
                    <div class="kst-time">⏰ {item['kst_dt'].strftime('%m-%d %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)

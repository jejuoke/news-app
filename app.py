import streamlit as st
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
from dateutil import parser 
from datetime import datetime, timedelta
import urllib.parse

# 1. 페이지 설정 및 디자인 커스텀
st.set_page_config(page_title="News Insights", layout="wide")

# 모바일에서 더 예쁘게 보이도록 CSS 스타일 추가
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #0078D4; color: white; }
    .news-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .kst-time { color: #666; font-size: 0.85em; }
    .sentiment-tag { font-weight: bold; font-size: 0.9em; padding: 2px 8px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 분석기 로드
@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# 3. 헤더 섹션
st.title("🚀 실시간 뉴스 분석")
st.write("최신 동향을 한국 시간(KST)으로 가장 빠르게 분석합니다.")

# 4. [핵심] 검색창을 사이드바가 아닌 메인 화면 상단으로 배치
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("", value="원전", placeholder="키워드를 입력하세요 (예: 원전, 삼성전자)")
with col2:
    st.write(" ") # 간격 맞추기용
    search_btn = st.button("분석 실행")

# 5. 분석 로직
if search_btn or query: # 버튼을 누르거나 키워드만 입력해도 바로 작동
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    now_pc = datetime.now()
    
    st.markdown(f"#### 🔍 '{query}' 검색 결과")
    
    if not feed.entries:
        st.error("검색 결과가 없습니다.")
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
            
            # 호재/악재 색상 설정
            if score >= 0.05:
                tag, color = "📈 호재", "#e1f5fe" # 연파랑
                t_color = "#01579b"
            elif score <= -0.05:
                tag, color = "📉 악재", "#ffebee" # 연빨강
                t_color = "#c62828"
            else:
                tag, color = "😐 중립", "#f5f5f5"
                t_color = "#424242"
            
            # 디자인된 카드 출력
            st.markdown(f"""
                <div class="news-card">
                    <span style="background-color: {color}; color: {t_color}; padding: 3px 8px; border-radius: 5px; font-weight: bold;">{tag}</span>
                    <h3 style="margin-top: 10px; font-size: 1.1em;"><a href="{item['link']}" target="_blank" style="text-decoration: none; color: #1a1a1a;">{item['title']}</a></h3>
                    <p class="kst-time">⏰ {item['kst_dt'].strftime('%Y-%m-%d %H:%M')} (KST)</p>
                </div>
                """, unsafe_allow_html=True)

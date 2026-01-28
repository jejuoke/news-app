import streamlit as st
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
from dateutil import parser 
from datetime import datetime, timedelta
import urllib.parse

# 페이지 설정
st.set_page_config(page_title="실시간 뉴스 분석기", layout="wide")

st.title("📡 실시간 뉴스 감성 분석기 (KST)")
st.write("스마트폰에서도 확인 가능한 실시간 뉴스 분석 서비스입니다.")

# 분석기 로드 (캐싱하여 속도 향상)
@st.cache_resource
def load_tools():
    return SentimentIntensityAnalyzer(), GoogleTranslator(source='ko', target='en')

analyzer, translator = load_tools()

# 사이드바 검색창
query = st.sidebar.text_input("검색 키워드", value="원전")
search_btn = st.sidebar.button("최신순 분석 시작")

if search_btn:
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    now_pc = datetime.now()
    
    st.subheader(f"🔍 '{query}' 분석 결과")
    st.caption(f"기준 시각: {now_pc.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not feed.entries:
        st.error("검색 결과가 없습니다.")
    else:
        analyzed_list = []
        for e in feed.entries:
            # 9시간 강제 보정 로직 적용
            raw_dt = parser.parse(e.published).replace(tzinfo=None)
            kst_dt = raw_dt + timedelta(hours=9)
            
            analyzed_list.append({
                'title': e.title.split(' - ')[0],
                'link': e.link,
                'kst_dt': kst_dt
            })
        
        # 최신순 정렬
        sorted_list = sorted(analyzed_list, key=lambda x: x['kst_dt'], reverse=True)

        for item in sorted_list[:20]:
            # 감성 분석
            try:
                en_title = translator.translate(item['title'])
                score = analyzer.polarity_scores(en_title)['compound']
            except: score = 0
            
            sent = "📈 [호재]" if score >= 0.05 else "📉 [악재]" if score <= -0.05 else "😐 [중립]"
            
            # 웹 화면 출력 (카드 형태)
            with st.container():
                st.markdown(f"#### {sent} [{item['title']}]({item['link']})")
                st.write(f"⏰ 등록시간: {item['kst_dt'].strftime('%Y-%m-%d %H:%M')}")
                st.divider()
# app.py
import streamlit as st
import sqlite3
from datetime import datetime

# 데이터베이스 초기화 함수
def init_db():
    # orders.db 라는 파일로 SQLite 연결
    conn = sqlite3.connect('orders.db', check_same_thread=False)
    c = conn.cursor()
    # orders 테이블이 없으면 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER,
            order_text TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn, c

# DB 연결 및 커서 획득
conn, c = init_db()

# 사이드바에서 페이지 선택
page = st.sidebar.selectbox("페이지 선택", ["주문 페이지", "관리자 페이지"])  

if page == "주문 페이지":
    st.title("🎉 학교 축제 주문 페이지")
    # 테이블 번호 입력
    table_number = st.number_input("테이블 번호", min_value=1, step=1)
    # 주문 내용 입력
    order_text = st.text_area("주문 내용", height=150)
    # 주문 제출 버튼
    if st.button("주문 제출"):
        if order_text.strip() == "":
            st.warning("주문 내용을 입력해주세요.")
        else:
            # 현재 시각 기록
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # DB에 주문 추가
            c.execute(
                "INSERT INTO orders (table_number, order_text, timestamp) VALUES (?, ?, ?)",
                (table_number, order_text, timestamp)
            )
            conn.commit()
            st.success(f"주문이 정상적으로 접수되었습니다! (테이블 {table_number}, 시간 {timestamp})")

elif page == "관리자 페이지":
    st.title("🔍 관리자 페이지")
    st.write("주문 내역을 시간순으로 확인하세요.")
    # 시간순으로 정렬하여 주문 조회
    c.execute("SELECT table_number, order_text, timestamp FROM orders ORDER BY timestamp ASC")
    rows = c.fetchall()
    if rows:
        import pandas as pd
        # DataFrame으로 변환 후 테이블 형태로 표시
        df = pd.DataFrame(rows, columns=["테이블 번호", "주문 내용", "주문 시간"])
        st.table(df)
    else:
        st.info("아직 접수된 주문이 없습니다.")

# 실행 방법 안내
st.sidebar.markdown("---")
st.sidebar.info("앱 실행: `streamlit run streamlit_ordering_app.py`")

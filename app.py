import streamlit as st
import sqlite3
from datetime import datetime

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect('orders.db', check_same_thread=False)
    c = conn.cursor()

    # 기본 테이블 생성 (최초 실행 시)
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER,
            timestamp TEXT
        )
    ''')

    # 기존 테이블 컬럼 정보 조회
    c.execute("PRAGMA table_info(orders)")
    existing_cols = {row[1] for row in c.fetchall()}

    # 추가할 컬럼 정의
    migrations = {
        'cheese_cake':      'INTEGER DEFAULT 0',
        'beef_stir_fry':     'INTEGER DEFAULT 0',
        'canape':            'INTEGER DEFAULT 0',
        'fried_egg':         'INTEGER DEFAULT 0',
        'fried_chicken':     'INTEGER DEFAULT 0',
        'butter_shrimp':     'INTEGER DEFAULT 0',
        'order_Done':        'BOOLEAN DEFAULT FALSE'
    }

    # 누락된 컬럼만 추가
    for col, col_def in migrations.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_def}")

    conn.commit()
    return conn, c

# DB 연결결
conn, c = init_db()

# 사이드바 페이지 선택 및 필터 설정
page = st.sidebar.selectbox("페이지 선택", ["주문 페이지", "관리자 페이지"])
hide_done = st.sidebar.checkbox("완료된 주문 숨기기", value=True)

# 주문 페이지
if page == "주문 페이지":
    st.title("🎉 대동제 주문 페이지")
    table_number = st.number_input("테이블 번호", min_value=1, step=1)
    cheese_pancake  = st.slider("치즈 감자전", 0, 5, 0)
    beef_stir_fry   = st.slider("우삼겹 숙주 볶음", 0, 5, 0)
    canape          = st.slider("카나페", 0, 5, 0)
    fried_egg       = st.slider("후라이", 0, 5, 0)
    fried_chicken   = st.slider("가라아게", 0, 5, 0)
    butter_shrimp   = st.slider("버터 새우", 0, 5, 0)

    if st.button("주문 제출"):
        if not any([cheese_pancake, beef_stir_fry, canape, fried_egg, fried_chicken, butter_shrimp]):
            st.warning("주문할 메뉴를 선택해주세요.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                '''
                INSERT INTO orders
                (table_number, cheese_cake, beef_stir_fry, canape,
                 fried_egg, fried_chicken, butter_shrimp, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    table_number,
                    cheese_pancake,
                    beef_stir_fry,
                    canape,
                    fried_egg,
                    fried_chicken,
                    butter_shrimp,
                    timestamp
                )
            )
            conn.commit()
            st.success(f"주문이 정상적으로 접수되었습니다! (테이블 {table_number}, 시간 {timestamp})")

# 관리자 페이지
elif page == "관리자 페이지":
    st.title("🔍 관리자 페이지")
    st.write("주문 내역을 시간순으로 확인하고, 개별 메뉴 완료 체크 후, 모든 메뉴가 완료되면 테이블 전체를 완료 처리합니다.")

    # 주문 내역 초기화 버튼 (테이블 삭제 없이 데이터만 삭제)
    if st.sidebar.button("주문 내역 초기화"):  # 이전 '데이터베이스 초기화' 대신
        c.execute("DELETE FROM orders")
        conn.commit()
        st.sidebar.success("주문 내역이 초기화되었습니다.")

    # 주문 조회
    c.execute('''
        SELECT id, table_number, cheese_cake, beef_stir_fry, canape,
               fried_egg, fried_chicken, butter_shrimp, order_Done, timestamp
        FROM orders
        ORDER BY timestamp ASC
    ''')
    rows = c.fetchall()

    if not rows:
        st.info("아직 접수된 주문이 없습니다.")
    else:
        for row in rows:
            order_id, table_no, chz, beef, canp, egg, chick, shrp, done, ts = row

            # 완료된 주문 숨기기 옵션
            if hide_done and done:
                continue

            header = f"테이블 {table_no} @ {ts}"
            if done:
                # 완료된 주문은 녹색 배경 메시지로 표시
                with st.expander(header, expanded=False,icon="✅"):
                    st.success("✅ 이 테이블 주문이 완료되었습니다.")
            else:
                with st.expander(header, expanded=False,icon="❌"):
                    # 메뉴별 개별 체크박스 생성
                    menu_items = [
                        ("치즈 감자전", chz, "cheese_cake"),
                        ("우삼겹 숙주 볶음", beef, "beef_stir_fry"),
                        ("카나페", canp, "canape"),
                        ("후라이", egg, "fried_egg"),
                        ("가라아게", chick, "fried_chicken"),
                        ("버터 새우", shrp, "butter_shrimp"),
                    ]
                    checks = []
                    for name, qty, col in menu_items:
                        if qty > 0:
                            st.write(f"- {name}: {qty}개")
                            for i in range(qty):
                                checked = st.checkbox(
                                    f"{name} #{i+1}",
                                    value=False,
                                    key=f"{order_id}_{col}_{i}"
                                )
                                checks.append(checked)

                    # 모든 개별 메뉴가 체크되었을 때 테이블 완료 처리
                    if checks and all(checks):
                        c.execute(
                            "UPDATE orders SET order_Done = 1 WHERE id = ?",
                            (order_id,)
                        )
                        conn.commit()
                        st.success(f"🎉 테이블 {table_no}의 모든 메뉴가 완료 처리되었습니다.")

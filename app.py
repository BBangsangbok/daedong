import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect('orders.db', check_same_thread=False)
    c = conn.cursor()

    # 기본 테이블 생성 (id, table_number, timestamp)
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER,
            timestamp TEXT
        )
    ''')

    # 기존 컬럼 정보 조회
    c.execute("PRAGMA table_info(orders)")
    existing_cols = {row[1] for row in c.fetchall()}

    # 추가할 컬럼 정의
    migrations = {
        'customer_name':    "TEXT DEFAULT ''",
        'cheese_cake':      'INTEGER DEFAULT 0',
        'beef_stir_fry':    'INTEGER DEFAULT 0',
        'beef_with_mara':   'INTEGER DEFAULT 0',
        'canape':           'INTEGER DEFAULT 0',
        'fried_egg':        'INTEGER DEFAULT 0',
        'fried_chickenN':   'INTEGER DEFAULT 0',
        'fried_chickenU':   'INTEGER DEFAULT 0',
        'butter_shrimp':    'INTEGER DEFAULT 0',
        'Hot_dog':          'INTEGER DEFAULT 0',
        'ice_mango':        'INTEGER DEFAULT 0',
        'blue_lagoon':      'INTEGER DEFAULT 0',
        'screwdriver':      'INTEGER DEFAULT 0',
        'midori':           'INTEGER DEFAULT 0',
        'sea_breeze':       'INTEGER DEFAULT 0',
        'tropical':         'INTEGER DEFAULT 0',
        'blue_lagoon_na':   'INTEGER DEFAULT 0',
        'screwdriver_na':   'INTEGER DEFAULT 0',
        'midori_na':        'INTEGER DEFAULT 0',
        'sea_breeze_na':    'INTEGER DEFAULT 0',
        'tropical_na':      'INTEGER DEFAULT 0',
        'order_Done':       'BOOLEAN DEFAULT FALSE'
    }
    for col, col_def in migrations.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE orders ADD COLUMN {col} {col_def}")

    conn.commit()
    return conn, c

# DB 연결
conn, c = init_db()

# 가격 설정 (메뉴별 단가)
PRICE_MAP = {
    "치즈 감자전": 16000,
    "우삼겹 숙주 볶음": 16000,
    "우삼겹 숙주 볶음 (마라)": 16000,  # 추가된 메뉴
    "카나페": 7000,
    "후라이": 10000,
    "치킨 난반": 17000,
    "유린기": 17000,
    "버터 새우": 17000,
    "핫도그": 4000,
    "아망추": 4000,
    "블루 라군": 6500,
    "스크루 드라이버": 6500,
    "미도리 사워": 6500,
    "시 브리즈": 6500,
    "트로피컬 선라이즈": 6500,
    "블루 라군 (논알콜)": 6500,
    "스크루 드라이버 (논알콜)": 6500,
    "미도리 사워 (논알콜)": 6500,
    "시 브리즈 (논알콜)": 6500,
    "트로피컬 선라이즈 (논알콜)": 6500
}

# 사이드바 페이지 선택 및 필터 설정
page = st.sidebar.selectbox(
    "페이지 선택", ["주문 페이지", "관리자 페이지", "통계 페이지"]
)
hide_done = st.sidebar.checkbox("완료된 주문 숨기기", value=True)

# 주문 페이지
if page == "주문 페이지":
    st.title("🎉 대동제 주문 페이지")
    table_number = st.number_input("테이블 번호", min_value=1, step=1)
    customer_name = st.text_input("주문자 이름")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🍽️ 음식")
        cheese_cake    = st.number_input("치즈 감자전", min_value=0, max_value=5, value=0)
        beef_stir_fry  = st.number_input("우삼겹 숙주 볶음", min_value=0, max_value=5, value=0)
        beef_with_mara = st.number_input("우삼겹 숙주 볶음 (마라)", min_value=0, max_value=5, value=0)
        canape         = st.number_input("카나페", min_value=0, max_value=5, value=0)
        fried_egg      = st.number_input("후라이", min_value=0, max_value=5, value=0)
        fried_chickenN = st.number_input("치킨 난반", min_value=0, max_value=5, value=0)
        fried_chickenU = st.number_input("유린기", min_value=0, max_value=5, value=0)
        butter_shrimp  = st.number_input("버터 새우", min_value=0, max_value=5, value=0)
        hot_dog        = st.number_input("핫도그", min_value=0, max_value=5, value=0)
        ice_mango      = st.number_input("아망추", min_value=0, max_value=5, value=0)
    with col2:
        st.subheader("🍹 칵테일")
        blue_lagoon   = st.number_input("블루 라군", min_value=0, max_value=5, value=0)
        screwdriver   = st.number_input("스크루 드라이버", min_value=0, max_value=5, value=0)
        midori        = st.number_input("미도리 사워", min_value=0, max_value=5, value=0)
        sea_breeze    = st.number_input("시 브리즈", min_value=0, max_value=5, value=0)
        tropical      = st.number_input("트로피컬 선라이즈", min_value=0, max_value=5, value=0)
        st.markdown("---")
        st.subheader("🍸 논알콜 버전")
        blue_lagoon_na  = st.number_input("블루 라군 (논알콜)", min_value=0, max_value=5, value=0)
        screwdriver_na  = st.number_input("스크루 드라이버 (논알콜)", min_value=0, max_value=5, value=0)
        midori_na       = st.number_input("미도리 사워 (논알콜)", min_value=0, max_value=5, value=0)
        sea_breeze_na   = st.number_input("시 브리즈 (논알콜)", min_value=0, max_value=5, value=0)
        tropical_na     = st.number_input("트로피컬 선라이즈 (논알콜)", min_value=0, max_value=5, value=0)

    if st.button("주문 제출"):
        if not customer_name:
            st.warning("주문자 이름을 입력해주세요.")
        elif not any([
            cheese_cake, beef_stir_fry, beef_with_mara, canape, fried_egg, fried_chickenN,
            fried_chickenU, butter_shrimp, hot_dog, ice_mango, blue_lagoon, screwdriver, midori, sea_breeze,
            tropical, blue_lagoon_na, screwdriver_na, midori_na,
            sea_breeze_na, tropical_na
        ]):
            st.warning("주문할 메뉴를 선택해주세요.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                '''INSERT INTO orders
                (table_number, customer_name,
                    cheese_cake, beef_stir_fry, beef_with_mara, canape, fried_egg,
                    fried_chickenN, fried_chickenU, butter_shrimp, hot_dog, ice_mango,
                    blue_lagoon, screwdriver, midori, sea_breeze,
                    tropical, blue_lagoon_na, screwdriver_na,
                    midori_na, sea_breeze_na, tropical_na, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    table_number, customer_name,
                    cheese_cake, beef_stir_fry, beef_with_mara, canape, fried_egg,
                    fried_chickenN, fried_chickenU, butter_shrimp, hot_dog, ice_mango,
                    blue_lagoon, screwdriver, midori, sea_breeze,
                    tropical, blue_lagoon_na, screwdriver_na,
                    midori_na, sea_breeze_na, tropical_na,
                    timestamp
                )
            )
            conn.commit()
            st.success(f"주문이 정상적으로 접수되었습니다! (테이블 {table_number}, 주문자 {customer_name})")

# 관리자 페이지
elif page == "관리자 페이지":
    st.title("🔍 관리자 페이지")
    st.write(
        "주문 내역을 확인하고, 메뉴별 완료 체크 후, 모든 주문을 완료 처리하거나 개별적으로 취소할 수 있습니다."
    )
    if st.button("새로고침"):
        st.write()
    if st.sidebar.button("주문 내역 초기화"):
        c.execute("DELETE FROM orders")
        conn.commit()
        st.sidebar.success("주문 내역이 초기화되었습니다.")

    c.execute(
        '''SELECT id, table_number, customer_name,
                   cheese_cake, beef_stir_fry, beef_with_mara, canape, fried_egg,
                   fried_chickenN, fried_chickenU, butter_shrimp, hot_dog, ice_mango,
                   blue_lagoon, screwdriver, midori, sea_breeze, tropical,
                   blue_lagoon_na, screwdriver_na, midori_na,
                   sea_breeze_na, tropical_na, order_Done, timestamp
           FROM orders
           ORDER BY timestamp ASC
        '''
    )
    rows = c.fetchall()
    if not rows:
        st.info("아직 접수된 주문이 없습니다.")
    else:
        for row in rows:
            (
                order_id, table_no, cust,
                chz, beef, beef_mara, canp, egg,
                chickN, chickU, shrp, hot_dog, ice_mango, blue, screw,
                mid, sea, trop, blue_na,
                screw_na, mid_na, sea_na,
                trop_na, done, ts
            ) = row
            if hide_done and done:
                continue
            header = f"테이블 {table_no} / {cust} @ {ts}"
            with st.expander(header, expanded=False, icon="❌" if not done else "✅"):
                st.write(f"**주문자**: {cust}")
                menu_items = [
                    ("치즈 감자전", chz), ("우삼겹 숙주 볶음", beef),
                    ("우삼겹 숙주 볶음 (마라)", beef_mara),
                    ("카나페", canp), ("후라이", egg),
                    ("치킨 난반", chickN), ("유린기", chickU), ("버터 새우", shrp),
                    ("핫도그", hot_dog), ("아망추", ice_mango),
                    ("블루 라군", blue), ("스크루 드라이버", screw),
                    ("미도리 사워", mid), ("시 브리즈", sea),
                    ("트로피컬 선라이즈", trop),
                    ("블루 라군 (논알콜)", blue_na),
                    ("스크루 드라이버 (논알콜)", screw_na),
                    ("미도리 사워 (논알콜)", mid_na),
                    ("시 브리즈 (논알콜)", sea_na),
                    ("트로피컬 선라이즈 (논알콜)", trop_na)
                ]
                # 주문 내역 출력
                for name, qty in menu_items:
                    if qty > 0:
                        st.write(f"- {name}: {qty}개")
                # 완료/취소 버튼
                col_cancel, col_done = st.columns(2)
                with col_cancel:
                    if st.button("주문 취소", key=f"cancel_{order_id}"):
                        c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
                        conn.commit()
                        st.warning(f"테이블 {table_no}의 주문이 취소되었습니다.")
                        st.write()
                with col_done:
                    if not done:
                        checks = []
                        for name, qty in menu_items:
                            for i in range(qty):
                                checked = st.checkbox(
                                    f"{name} #{i+1}", key=f"{order_id}_{name}_{i}")
                                checks.append(checked)
                        if checks and all(checks):
                            c.execute(
                                "UPDATE orders SET order_Done = 1 WHERE id = ?",
                                (order_id,)
                            )
                            conn.commit()
                            st.success(f"🎉 테이블 {table_no}의 주문이 완료 처리되었습니다.")
                            st.write()
                    else:
                        st.success("✅ 주문이 완료된 상태입니다.")

# 통계 페이지
elif page == "통계 페이지":
    st.title("📊 매출 및 주문량 통계")

    # 각 메뉴별 주문량 합계 조회
    c.execute(
        '''SELECT
            SUM(cheese_cake), SUM(beef_stir_fry),SUM(beef_with_mara), SUM(canape),
            SUM(fried_egg), SUM(fried_chickenN), SUM(fried_chickenU), SUM(butter_shrimp),
            SUM(hot_dog), SUM(ice_mango), SUM(blue_lagoon), SUM(screwdriver), SUM(midori),
            SUM(sea_breeze), SUM(tropical), SUM(blue_lagoon_na),
            SUM(screwdriver_na), SUM(midori_na), SUM(sea_breeze_na),
            SUM(tropical_na)
        FROM orders'''
    )
    sums = c.fetchone()

    columns = [
        "치즈 감자전", "우삼겹 숙주 볶음", "우삼겹 숙주 볶음 (마라)", "카나페", "후라이", "치킨 난반", "유린기", "버터 새우",
        "핫도그", "아망추", "블루 라군", "스크루 드라이버", "미도리 사워", "시 브리즈", "트로피컬 선라이즈",
        "블루 라군 (논알콜)", "스크루 드라이버 (논알콜)", "미도리 사워 (논알콜)",
        "시 브리즈 (논알콜)", "트로피컬 선라이즈 (논알콜)"
    ]
    df = pd.DataFrame({
        '메뉴': columns,
        '총 주문량': sums
    })
    # 단가 컬럼 추가
    df['단가 (원)'] = df['메뉴'].map(PRICE_MAP).astype(int)
    df['매출 (원)'] = df['총 주문량'] * df['단가 (원)']
    total_revenue = df['매출 (원)'].sum()

    st.metric("총 매출", f"{total_revenue:,}원")
    st.table(df.set_index('메뉴'))

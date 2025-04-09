from backend.db import get_connection, release_connection

def init_database():
    """데이터베이스 테이블 초기화"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 기존 테이블 삭제 (CASCADE로 외래 키 제약조건도 함께 삭제)
                cur.execute("""
                    DROP TABLE IF EXISTS chat_messages CASCADE;
                    DROP TABLE IF EXISTS chat_sessions CASCADE;
                    DROP TABLE IF EXISTS users CASCADE;
                """)

                # users 테이블 생성
                cur.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul')
                    );
                """)

                # chat_sessions 테이블 생성
                cur.execute("""
                    CREATE TABLE chat_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul'),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                """)

                # chat_messages 테이블 생성
                cur.execute("""
                    CREATE TABLE chat_messages (
                        id SERIAL PRIMARY KEY,
                        session_id INT NOT NULL,
                        sender VARCHAR(50) NOT NULL CHECK (sender IN ('user', 'bot')),
                        message TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul'),
                        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                    );
                """)

                conn.commit()
                print("Database tables initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
        finally:
            release_connection(conn)

def convert_password_to_binary():
    """비밀번호 컬럼을 TEXT에서 BYTEA로 변환"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 비밀번호 컬럼 변환
                cur.execute("""
                    ALTER TABLE users ADD COLUMN password_new BYTEA;
                    UPDATE users SET password_new = decode(password, 'escape');
                    ALTER TABLE users DROP COLUMN password;
                    ALTER TABLE users RENAME COLUMN password_new TO password;
                """)
                conn.commit()
                print("Password column converted to binary successfully.")
        except Exception as e:
            print(f"Error converting password column: {e}")
            conn.rollback()
        finally:
            release_connection(conn)

if __name__ == "__main__":
    init_database()
import psycopg2
import bcrypt
import streamlit as st
from backend.db import get_connection, release_connection  # Connection Pool 활용

# 비밀번호 해싱
def hash_password(password: str) -> str:
    """비밀번호를 해싱하여 저장"""
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()  # 해싱 후 문자열로 변환

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증 (해싱된 비밀번호와 비교)"""
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        raise ValueError("Both plain_password and hashed_password must be strings")
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode('utf-8'))  # 수정된 부분

# 사용자 등록
def register_user(username: str, password: str) -> bool:
    """새 사용자를 데이터베이스에 추가"""
    if not isinstance(username, str) or not isinstance(password, str):
        raise ValueError("Username and password must be strings")
    
    hashed_password = hash_password(password)
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 먼저 해당 사용자명이 있는지 확인 (is_active = TRUE인 경우만)
                cur.execute(
                    "SELECT id FROM users WHERE username = %s AND is_active = TRUE",
                    (username,),
                )
                existing_user = cur.fetchone()

                if existing_user:
                    return False  # 활성화된 사용자가 이미 존재함

                # is_active = FALSE인 사용자가 있다면 업데이트
                cur.execute(
                    "SELECT id FROM users WHERE username = %s AND is_active = FALSE",
                    (username,),
                )
                inactive_user = cur.fetchone()

                if inactive_user:
                    # 기존 사용자 정보 업데이트
                    cur.execute(
                        "UPDATE users SET password = %s, is_active = TRUE WHERE username = %s",
                        (hashed_password, username),
                    )
                else:
                    # 새 사용자 추가
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
                        (username, hashed_password),
                    )
                
                conn.commit()
                return True  # 회원가입 성공
        except Exception as e:
            print(f"Error during registration: {e}")
            return False
        finally:
            release_connection(conn)

# 사용자 인증 (로그인)
def authenticate(username: str, password: str) -> bool:
    """사용자의 비밀번호를 검증하여 로그인 처리"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password FROM users WHERE username = %s AND is_active = TRUE",
                    (username,),
                )
                user_data = cur.fetchone()

            if user_data:
                stored_password = user_data[0]  # 데이터베이스에서 가져온 해싱된 비밀번호
                return verify_password(password, stored_password)  # 수정된 부분
            return False
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False
        finally:
            release_connection(conn)

# 로그인 처리 (세션 업데이트)
def login_user(username: str):
    """로그인 시 세션에 사용자 정보 저장"""
    st.session_state["authenticated"] = True
    st.session_state["user"] = username
    st.success(f"{username}님, 로그인되었습니다.")

# 로그아웃 처리
def logout():
    """로그아웃 시 세션 초기화"""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.info("📢 로그아웃 되었습니다.")

# 회원 탈퇴 (is_active = False 로 변경)
def delete_user(username: str) -> bool:
    """회원 탈퇴 시 실제 데이터를 삭제하는 대신 is_active = False로 변경"""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_active = FALSE WHERE username = %s",
                    (username,),
                )
                conn.commit()
                return True  # 탈퇴 성공
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            release_connection(conn)

# 로그인 상태 확인
def is_authenticated() -> bool:
    """세션을 통해 현재 로그인 상태 확인"""
    return st.session_state.get("authenticated", False)
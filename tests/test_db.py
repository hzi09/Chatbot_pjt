import pytest
from unittest.mock import patch, MagicMock
from backend.db import (
    get_connection,
    release_connection,
    create_chat_session,
    insert_chat_message,
    get_chat_history,
    get_user_chat_sessions,
    get_all_chat_sessions,
    delete_chat_messages,
    delete_chat_session,
    delete_all_user_sessions,
    get_user_id
)

class TestDB:
    @pytest.fixture
    def mock_connection(self):
        """데이터베이스 연결 모의 객체"""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.__enter__.return_value = mock_cur
        mock_cur.__exit__.return_value = None
        mock_conn.cursor.return_value = mock_cur
        return mock_conn, mock_cur

    @pytest.fixture
    def mock_connection_pool(self):
        """연결 풀 모의 객체"""
        with patch('backend.db.connection_pool') as mock_pool:
            yield mock_pool

    def test_get_connection(self, mock_connection_pool, mock_connection):
        """데이터베이스 연결 가져오기 테스트"""
        mock_conn, _ = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        
        conn = get_connection()
        assert conn == mock_conn
        mock_connection_pool.getconn.assert_called_once()

    def test_release_connection(self, mock_connection_pool, mock_connection):
        """데이터베이스 연결 반환 테스트"""
        mock_conn, _ = mock_connection
        release_connection(mock_conn)
        mock_connection_pool.putconn.assert_called_once_with(mock_conn)

    def test_create_chat_session(self, mock_connection_pool, mock_connection):
        """채팅 세션 생성 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchone.return_value = (1,)  # 세션 ID
        
        session_id = create_chat_session(1)
        assert session_id == 1
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_insert_chat_message(self, mock_connection_pool, mock_connection):
        """채팅 메시지 삽입 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        
        insert_chat_message(1, "user", "안녕하세요")
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_get_chat_history(self, mock_connection_pool, mock_connection):
        """채팅 기록 조회 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchall.return_value = [
            {"sender": "user", "message": "안녕하세요", "timestamp": "2024-01-01 12:00:00"},
            {"sender": "bot", "message": "안녕하세요!", "timestamp": "2024-01-01 12:00:01"}
        ]
        
        history = get_chat_history(1)
        assert len(history) == 2
        assert history[0]["sender"] == "user"
        assert history[1]["sender"] == "bot"
        mock_cur.execute.assert_called_once()

    def test_get_user_chat_sessions(self, mock_connection_pool, mock_connection):
        """사용자 채팅 세션 조회 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchall.return_value = [
            {"id": 1, "created_at": "2024-01-01 12:00:00"},
            {"id": 2, "created_at": "2024-01-01 11:00:00"}
        ]
        
        sessions = get_user_chat_sessions(1)
        assert len(sessions) == 2
        assert sessions[0]["id"] == 1
        mock_cur.execute.assert_called_once()

    def test_get_all_chat_sessions(self, mock_connection_pool, mock_connection):
        """전체 채팅 세션 조회 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchall.return_value = [
            {"id": 1, "username": "user1", "created_at": "2024-01-01 12:00:00"},
            {"id": 2, "username": "user2", "created_at": "2024-01-01 11:00:00"}
        ]
        
        sessions = get_all_chat_sessions()
        assert len(sessions) == 2
        assert sessions[0]["username"] == "user1"
        mock_cur.execute.assert_called_once()

    def test_delete_chat_messages(self, mock_connection_pool, mock_connection):
        """채팅 메시지 삭제 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        
        delete_chat_messages(1)
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_delete_chat_session(self, mock_connection_pool, mock_connection):
        """채팅 세션 삭제 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        
        delete_chat_session(1)
        assert mock_cur.execute.call_count == 2  # 메시지 삭제 + 세션 삭제
        mock_conn.commit.assert_called_once()

    def test_delete_all_user_sessions(self, mock_connection_pool, mock_connection):
        """사용자 모든 세션 삭제 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchall.return_value = [(1,), (2,)]  # 세션 ID 목록
        
        delete_all_user_sessions(1)
        # 세션 ID 조회 (1번) + 각 세션의 메시지 삭제 (2번) + 세션 삭제 (1번) = 총 4번
        assert mock_cur.execute.call_count == 4
        mock_conn.commit.assert_called_once()

    def test_get_user_id(self, mock_connection_pool, mock_connection):
        """사용자 ID 조회 테스트"""
        mock_conn, mock_cur = mock_connection
        mock_connection_pool.getconn.return_value = mock_conn
        mock_cur.fetchone.return_value = (1,)  # 사용자 ID
        
        user_id = get_user_id("test_user")
        assert user_id == 1
        mock_cur.execute.assert_called_once()
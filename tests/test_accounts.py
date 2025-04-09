import pytest
import bcrypt
from backend.accounts import (
    hash_password,
    verify_password,
    register_user,
    authenticate,
    login_user,
    logout,
    delete_user,
    is_authenticated
)
from backend.init_db import init_database

class TestAccounts:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """각 테스트 전에 데이터베이스 초기화"""
        init_database()

    @pytest.fixture
    def test_credentials(self):
        return {
            "username": "test_user",
            "password": "test_password123",
            "wrong_password": "wrong_password"
        }

    def test_hash_password(self, test_credentials):
        """비밀번호 해싱 테스트"""
        hashed = hash_password(test_credentials["password"])
        assert isinstance(hashed, str)
        assert bcrypt.checkpw(test_credentials["password"].encode(), hashed.encode())

    def test_verify_password(self, test_credentials):
        """비밀번호 검증 테스트"""
        hashed = hash_password(test_credentials["password"])
        assert verify_password(test_credentials["password"], hashed)
        assert not verify_password(test_credentials["wrong_password"], hashed)

    def test_register_user(self, test_credentials):
        """사용자 등록 테스트"""
        # 정상적인 회원가입
        result = register_user(test_credentials["username"], test_credentials["password"])
        assert result is True

        # 중복 아이디로 회원가입 시도
        result = register_user(test_credentials["username"], test_credentials["password"])
        assert result is False

    def test_authenticate(self, test_credentials):
        """사용자 인증 테스트"""
        # 먼저 사용자 등록
        register_user(test_credentials["username"], test_credentials["password"])
        
        # 정상적인 로그인
        result = authenticate(test_credentials["username"], test_credentials["password"])
        assert result is True

        # 잘못된 비밀번호로 로그인 시도
        result = authenticate(test_credentials["username"], test_credentials["wrong_password"])
        assert result is False

        # 존재하지 않는 사용자로 로그인 시도
        result = authenticate("nonexistent_user", test_credentials["password"])
        assert result is False

    def test_delete_user(self, test_credentials):
        """회원 탈퇴 테스트 (is_active = FALSE로 변경)"""
        # 먼저 사용자 등록
        register_user(test_credentials["username"], test_credentials["password"])
        
        # 정상적인 탈퇴
        result = delete_user(test_credentials["username"])
        assert result is True

        # 탈퇴 후 로그인 시도 (is_active = FALSE이므로 실패해야 함)
        result = authenticate(test_credentials["username"], test_credentials["password"])
        assert result is False

        # 동일한 사용자명으로 다시 회원가입 시도 (성공해야 함)
        result = register_user(test_credentials["username"], test_credentials["password"])
        assert result is True 
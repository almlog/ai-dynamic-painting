"""
API例外クラスとエラーコード定義

Phase 6 VEO API統合における包括的エラーハンドリング
"""

from fastapi import HTTPException, status
from typing import Dict, Any, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """API エラーコード定義"""
    
    # 一般的なエラー (1xxx)
    INVALID_REQUEST = "E1001"
    VALIDATION_ERROR = "E1002"
    MISSING_PARAMETER = "E1003"
    INVALID_PARAMETER_VALUE = "E1004"
    
    # 認証・認可エラー (2xxx)
    AUTHENTICATION_REQUIRED = "E2001"
    INVALID_API_KEY = "E2002"
    INSUFFICIENT_PERMISSIONS = "E2003"
    TOKEN_EXPIRED = "E2004"
    
    # VEO API関連エラー (3xxx)
    VEO_SERVICE_UNAVAILABLE = "E3001"
    VEO_QUOTA_EXCEEDED = "E3002"
    VEO_GENERATION_FAILED = "E3003"
    VEO_TIMEOUT = "E3004"
    VEO_INVALID_PROMPT = "E3005"
    VEO_UNSUPPORTED_PARAMETERS = "E3006"
    
    # コスト・予算関連エラー (4xxx)
    BUDGET_EXCEEDED = "E4001"
    INSUFFICIENT_CREDITS = "E4002"
    COST_CALCULATION_ERROR = "E4003"
    PAYMENT_REQUIRED = "E4004"
    
    # システムエラー (5xxx)
    INTERNAL_SERVER_ERROR = "E5001"
    DATABASE_ERROR = "E5002"
    SERVICE_INITIALIZATION_ERROR = "E5003"
    CONFIGURATION_ERROR = "E5004"
    
    # レート制限エラー (6xxx)
    RATE_LIMIT_EXCEEDED = "E6001"
    CONCURRENT_REQUEST_LIMIT = "E6002"
    DAILY_QUOTA_EXCEEDED = "E6003"
    
    # タスク管理エラー (7xxx)
    TASK_NOT_FOUND = "E7001"
    TASK_ALREADY_COMPLETED = "E7002"
    TASK_CANCELLED = "E7003"
    TASK_FAILED = "E7004"


class APIException(HTTPException):
    """
    カスタムAPI例外基底クラス
    
    構造化されたエラーレスポンスを提供し、
    フロントエンドでの適切なエラーハンドリングを支援
    """
    
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggested_action: Optional[str] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggested_action = suggested_action
        
        # FastAPI HTTPException形式のレスポンス構築
        error_response = {
            "error": {
                "code": error_code.value,
                "message": message,
                "type": self.__class__.__name__,
                "details": self.details
            }
        }
        
        if suggested_action:
            error_response["error"]["suggested_action"] = suggested_action
            
        super().__init__(status_code=status_code, detail=error_response)


class ValidationException(APIException):
    """バリデーションエラー (400)"""
    
    def __init__(
        self, 
        message: str = "リクエストパラメータが無効です",
        field_errors: Optional[Dict[str, str]] = None
    ):
        details = {"field_errors": field_errors} if field_errors else {}
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            suggested_action="パラメータの値と形式を確認してください"
        )


class AuthenticationException(APIException):
    """認証エラー (401)"""
    
    def __init__(self, message: str = "認証が必要です"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.AUTHENTICATION_REQUIRED,
            message=message,
            suggested_action="有効なAPIキーを提供してください"
        )


class PermissionException(APIException):
    """認可エラー (403)"""
    
    def __init__(self, message: str = "この操作を実行する権限がありません"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
            suggested_action="アカウント管理者に権限の確認をしてください"
        )


class ResourceNotFoundException(APIException):
    """リソース未発見エラー (404)"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.TASK_NOT_FOUND,
            message=f"{resource_type} (ID: {resource_id}) が見つかりません",
            details={"resource_type": resource_type, "resource_id": resource_id},
            suggested_action="リソースIDを確認するか、リソースが存在するか確認してください"
        )


class RateLimitException(APIException):
    """レート制限エラー (429)"""
    
    def __init__(
        self, 
        limit_type: str = "request",
        retry_after: Optional[int] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None
    ):
        details = {"limit_type": limit_type}
        if current_usage is not None and limit is not None:
            details.update({"current_usage": current_usage, "limit": limit})
            
        message = f"{limit_type}の制限に達しました"
        if retry_after:
            message += f"。{retry_after}秒後に再試行してください"
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            details=details,
            suggested_action=f"{retry_after or 60}秒待ってから再試行してください"
        )
        
        # レート制限特有のヘッダー情報
        if retry_after:
            self.headers = {"Retry-After": str(retry_after)}


class BudgetExceededException(APIException):
    """予算制限エラー (507)"""
    
    def __init__(
        self, 
        current_usage: float,
        budget_limit: float,
        estimated_cost: Optional[float] = None
    ):
        details = {
            "current_usage": current_usage,
            "budget_limit": budget_limit,
            "remaining_budget": max(0, budget_limit - current_usage)
        }
        if estimated_cost:
            details["estimated_cost"] = estimated_cost
            
        super().__init__(
            status_code=507,  # Insufficient Storage (予算不足の代用)
            error_code=ErrorCode.BUDGET_EXCEEDED,
            message=f"月間予算制限に達しました (使用量: ${current_usage:.2f} / 制限: ${budget_limit:.2f})",
            details=details,
            suggested_action="予算制限を引き上げるか、翌月まで待機してください"
        )


class VEOServiceException(APIException):
    """VEO API関連エラー (502)"""
    
    def __init__(
        self, 
        message: str = "VEO APIサービスでエラーが発生しました",
        veo_error_code: Optional[str] = None,
        veo_message: Optional[str] = None
    ):
        details = {}
        if veo_error_code:
            details["veo_error_code"] = veo_error_code
        if veo_message:
            details["veo_message"] = veo_message
            
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=ErrorCode.VEO_GENERATION_FAILED,
            message=message,
            details=details,
            suggested_action="しばらく待ってから再試行するか、サポートにお問い合わせください"
        )


class ServiceUnavailableException(APIException):
    """サービス利用不可エラー (503)"""
    
    def __init__(self, service_name: str = "AI生成サービス"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.SERVICE_INITIALIZATION_ERROR,
            message=f"{service_name}が初期化されていません",
            suggested_action="サービスの初期化完了まで少々お待ちください"
        )


# エラーコード説明マッピング
ERROR_CODE_DESCRIPTIONS = {
    ErrorCode.INVALID_REQUEST: "リクエスト形式が正しくありません",
    ErrorCode.VALIDATION_ERROR: "パラメータのバリデーションに失敗しました",
    ErrorCode.MISSING_PARAMETER: "必須パラメータが不足しています",
    ErrorCode.INVALID_PARAMETER_VALUE: "パラメータの値が無効です",
    
    ErrorCode.AUTHENTICATION_REQUIRED: "認証が必要です",
    ErrorCode.INVALID_API_KEY: "APIキーが無効です",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "権限が不足しています",
    ErrorCode.TOKEN_EXPIRED: "認証トークンが期限切れです",
    
    ErrorCode.VEO_SERVICE_UNAVAILABLE: "VEO APIサービスが利用できません",
    ErrorCode.VEO_QUOTA_EXCEEDED: "VEO APIの利用制限に達しました",
    ErrorCode.VEO_GENERATION_FAILED: "動画生成に失敗しました",
    ErrorCode.VEO_TIMEOUT: "動画生成がタイムアウトしました",
    ErrorCode.VEO_INVALID_PROMPT: "プロンプトが無効です",
    ErrorCode.VEO_UNSUPPORTED_PARAMETERS: "サポートされていないパラメータです",
    
    ErrorCode.BUDGET_EXCEEDED: "予算制限に達しました",
    ErrorCode.INSUFFICIENT_CREDITS: "クレジットが不足しています",
    ErrorCode.COST_CALCULATION_ERROR: "コスト計算でエラーが発生しました",
    ErrorCode.PAYMENT_REQUIRED: "支払いが必要です",
    
    ErrorCode.INTERNAL_SERVER_ERROR: "内部サーバーエラーが発生しました",
    ErrorCode.DATABASE_ERROR: "データベースエラーが発生しました",
    ErrorCode.SERVICE_INITIALIZATION_ERROR: "サービスの初期化に失敗しました",
    ErrorCode.CONFIGURATION_ERROR: "設定エラーが発生しました",
    
    ErrorCode.RATE_LIMIT_EXCEEDED: "リクエスト制限に達しました",
    ErrorCode.CONCURRENT_REQUEST_LIMIT: "同時リクエスト制限に達しました",
    ErrorCode.DAILY_QUOTA_EXCEEDED: "日次制限に達しました",
    
    ErrorCode.TASK_NOT_FOUND: "タスクが見つかりません",
    ErrorCode.TASK_ALREADY_COMPLETED: "タスクは既に完了しています",
    ErrorCode.TASK_CANCELLED: "タスクがキャンセルされました",
    ErrorCode.TASK_FAILED: "タスクの実行に失敗しました",
}


def get_error_description(error_code: ErrorCode) -> str:
    """エラーコードの説明を取得"""
    return ERROR_CODE_DESCRIPTIONS.get(error_code, "不明なエラーです")
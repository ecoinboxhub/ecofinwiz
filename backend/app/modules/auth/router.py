from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.schemas import (
    AuthUserResponse,
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthUserResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, access, refresh = await service.register(
        email=body.email, password=body.password, full_name=body.full_name
    )
    return AuthUserResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(access_token=access, refresh_token=refresh),
    )


@router.post("/login", response_model=AuthUserResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, access, refresh = await service.login(email=body.email, password=body.password)
    return AuthUserResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(access_token=access, refresh_token=refresh),
    )


@router.post("/google", response_model=AuthUserResponse)
async def google_auth(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, access, refresh = await service.google_auth(id_token=body.id_token)
    return AuthUserResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(access_token=access, refresh_token=refresh),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    access, refresh = await service.refresh(refresh_token_str=body.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=204)
async def logout(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(refresh_token_str=body.refresh_token)


@router.post("/forgot-password", status_code=200)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.forgot_password(email=body.email)


@router.post("/reset-password", status_code=200)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(token=body.token, new_password=body.new_password)


@router.post("/verify-email", status_code=200)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(token=body.token)
    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=200)
async def resend_verification(body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.resend_verification(email=body.email)
    return {"message": "Verification email sent if account exists"}

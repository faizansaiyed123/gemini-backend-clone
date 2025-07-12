from pydantic import BaseModel
from pydantic import BaseModel, Field, validator
import re

class UserSignup(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number with 10–15 digits")
    full_name: str | None = Field(None, max_length=100, description="Optional full name")
    password: str = Field(..., min_length=8, max_length=100, description="Password must be 8+ characters")

    @validator("mobile")
    def validate_mobile(cls, value):
        pattern = r"^\d{10,15}$"
        if not re.match(pattern, value):
            raise ValueError("Mobile must be 10–15 digits only")
        return value

    @validator("password")
    def validate_password(cls, value):
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must include at least one number")
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must include at least one letter")
        if not any(c in "!@#$%^&*()-_=+[{]};:<>|./?" for c in value):
            raise ValueError("Password must include at least one special character")
        return value



class SendOTPRequest(BaseModel):
    mobile: str


class SendOTPResponse(BaseModel):
    message: str
    otp: str


class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str


class MobileRequest(BaseModel):
    mobile: str






class ChangePasswordRequest(BaseModel):
    old_password: str | None = None
    new_password: str


    @validator("new_password")
    def validate_password(cls, value):
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must include at least one number")
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must include at least one letter")
        if not any(c in "!@#$%^&*()-_=+[{]};:<>|./?" for c in value):
            raise ValueError("Password must include at least one special character")
        return value



class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, value):
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must include at least one number")
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must include at least one letter")
        if not any(c in "!@#$%^&*()-_=+[{]};:<>|./?" for c in value):
            raise ValueError("Password must include at least one special character")
        return value

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class MedicalFacilityBase(BaseModel):
    medical_name: str = Field(..., description="医療機関名", min_length=1)
    address_postal_code: Optional[str] = Field(None, description="郵便番号")
    address_prefecture: Optional[str] = Field(None, description="都道府県")
    address_city: Optional[str] = Field(None, description="市区町村")
    address_line1: Optional[str] = Field(None, description="住所1")
    address_line2: Optional[str] = Field(None, description="住所2")
    phone_number: Optional[str] = Field(None, description="電話番号")
    
    @field_validator('medical_name')
    @classmethod
    def validate_medical_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('医療機関名は必須です')
        return v.strip()

class MedicalFacilityCreate(MedicalFacilityBase):
    pass

class MedicalFacility(MedicalFacilityBase):
    medical_id: int
    regdate: datetime
    lastupdate: datetime

    class Config:
        from_attributes = True

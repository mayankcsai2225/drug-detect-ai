from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TargetBase(BaseModel):
    platform: str
    handle: str
    url: Optional[str] = None
    subscriber_count: Optional[int] = None
    risk_score: float = 0.0
    status: str = "active"

class TargetCreate(TargetBase):
    pass

class TargetResponse(TargetBase):
    id: str
    first_seen: datetime
    last_scanned: Optional[datetime] = None
    created_at: datetime

class PostBase(BaseModel):
    target_id: str
    platform: str
    post_url: Optional[str] = None
    raw_text: Optional[str] = None
    ocr_text: Optional[str] = None
    detected_drugs: List[str] = []
    confidence_score: Optional[float] = None
    keyword_matched: bool = False
    ai_classified: bool = False
    has_image: bool = False
    image_path: Optional[str] = None
    sha256_hash: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    geo_address: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: str
    captured_at: datetime

class IdentityLeadBase(BaseModel):
    target_id: str
    lead_type: str
    value: str
    source: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    isp: Optional[str] = None
    confidence: Optional[str] = None
    verified: bool = False

class IdentityLeadCreate(IdentityLeadBase):
    pass

class IdentityLeadResponse(IdentityLeadBase):
    id: str
    created_at: datetime

class ScanJobBase(BaseModel):
    job_type: str
    status: str = "queued"
    targets_scanned: int = 0
    posts_found: int = 0
    threats_detected: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_log: Optional[str] = None

class ScanJobCreate(ScanJobBase):
    pass

class ScanJobResponse(ScanJobBase):
    id: str
    created_at: datetime

class AlertBase(BaseModel):
    post_id: Optional[str] = None
    target_id: Optional[str] = None
    alert_type: str
    severity: str
    message: str
    acknowledged: bool = False

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: str
    created_at: datetime

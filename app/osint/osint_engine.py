import re
import phonenumbers
import logging
import asyncio
import httpx
import exifread
from phonenumbers import geocoder, carrier
from email_validator import validate_email, EmailNotValidError
from typing import List, Dict, Any, Optional
from geopy.geocoders import Nominatim
import hashlib

logger = logging.getLogger(__name__)

# Regex Patterns
PHONE_REGEX = r'(\+?91[-\s]?[6-9]\d{9}|\+?[1-9]\d{6,14})'
EMAIL_REGEX = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
IP_REGEX = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
BTC_REGEX = r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}'
ETH_REGEX = r'0x[a-fA-F0-9]{40}'
XMR_REGEX = r'4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}'

class OSINTLead:
    def __init__(self, lead_type: str, value: str, source: str = "", confidence: str = "medium"):
        self.lead_type = lead_type
        self.value = value
        self.source = source
        self.confidence = confidence
        self.geo_country = None
        self.geo_city = None
        self.isp = None

async def extract_all_leads(text: str, source: str = "") -> List[Dict[str, Any]]:
    """
    Runs all extractors on the provided text.
    """
    leads = []
    
    # Extract Phones
    phones = re.findall(PHONE_REGEX, text)
    for p in phones:
        try:
            parsed = phonenumbers.parse(p, "IN")
            if phonenumbers.is_valid_number(parsed):
                val = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                geo = geocoder.description_for_number(parsed, "en")
                carr = carrier.name_for_number(parsed, "en")
                
                lead = {
                    "lead_type": "phone",
                    "value": val,
                    "source": source,
                    "geo_country": geo or "Unknown",
                    "confidence": "high",
                    "isp": carr
                }
                leads.append(lead)
        except:
            pass
            
    # Extract Emails
    emails = re.findall(EMAIL_REGEX, text)
    for e in emails:
        try:
            valid = validate_email(e)
            lead = {
                "lead_type": "email",
                "value": valid.email,
                "source": source,
                "confidence": "medium"
            }
            leads.append(lead)
        except EmailNotValidError:
            pass
            
    # Extract IPs
    ips = re.findall(IP_REGEX, text)
    async with httpx.AsyncClient() as client:
        for ip in ips:
            try:
                # ip-api.com free endpoint
                resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,query")
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        # Check for VPN/hosting in ASN
                        isp = data.get("isp", "")
                        asn = data.get("as", "")
                        comp = data.get("org", "")
                        conf = "low" if "VPN" in (isp + asn + comp).upper() or "HOSTING" in (isp + asn + comp).upper() else "medium"
                        
                        leads.append({
                            "lead_type": "ip",
                            "value": ip,
                            "source": source,
                            "geo_country": data.get("country"),
                            "geo_city": data.get("city"),
                            "isp": isp,
                            "confidence": conf
                        })
            except:
                pass

    # Extract Wallets
    for ticker, regex in [('BTC', BTC_REGEX), ('ETH', ETH_REGEX), ('XMR', XMR_REGEX)]:
        wallets = re.findall(regex, text)
        for w in set(wallets):
            leads.append({
                "lead_type": "wallet",
                "value": f"{ticker}: {w}",
                "source": source,
                "confidence": "high"
            })
            
    return leads

async def get_gps_data(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Extracts GPS coordinates from image EXIF metadata.
    Returns latitude, longitude, and address.
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            
        def _to_decimal(v):
            d, m, s = [float(x.num) / float(x.den) for x in v.values]
            return d + (m / 60.0) + (s / 3600.0)

        lat_ref = tags.get('GPS GPSLatitudeRef')
        lat = tags.get('GPS GPSLatitude')
        lon_ref = tags.get('GPS GPSLongitudeRef')
        lon = tags.get('GPS GPSLongitude')

        if not all([lat, lat_ref, lon, lon_ref]):
            return None

        lat_dec = _to_decimal(lat)
        if lat_ref.values[0] != 'N': lat_dec = -lat_dec
        
        lon_dec = _to_decimal(lon)
        if lon_ref.values[0] != 'E': lon_dec = -lon_dec

        # Reverse geocode via Nominatim
        geolocator = Nominatim(user_agent="ncb_drugnet_intelligence_platform")
        location = await asyncio.to_thread(geolocator.reverse, f"{lat_dec}, {lon_dec}")
        
        return {
            "geo_lat": lat_dec,
            "geo_lon": lon_dec,
            "geo_address": location.address if location else "Unknown"
        }
    except Exception as e:
        logger.error(f"Error extracting EXIF GPS from {image_path}: {e}")
        return None

def get_platform_links(username: str) -> Dict[str, str]:
    """
    Generates OSINT cross-platform username search links.
    """
    if not username:
        return {}
        
    return {
        "Telegram": f"https://t.me/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "TikTok": f"https://tiktok.com/@{username}"
    }

def calculate_post_hash(text: str, image_content: Optional[bytes] = None) -> str:
    """
    Generates SHA-256 integrity hash for a post.
    """
    sha = hashlib.sha256()
    sha.update(text.encode('utf-8'))
    if image_content:
        sha.update(image_content)
    return sha.hexdigest()

"""
Ibanista Lead Capture API
Email automation backend emulating HubSpot functionality
"""
import os
import re
import ssl
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")

# Handle Neon/Postgres SSL if needed
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
    DATABASE_URL = re.sub(r'[\?&]sslmode=[^&]*', '', DATABASE_URL)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    engine = create_engine(DATABASE_URL, connect_args={"ssl_context": ssl_context})
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True)
    name = Column(String(255), nullable=True)
    source = Column(String(50))  # 'calculator', 'quiz', 'newsletter'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Calculator data
    uk_rent = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)
    household_size = Column(Integer, nullable=True)
    move_type = Column(String(50), nullable=True)
    monthly_savings = Column(Float, nullable=True)

    # Quiz data
    quiz_answers = Column(Text, nullable=True)  # JSON string
    top_regions = Column(Text, nullable=True)   # JSON string of top 3 matches

    # Email tracking
    welcome_sent = Column(DateTime, nullable=True)
    followup_sent = Column(DateTime, nullable=True)


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    email_type = Column(String(50))  # 'welcome', 'quiz_followup', 'calculator_followup'
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20))  # 'sent', 'failed', 'queued'
    error_message = Column(Text, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic schemas
class CalculatorSubmission(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    uk_rent: float
    region: str
    household_size: int
    move_type: str
    monthly_savings: float

    @field_validator('uk_rent', 'monthly_savings')
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v


class QuizSubmission(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    answers: dict
    top_regions: list


class NewsletterSignup(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    email: str
    source: str
    created_at: datetime
    name: Optional[str] = None
    region: Optional[str] = None
    top_regions: Optional[list] = None


# Email templates
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to Ibanista - Your French Adventure Starts Here",
        "body": """
Hi {name},

Thank you for exploring your move to France with Ibanista!

We're here to make your relocation smooth, supported, and stress-free. Whether you're
dreaming of Provence's lavender fields, Bordeaux's wine country, or Paris's cultural riches,
we've helped hundreds of UK expats make France their home.

What happens next:
1. Our team will review your information
2. We'll send you a personalized relocation guide within 24 hours
3. You can book a free consultation call at any time

In the meantime, explore our resources:
- Money Transfers: https://www.ibanista.com/money-transfer/
- Long-Term Rentals: https://www.ibanista.com/long-term-rentals/
- Power Hour Consultation: https://www.ibanista.com/power-hour/

Questions? Reply to this email or call us at +44 203 376 5117.

À bientôt!

The Ibanista Team
https://www.ibanista.com
"""
    },
    "calculator_followup": {
        "subject": "Your France Relocation Budget - Next Steps",
        "body": """
Hi {name},

Great news! Based on your calculator results, moving to {region} could save you
approximately £{monthly_savings:.0f} per month compared to your current UK rent.

That's £{annual_savings:.0f} per year that could go towards:
- Exploring France's incredible food and wine scene
- Weekend trips to neighboring countries
- Building your new life in France

Your personalized breakdown:
- Current UK Rent: £{uk_rent:.0f}/month
- Estimated France Rent: €{france_rent:.0f}/month
- Move Type: {move_type}

Ready to make it real? Here's how we can help:

1. **Free Consultation** - Book a 30-minute call to discuss your move
   https://www.ibanista.com/power-hour/

2. **Long-Term Rentals** - We'll find your perfect French home
   https://www.ibanista.com/long-term-rentals/

3. **Money Transfers** - Save on currency exchange
   https://www.ibanista.com/money-transfer/

Reply to this email with any questions - we're here to help!

The Ibanista Team
"""
    },
    "quiz_followup": {
        "subject": "Your Perfect French Region: {top_region}",
        "body": """
Hi {name},

Based on your lifestyle preferences, we've found your ideal French destinations!

Your Top 3 Matches:
1. {region_1} - {match_1}% match
2. {region_2} - {match_2}% match
3. {region_3} - {match_3}% match

Why {top_region} suits you:
{region_description}

What makes {top_region} special for UK expats:
- Established British community for support and socializing
- Direct transport links to the UK
- English-friendly services and healthcare

Ready to explore {top_region}? Here's your next step:

**Book a Free Discovery Call**
We'll discuss your specific needs, timeline, and how Ibanista can
make your move seamless.

https://www.ibanista.com/power-hour/

Questions about {top_region}? Just reply to this email!

À bientôt,

The Ibanista Team
"""
    }
}

REGION_DESCRIPTIONS = {
    "Ile-de-France": "Paris and its surroundings offer world-class culture, career opportunities, and urban excitement. Perfect for professionals and culture enthusiasts.",
    "Provence-Alpes-Côte d'Azur": "Sun-drenched Mediterranean lifestyle with stunning coastlines, vibrant markets, and a relaxed pace of life. Ideal for those seeking warmth and beauty.",
    "Nouvelle-Aquitaine": "Bordeaux's wine country combines gastronomy, history, and a growing tech scene. Great for foodies and those seeking work-life balance.",
    "Occitanie": "From Toulouse's aerospace industry to Montpellier's beaches, this diverse region offers affordability and sunshine. Perfect for families and remote workers.",
    "Bretagne": "Celtic heritage, dramatic coastlines, and tight-knit communities. Ideal for nature lovers and those seeking authentic French village life.",
    "Auvergne-Rhône-Alpes": "Lyon's gastronomic capital status plus Alpine adventures. Perfect for food lovers and outdoor enthusiasts alike."
}


# Email sending function
def send_email(to_email: str, subject: str, body: str, lead_id: int, email_type: str) -> bool:
    """Send email via SMTP (configure with environment variables)"""
    db = SessionLocal()

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_email = os.getenv("FROM_EMAIL", "hello@ibanista.com")

    # If no SMTP configured, log and skip
    if not smtp_host or not smtp_user:
        log = EmailLog(
            lead_id=lead_id,
            email_type=email_type,
            status="queued",
            error_message="SMTP not configured - email queued for manual send"
        )
        db.add(log)
        db.commit()
        db.close()
        print(f"[EMAIL QUEUED] To: {to_email}, Type: {email_type}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Ibanista <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        log = EmailLog(
            lead_id=lead_id,
            email_type=email_type,
            status="sent"
        )
        db.add(log)
        db.commit()
        print(f"[EMAIL SENT] To: {to_email}, Type: {email_type}")
        return True

    except Exception as e:
        log = EmailLog(
            lead_id=lead_id,
            email_type=email_type,
            status="failed",
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        print(f"[EMAIL FAILED] To: {to_email}, Error: {e}")
        return False
    finally:
        db.close()


# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ibanista Lead API starting...")
    yield
    print("Ibanista Lead API shutting down...")


# FastAPI app
app = FastAPI(
    title="Ibanista Lead Capture API",
    description="Email automation backend for Ibanista Tools",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ibanista-tools.vercel.app",
        "https://www.ibanista.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ibanista-lead-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/leads/calculator", response_model=LeadResponse)
def submit_calculator(data: CalculatorSubmission, background_tasks: BackgroundTasks):
    """Capture lead from budget calculator"""
    db = SessionLocal()
    try:
        lead = Lead(
            email=data.email,
            name=data.name or data.email.split('@')[0],
            source="calculator",
            uk_rent=data.uk_rent,
            region=data.region,
            household_size=data.household_size,
            move_type=data.move_type,
            monthly_savings=data.monthly_savings
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Queue welcome email
        name = data.name or data.email.split('@')[0]
        welcome_body = EMAIL_TEMPLATES["welcome"]["body"].format(name=name)
        background_tasks.add_task(
            send_email,
            data.email,
            EMAIL_TEMPLATES["welcome"]["subject"],
            welcome_body,
            lead.id,
            "welcome"
        )

        # Queue calculator follow-up
        france_rent = data.uk_rent - data.monthly_savings
        followup_body = EMAIL_TEMPLATES["calculator_followup"]["body"].format(
            name=name,
            region=data.region,
            monthly_savings=data.monthly_savings,
            annual_savings=data.monthly_savings * 12,
            uk_rent=data.uk_rent,
            france_rent=france_rent,
            move_type=data.move_type
        )
        background_tasks.add_task(
            send_email,
            data.email,
            EMAIL_TEMPLATES["calculator_followup"]["subject"],
            followup_body,
            lead.id,
            "calculator_followup"
        )

        return LeadResponse(
            id=lead.id,
            email=lead.email,
            source=lead.source,
            created_at=lead.created_at,
            name=lead.name,
            region=lead.region
        )
    finally:
        db.close()


@app.post("/api/leads/quiz", response_model=LeadResponse)
def submit_quiz(data: QuizSubmission, background_tasks: BackgroundTasks):
    """Capture lead from region finder quiz"""
    db = SessionLocal()
    try:
        lead = Lead(
            email=data.email,
            name=data.name or data.email.split('@')[0],
            source="quiz",
            quiz_answers=json.dumps(data.answers),
            top_regions=json.dumps(data.top_regions)
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Queue welcome email
        name = data.name or data.email.split('@')[0]
        welcome_body = EMAIL_TEMPLATES["welcome"]["body"].format(name=name)
        background_tasks.add_task(
            send_email,
            data.email,
            EMAIL_TEMPLATES["welcome"]["subject"],
            welcome_body,
            lead.id,
            "welcome"
        )

        # Queue quiz follow-up
        top_region = data.top_regions[0]["name"] if data.top_regions else "France"
        region_desc = REGION_DESCRIPTIONS.get(top_region, "A wonderful destination for your new life in France.")

        followup_subject = EMAIL_TEMPLATES["quiz_followup"]["subject"].format(top_region=top_region)
        followup_body = EMAIL_TEMPLATES["quiz_followup"]["body"].format(
            name=name,
            top_region=top_region,
            region_1=data.top_regions[0]["name"] if len(data.top_regions) > 0 else "N/A",
            match_1=data.top_regions[0]["score"] if len(data.top_regions) > 0 else 0,
            region_2=data.top_regions[1]["name"] if len(data.top_regions) > 1 else "N/A",
            match_2=data.top_regions[1]["score"] if len(data.top_regions) > 1 else 0,
            region_3=data.top_regions[2]["name"] if len(data.top_regions) > 2 else "N/A",
            match_3=data.top_regions[2]["score"] if len(data.top_regions) > 2 else 0,
            region_description=region_desc
        )
        background_tasks.add_task(
            send_email,
            data.email,
            followup_subject,
            followup_body,
            lead.id,
            "quiz_followup"
        )

        return LeadResponse(
            id=lead.id,
            email=lead.email,
            source=lead.source,
            created_at=lead.created_at,
            name=lead.name,
            top_regions=data.top_regions
        )
    finally:
        db.close()


@app.post("/api/leads/newsletter", response_model=LeadResponse)
def submit_newsletter(data: NewsletterSignup, background_tasks: BackgroundTasks):
    """Capture lead from newsletter signup"""
    db = SessionLocal()
    try:
        lead = Lead(
            email=data.email,
            name=data.name or data.email.split('@')[0],
            source="newsletter"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Queue welcome email
        name = data.name or data.email.split('@')[0]
        welcome_body = EMAIL_TEMPLATES["welcome"]["body"].format(name=name)
        background_tasks.add_task(
            send_email,
            data.email,
            EMAIL_TEMPLATES["welcome"]["subject"],
            welcome_body,
            lead.id,
            "welcome"
        )

        return LeadResponse(
            id=lead.id,
            email=lead.email,
            source=lead.source,
            created_at=lead.created_at,
            name=lead.name
        )
    finally:
        db.close()


@app.get("/api/leads")
def list_leads(source: Optional[str] = None, limit: int = 100):
    """List all captured leads (admin endpoint)"""
    db = SessionLocal()
    try:
        query = db.query(Lead)
        if source:
            query = query.filter(Lead.source == source)
        leads = query.order_by(Lead.created_at.desc()).limit(limit).all()

        return {
            "total": len(leads),
            "leads": [
                {
                    "id": l.id,
                    "email": l.email,
                    "name": l.name,
                    "source": l.source,
                    "created_at": l.created_at.isoformat(),
                    "region": l.region,
                    "monthly_savings": l.monthly_savings,
                    "top_regions": json.loads(l.top_regions) if l.top_regions else None
                }
                for l in leads
            ]
        }
    finally:
        db.close()


@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int):
    """Get specific lead details"""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        emails = db.query(EmailLog).filter(EmailLog.lead_id == lead_id).all()

        return {
            "id": lead.id,
            "email": lead.email,
            "name": lead.name,
            "source": lead.source,
            "created_at": lead.created_at.isoformat(),
            "calculator_data": {
                "uk_rent": lead.uk_rent,
                "region": lead.region,
                "household_size": lead.household_size,
                "move_type": lead.move_type,
                "monthly_savings": lead.monthly_savings
            } if lead.source == "calculator" else None,
            "quiz_data": {
                "answers": json.loads(lead.quiz_answers) if lead.quiz_answers else None,
                "top_regions": json.loads(lead.top_regions) if lead.top_regions else None
            } if lead.source == "quiz" else None,
            "emails_sent": [
                {
                    "type": e.email_type,
                    "status": e.status,
                    "sent_at": e.sent_at.isoformat(),
                    "error": e.error_message
                }
                for e in emails
            ]
        }
    finally:
        db.close()


@app.get("/api/stats")
def get_stats():
    """Get lead capture statistics"""
    db = SessionLocal()
    try:
        total = db.query(Lead).count()
        by_source = {
            "calculator": db.query(Lead).filter(Lead.source == "calculator").count(),
            "quiz": db.query(Lead).filter(Lead.source == "quiz").count(),
            "newsletter": db.query(Lead).filter(Lead.source == "newsletter").count()
        }
        emails_sent = db.query(EmailLog).filter(EmailLog.status == "sent").count()
        emails_queued = db.query(EmailLog).filter(EmailLog.status == "queued").count()

        return {
            "total_leads": total,
            "by_source": by_source,
            "emails": {
                "sent": emails_sent,
                "queued": emails_queued
            }
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import os
import json
from typing import Literal, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config

# Industry-standard email taxonomy (helpdesk / email-ops style).
EmailCategory = Literal[
    "SECURITY",
    "BILLING",
    "SYSTEM_ALERT",
    "SUPPORT",
    "SALES",
    "RECRUITMENT",
    "NEWSLETTER",
    "PROMOTION",
    "SOCIAL",
    "LEGAL",
    "PERSONAL",
    "SPAM",
    "OTHER",
]


class EmailAnalysis(BaseModel):
    important: bool = Field(description="True if the email is worth surfacing to the user, false only for pure spam")
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="HIGH, MEDIUM, or LOW")
    category: EmailCategory = Field(description="One of the fixed taxonomy categories")
    reason: str = Field(description="One sentence rationale string")

class AIClassifierService:
    def __init__(self):
        api_key = config("GEMINI_API_KEY", default=None)
        
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0,
            # Fail fast to the rule-based fallback instead of hanging for minutes
            # when the API is rate-limited or the daily quota is exhausted.
            max_retries=1,
        ) # type: ignore
        
        # Fallback to a bulletproof native JSON output parser
        self.parser = JsonOutputParser(pydantic_object=EmailAnalysis)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Operations Engineer triaging incoming business emails.\n"
                "Read the sender, subject, and body, then reason about how the user should treat this email.\n"
                "Return a structured decision that matches the schema specifications.\n\n"
                "IMPORTANCE RULES:\n"
                "- 'important: true' for anything the user should see on their dashboard "
                "(security, billing, system, support, sales, recruitment, newsletters, "
                "promotions, social, legal, personal — even low-priority automated mail).\n"
                "- 'important: false' ONLY for pure spam, phishing, or junk with no value.\n\n"
                "CATEGORY RULES (choose EXACTLY one, the single best fit):\n"
                "- SECURITY     -> login alerts, suspicious activity, password resets, 2FA, breaches\n"
                "- BILLING      -> payments, invoices, receipts, subscription charges, refunds, payouts\n"
                "- SYSTEM_ALERT -> outages, downtime, crashes, monitoring/health-check failures, error reports\n"
                "- SUPPORT      -> customer questions, complaints, support tickets, help requests\n"
                "- SALES        -> sales leads, prospect inquiries, deals, demo or quote requests\n"
                "- RECRUITMENT  -> job alerts, applications, interviews, recruiter outreach, offers\n"
                "- NEWSLETTER   -> newsletters, digests, blogs, content/product updates\n"
                "- PROMOTION    -> marketing, discounts, offers, advertisements\n"
                "- SOCIAL       -> social network notifications (connections, likes, mentions, follows)\n"
                "- LEGAL        -> policy/terms updates, compliance, privacy notices, contracts\n"
                "- PERSONAL     -> genuine person-to-person correspondence\n"
                "- SPAM         -> junk, phishing, scams (pair with important: false)\n"
                "- OTHER        -> use only when nothing above fits\n\n"
                "PRIORITY RULES:\n"
                "- HIGH   -> SECURITY threats, BILLING failures, SYSTEM_ALERT outages, urgent SUPPORT, hot SALES leads\n"
                "- MEDIUM -> routine SUPPORT/SALES/RECRUITMENT, LEGAL notices, PERSONAL mail needing a reply\n"
                "- LOW    -> NEWSLETTER, PROMOTION, SOCIAL, and other automated low-urgency notices\n\n"
                "OUTPUT INSTRUCTIONS:\n{format_instructions}"
            )),
            ("human", "SENDER: {sender}\nSUBJECT: {subject}\nBODY:\n{body}")
        ])
        
        self.chain = self.prompt_template | self.llm | self.parser

    def analyze_email(self, sender: str, subject: str, body: str) -> EmailAnalysis:
        api_key = config("GEMINI_API_KEY", default=None)
        if not api_key or api_key == "your_actual_gemini_api_key_here":
            return self._rule_based_fallback(subject)
            
        try:
            instructions = self.parser.get_format_instructions()
            raw_result = self.chain.invoke({
                "sender": sender,
                "subject": subject,
                "body": body,
                "format_instructions": instructions
            })
            
            return EmailAnalysis(
                important=bool(raw_result.get("important", False)),
                priority=raw_result.get("priority", "LOW"),
                category=raw_result.get("category", "OTHER"),
                reason=str(raw_result.get("reason", "Processed by parser output structure node."))
            )
        except Exception as e:
            print(f"[AI SERVICE WARNING] Pipeline exception, invoking backup: {e}")
            return self._rule_based_fallback(subject)

    def _rule_based_fallback(self, subject: str) -> EmailAnalysis:
        sub_lower = subject.lower()

        def has(*words):
            return any(w in sub_lower for w in words)

        if has("security", "suspicious", "password", "2fa", "verify your", "unusual activity", "sign-in", "login"):
            return EmailAnalysis(important=True, priority="HIGH", category="SECURITY", reason="Rule Engine: Flagged as an account security alert.")
        if has("chargeback", "payment", "billing", "invoice", "receipt", "payout", "refund"):
            return EmailAnalysis(important=True, priority="HIGH", category="BILLING", reason="Rule Engine: Flagged due to billing/payment keywords.")
        if has("job", "application", "interview", "recruit", "hiring", "vacancy", "position"):
            return EmailAnalysis(important=True, priority="MEDIUM", category="RECRUITMENT", reason="Rule Engine: Flagged as a recruitment/job-related email.")
        if has("crash", "unreachable", "outage", "incident", "degraded", "downtime"):
            return EmailAnalysis(important=True, priority="HIGH", category="SYSTEM_ALERT", reason="Rule Engine: Flagged due to system/outage terminology.")
        if has("complaint", "urgent", "not working", "issue", "help", "support", "ticket"):
            return EmailAnalysis(important=True, priority="MEDIUM", category="SUPPORT", reason="Rule Engine: Flagged as a support request or complaint.")
        if has("policy", "terms", "privacy", "compliance", "agreement", "legal"):
            return EmailAnalysis(important=True, priority="MEDIUM", category="LEGAL", reason="Rule Engine: Flagged as a legal/policy notice.")
        if has("sale", "discount", "offer", "deal", "% off", "promo", "limited time"):
            return EmailAnalysis(important=True, priority="LOW", category="PROMOTION", reason="Rule Engine: Flagged as a promotional/marketing email.")
        if has("newsletter", "digest", "weekly", "update", "blog"):
            return EmailAnalysis(important=True, priority="LOW", category="NEWSLETTER", reason="Rule Engine: Flagged as a newsletter/digest.")
        if has("connection", "mentioned you", "liked", "follow", "viewed your"):
            return EmailAnalysis(important=True, priority="LOW", category="SOCIAL", reason="Rule Engine: Flagged as a social network notification.")
        if has("win", "winner", "free", "lottery", "congratulations", "claim now", "prize"):
            return EmailAnalysis(important=False, priority="LOW", category="SPAM", reason="Rule Engine: Identified as junk with no business value.")
        return EmailAnalysis(important=True, priority="LOW", category="OTHER", reason="Rule Engine: Low-priority general email.")
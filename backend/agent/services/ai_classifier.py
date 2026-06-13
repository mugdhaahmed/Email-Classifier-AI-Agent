import os
import json
from typing import Literal, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config

class EmailAnalysis(BaseModel):
    important: bool = Field(description="True if the email is worth surfacing to the user, false only for pure spam")
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="HIGH, MEDIUM, or LOW")
    category: Literal[
        "PAYMENT_ISSUE", "SERVER_DOWN", "CLIENT_COMPLAINT", "SUBSCRIPTION", "SPAM"
    ] = Field(description="One of the fixed taxonomy categories")
    reason: str = Field(description="One sentence rationale string")

class AIClassifierService:
    def __init__(self):
        api_key = config("GEMINI_API_KEY", default=None)
        
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash", 
            google_api_key=api_key,
            temperature=0.0
        ) # type: ignore
        
        # Fallback to a bulletproof native JSON output parser
        self.parser = JsonOutputParser(pydantic_object=EmailAnalysis)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Operations Engineer triaging incoming business emails.\n"
                "Read the sender, subject, and body, then reason about how the user should treat this email.\n"
                "Return a structured decision that matches the schema specifications.\n\n"
                "IMPORTANCE RULES:\n"
                "- 'important: true' for anything the user should see on their dashboard. This includes:\n"
                "    * Client complaints or urgent customer requests\n"
                "    * Payment failures or billing issues\n"
                "    * Critical system downtime or server alerts\n"
                "    * Low-priority automated or subscription emails (these are still shown, just low priority)\n"
                "- 'important: false' ONLY for pure spam or junk with no business value.\n\n"
                "PRIORITY RULES:\n"
                "- HIGH  -> payment failures, server outages, urgent client complaints\n"
                "- MEDIUM-> non-urgent client requests or issues needing follow-up\n"
                "- LOW   -> automated notices, newsletters, subscription updates\n\n"
                "CATEGORY RULES (choose exactly one):\n"
                "- PAYMENT_ISSUE    -> billing, invoices, chargebacks, payouts\n"
                "- SERVER_DOWN      -> outages, crashes, downtime, health-check failures\n"
                "- CLIENT_COMPLAINT -> customer complaints or urgent customer requests\n"
                "- SUBSCRIPTION     -> newsletters, automated product/marketing updates\n"
                "- SPAM             -> junk with no business value (pair with important: false)\n\n"
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
                category=raw_result.get("category", "SUBSCRIPTION"),
                reason=str(raw_result.get("reason", "Processed by parser output structure node."))
            )
        except Exception as e:
            print(f"[AI SERVICE WARNING] Pipeline exception, invoking backup: {e}")
            return self._rule_based_fallback(subject)

    def _rule_based_fallback(self, subject: str) -> EmailAnalysis:
        sub_lower = subject.lower()
        if "chargeback" in sub_lower or "failure" in sub_lower or "billing" in sub_lower or "invoice" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="PAYMENT_ISSUE", reason="Rule Engine: Flagged due to payment crisis keywords.")
        if "crash" in sub_lower or "unreachable" in sub_lower or "down" in sub_lower or "outage" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="SERVER_DOWN", reason="Rule Engine: Flagged due to critical server downtime terminology.")
        if "complaint" in sub_lower or "urgent" in sub_lower or "refund" in sub_lower or "not working" in sub_lower:
            return EmailAnalysis(important=True, priority="MEDIUM", category="CLIENT_COMPLAINT", reason="Rule Engine: Flagged as a customer complaint or urgent request.")
        if "unsubscribe" in sub_lower or "win" in sub_lower or "free" in sub_lower or "lottery" in sub_lower:
            return EmailAnalysis(important=False, priority="LOW", category="SPAM", reason="Rule Engine: Identified as junk with no business value.")
        return EmailAnalysis(important=True, priority="LOW", category="SUBSCRIPTION", reason="Rule Engine: Low-priority automated or subscription update.")
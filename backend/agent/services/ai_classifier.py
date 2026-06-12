import os
from typing import Literal, Any, cast
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config

# 1. Define response schema shape
class EmailAnalysis(BaseModel):
    important: bool = Field(
        description="Set to true ONLY if the email requires immediate action like client complaints, billing issues, infrastructure crashes, or urgent requests. Set to false for newsletters, promotions, or spam."
    )
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="HIGH for system crashes or payment blockages; MEDIUM for client tickets/complaints; LOW for normal updates."
    )
    category: str = Field(
        description="A clear, short keyword in uppercase, e.g., PAYMENT_ISSUE, SERVER_DOWN, CLIENT_COMPLAINT, SPAM, MARKETING."
    )
    reason: str = Field(
        description="A single clear sentence explaining exactly why this email was or wasn't flagged as important."
    )

class AIClassifierService:
    def __init__(self):
        # Retrieve the API key from python-decouple safely
        api_key = config("GEMINI_API_KEY", default=None)
        
        # # type: ignore tells Pylance to skip signature mismatches caused by underlying Google SDK dynamic params
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.0
        )  # type: ignore
        
        # FIX: We cast the class blueprint itself to Any inside the method parameter slot.
        # This bypasses the structural schema mismatch error perfectly while preserving runtime schema execution.
        self.structured_llm: Runnable[Any, EmailAnalysis] = cast(
            Runnable[Any, EmailAnalysis],
            self.llm.with_structured_output(cast(Any, EmailAnalysis))
        )
        
        # Build strict system guardrails into the prompt context
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert AI Operations Engineer triaging incoming system emails.\n"
                "Analyze the sender, subject, and body to produce structural attributes.\n\n"
                "CRITICAL TAXONOMY RULES:\n"
                "- Flag 'important: true' for customer distress, payment failures, or critical downtime alerts.\n"
                "- Flag 'important: false' for subscription updates, generalized tech news, and spam."
            )),
            ("human", "SENDER: {sender}\nSUBJECT: {subject}\nBODY:\n{body}")
        ])
        
        self.chain = self.prompt_template | self.structured_llm

    def analyze_email(self, sender: str, subject: str, body: str) -> EmailAnalysis:
        """
        Processes an email body text through Gemini using structured output logic.
        Falls back smoothly to a programmatic rule engine if no API key is specified.
        """
        api_key = config("GEMINI_API_KEY", default=None)
        if not api_key or api_key == "your_actual_gemini_api_key_here":
            return self._rule_based_fallback(subject)
            
        try:
            return self.chain.invoke({
                "sender": sender,
                "subject": subject,
                "body": body
            })
        except Exception as e:
            print(f"[AI SERVICE WARNING] Pipeline call failed, invoking deterministic backup rules: {e}")
            return self._rule_based_fallback(subject)

    def _rule_based_fallback(self, subject: str) -> EmailAnalysis:
        """Deterministic programmatic rule-engine fallback for safety or offline mock execution."""
        sub_lower = subject.lower()
        if "chargeback" in sub_lower or "failure" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="PAYMENT_ISSUE", reason="Rule Engine: Flagged due to payment crisis keywords.")
        if "crash" in sub_lower or "unreachable" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="SERVER_DOWN", reason="Rule Engine: Flagged due to critical server downtime terminology.")
        return EmailAnalysis(important=False, priority="LOW", category="MARKETING", reason="Rule Engine: Identified as regular informational/subscription update.")
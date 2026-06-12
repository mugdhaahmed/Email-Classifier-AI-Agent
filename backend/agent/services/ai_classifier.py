import os
import json
from typing import Literal, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config

class EmailAnalysis(BaseModel):
    important: bool = Field(description="True if critical request/failure, false otherwise")
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="HIGH, MEDIUM, or LOW")
    category: str = Field(description="Short uppercase string keyword")
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
                "You are an expert AI Operations Engineer triaging incoming system emails.\n"
                "Analyze the email input and provide structured taxonomy metrics matching the schema specifications.\n\n"
                "CRITICAL TAXONOMY RULES:\n"
                "- Flag 'important: true' for customer distress, payment failures, or critical downtime alerts.\n"
                "- Flag 'important: false' for subscription updates, generalized tech news, and spam.\n\n"
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
                category=str(raw_result.get("category", "GENERAL")),
                reason=str(raw_result.get("reason", "Processed by parser output structure node."))
            )
        except Exception as e:
            print(f"[AI SERVICE WARNING] Pipeline exception, invoking backup: {e}")
            return self._rule_based_fallback(subject)

    def _rule_based_fallback(self, subject: str) -> EmailAnalysis:
        sub_lower = subject.lower()
        if "chargeback" in sub_lower or "failure" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="PAYMENT_ISSUE", reason="Rule Engine: Flagged due to payment crisis keywords.")
        if "crash" in sub_lower or "unreachable" in sub_lower:
            return EmailAnalysis(important=True, priority="HIGH", category="SERVER_DOWN", reason="Rule Engine: Flagged due to critical server downtime terminology.")
        return EmailAnalysis(important=False, priority="LOW", category="MARKETING", reason="Rule Engine: Identified as regular informational update.")
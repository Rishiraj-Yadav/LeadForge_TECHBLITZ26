"""Research agent — runs fast legitimacy checks."""

from app.agents.base import BaseAgent
from app.agents.research.tools import search_company, estimate_domain_age, validate_email_from_text
from app.schemas.agent_state import AgentState


class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        company_name = lead.get("customer_name") or lead.get("details", {}).get("company_name")
        message = lead.get("message", "")

        legitimacy_score = 5.0
        company_info = {}
        social_profiles = []
        summary_parts = []

        if company_name:
            try:
                results = await search_company(company_name)
                organic = results.get("organic", [])
                legitimacy_score += min(3.0, len(organic) * 0.6)
                company_info = {"results_found": len(organic), "top_results": organic[:3]}
                social_profiles = [item.get("link", "") for item in organic[:3] if item.get("link")]
                summary_parts.append(f"Found {len(organic)} search results for {company_name}")
            except Exception as exc:
                summary_parts.append(f"Search unavailable: {exc}")

        extracted_email = validate_email_from_text(message)
        if extracted_email:
            legitimacy_score += 0.5
            summary_parts.append("Email address detected in inquiry")

        website = lead.get("details", {}).get("website")
        domain_age = estimate_domain_age(website)
        if domain_age != "unknown":
            legitimacy_score += 0.5
            summary_parts.append(domain_age)

        legitimacy_score = round(min(10.0, legitimacy_score), 1)
        state["research"] = {
            "legitimacy_score": legitimacy_score,
            "company_info": company_info,
            "social_profiles": social_profiles,
            "domain_age": domain_age,
            "summary": "; ".join(summary_parts) or "Limited public signals found",
        }
        state["current_agent"] = self.name
        state["next_agent"] = "scoring"
        return state

"""
Planner for generating multi-step execution plans.

Separates planning from execution for true autonomy.
"""

import json
from typing import Any

import structlog

from src.models.schemas import AgentPlan

logger = structlog.get_logger(__name__)


class Planner:
    """
    Generates multi-step plans for complex tasks.

    The planner analyzes the goal and available tools to create
    a structured execution plan.
    """

    PLANNER_PROMPT = """You are a cybersecurity task planner. Given a goal and available tools, create a detailed execution plan.

Goal: {goal}

Available Tools:
{tools}

Create a step-by-step plan to achieve the goal. Each step should specify:
- tool: The tool to use
- params: Parameters for the tool
- reasoning: Why this step is needed

Respond with a JSON object:
{{
    "goal": "Restate the goal",
    "steps": [
        {{"tool": "tool_name", "params": {{}}, "reasoning": "why"}},
        ...
    ],
    "estimated_complexity": 0.0-1.0,
    "reasoning": "Overall plan explanation"
}}

Important:
- Start with passive, low-risk operations (query_threat_intel, scan_environment)
- Use propose_action for any high-risk operations
- Keep plans focused and efficient (3-7 steps ideal)
- Consider dependencies between steps"""

    def __init__(self, ollama_client: Any, available_tools: dict[str, Any]):
        """
        Initialize planner.

        Args:
            ollama_client: Ollama client for LLM inference
            available_tools: Dictionary of available tools
        """
        self.ollama_client = ollama_client
        self.available_tools = available_tools

    async def create_plan(self, goal: str) -> AgentPlan:
        """
        Create a multi-step plan for the given goal.

        Args:
            goal: The goal to achieve

        Returns:
            AgentPlan with ordered steps
        """
        logger.info("planner.creating_plan", goal=goal[:100])

        try:
            # Format tool descriptions
            tools_desc = self._format_tools()

            prompt = self.PLANNER_PROMPT.format(goal=goal, tools=tools_desc)

            response = await self.ollama_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=1000,
            )

            # Parse plan from response
            plan_data = self._parse_json_response(response)
            plan = AgentPlan(**plan_data)

            logger.info(
                "planner.plan_created",
                steps=len(plan.steps),
                complexity=plan.estimated_complexity,
            )

            return plan

        except Exception as e:
            logger.error("planner.plan_creation_failed", error=str(e))
            # Return minimal fallback plan
            return AgentPlan(
                goal=goal,
                steps=[
                    {
                        "tool": "query_threat_intel",
                        "params": {"query": goal, "k": 3},
                        "reasoning": "Gather context",
                    }
                ],
                estimated_complexity=0.5,
                reasoning="Fallback plan due to planning error",
            )

    def _format_tools(self) -> str:
        """Format available tools for prompt."""
        tool_descriptions = []
        for name, tool in self.available_tools.items():
            params = tool.get_parameters() if hasattr(tool, "get_parameters") else {}
            tool_descriptions.append(
                f"- {name}: {tool.description if hasattr(tool, 'description') else 'No description'}"
            )
            tool_descriptions.append(f"  Parameters: {json.dumps(params, indent=2)}")
        return "\n".join(tool_descriptions)

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("planner.json_parse_failed", response=response[:100])
            raise

    async def refine_plan(
        self, plan: AgentPlan, completed_steps: list[dict[str, Any]], observations: list[str]
    ) -> AgentPlan:
        """
        Refine plan based on execution results.

        Args:
            plan: Original plan
            completed_steps: Steps completed so far
            observations: Observations from completed steps

        Returns:
            Refined AgentPlan
        """
        logger.info("planner.refining_plan", completed=len(completed_steps))

        try:
            refinement_prompt = f"""Original Goal: {plan.goal}

Original Plan: {json.dumps(plan.steps, indent=2)}

Completed Steps: {json.dumps(completed_steps, indent=2)}

Observations: {json.dumps(observations, indent=2)}

Based on the observations, refine the remaining steps. Respond with updated plan JSON."""

            response = await self.ollama_client.generate(
                prompt=refinement_prompt,
                temperature=0.2,
                max_tokens=1000,
            )

            refined_data = self._parse_json_response(response)
            refined_plan = AgentPlan(**refined_data)

            logger.info("planner.plan_refined", new_steps=len(refined_plan.steps))

            return refined_plan

        except Exception as e:
            logger.error("planner.refinement_failed", error=str(e))
            # Return original plan if refinement fails
            return plan

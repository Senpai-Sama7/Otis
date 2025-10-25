"""ReAct agent implementation with tool execution loop."""

import asyncio
import json
from typing import Any

from src.agent.model import OllamaModel
from src.core.logging import get_logger
from src.models.schemas import AgentRequest, AgentResponse

logger = get_logger(__name__)


class ReactAgent:
    """
    ReAct (Reasoning + Acting) agent with tool execution loop.

    Policy:
    - Passive-first: Starts with low-risk operations
    - Max iterations: 2 tool calls
    - Max execution time: 45 seconds
    - High risk requires human approval
    """

    def __init__(
        self,
        model: OllamaModel,
        tools: dict[str, Any],
        max_iterations: int = 2,
        max_exec_time: int = 45,
    ):
        self.model = model
        self.tools = tools
        self.max_iterations = max_iterations
        self.max_exec_time = max_exec_time

    async def run(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the ReAct loop for the given request.

        Args:
            request: Agent request with instruction and configuration

        Returns:
            Agent response with summary, steps, proposals, evidence, and confidence
        """
        logger.info(
            "Starting ReAct agent",
            instruction=request.instruction,
            mode=request.mode,
        )

        steps = []
        proposals = []
        evidence = []
        start_time = asyncio.get_event_loop().time()

        try:
            # Enforce passive mode by default for safety
            mode = request.mode if request.mode else "passive"

            # Build initial prompt with available tools
            tool_descriptions = self._format_tool_descriptions()
            prompt = self._build_prompt(request.instruction, mode, tool_descriptions)

            # ReAct loop with limited iterations
            for iteration in range(self.max_iterations):
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.max_exec_time:
                    logger.warning("Agent execution timeout", elapsed=elapsed)
                    break

                # Get model reasoning and action
                response = await self.model.infer(prompt, temperature=0.1)
                logger.info(f"Iteration {iteration + 1} response", response_len=len(response))

                # Parse reasoning and action from response
                thought, action, action_input = self._parse_response(response)

                step = {
                    "iteration": iteration + 1,
                    "thought": thought,
                    "action": action,
                    "action_input": action_input,
                }

                # Execute tool if action specified
                if action and action in self.tools:
                    tool = self.tools[action]
                    observation = await tool.execute(**action_input)
                    step["observation"] = observation

                    # Extract proposals if action was propose_action
                    if action == "propose_action" and observation.get("success"):
                        proposals.append(
                            {
                                "action_id": observation.get("action_id"),
                                "status": observation.get("status"),
                                "risk_level": action_input.get("risk_level"),
                            }
                        )

                    # Collect evidence from scans and queries
                    if action in ["scan_environment", "query_threat_intel"]:
                        if observation.get("success"):
                            evidence.append(
                                {
                                    "source": action,
                                    "data": observation,
                                }
                            )

                    # Update prompt with observation for next iteration
                    prompt += f"\n\nObservation: {json.dumps(observation)}\n\nThought:"

                else:
                    # No valid action - consider it final answer
                    step["observation"] = "No valid action found. Concluding."
                    steps.append(step)
                    break

                steps.append(step)

            # Generate summary from final state
            summary = self._generate_summary(steps, proposals, evidence)

            # Calculate confidence based on evidence and completed steps
            confidence = self._calculate_confidence(steps, evidence, proposals)

            logger.info(
                "ReAct agent completed",
                steps_count=len(steps),
                proposals_count=len(proposals),
                confidence=confidence,
            )

            return AgentResponse(
                summary=summary,
                steps=steps,
                proposals=proposals if proposals else None,
                evidence=evidence if evidence else None,
                confidence=confidence,
            )

        except Exception as e:
            logger.error("ReAct agent execution failed", error=str(e))
            return AgentResponse(
                summary=f"Agent execution failed: {str(e)}",
                steps=steps,
                proposals=None,
                evidence=None,
                confidence=0.0,
            )

    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for the prompt."""
        descriptions = []
        for name, tool in self.tools.items():
            params = tool.get_parameters()
            descriptions.append(f"- {name}: {tool.description}")
            descriptions.append(f"  Parameters: {json.dumps(params, indent=2)}")
        return "\n".join(descriptions)

    def _build_prompt(self, instruction: str, mode: str, tool_descriptions: str) -> str:
        """Build the initial ReAct prompt."""
        return f"""You are a cybersecurity AI agent using the ReAct (Reasoning + Acting) framework.

Your task: {instruction}

Mode: {mode} (passive = read-only operations, active = may include network changes)

Available tools:
{tool_descriptions}

IMPORTANT RULES:
1. Always start with passive, low-risk operations (scan_environment, query_threat_intel)
2. For high-risk actions, use propose_action which requires human approval
3. Format your response as:
   Thought: <your reasoning>
   Action: <tool_name>
   Action Input: <valid JSON parameters>

4. If no action needed, just provide:
   Thought: <final reasoning>
   Answer: <final answer>

Begin! Analyze the task and decide on your first action.

Thought:"""

    def _parse_response(self, response: str) -> tuple[str, str | None, dict[str, Any]]:
        """
        Parse model response into thought, action, and action input.

        Returns:
            Tuple of (thought, action_name, action_input_dict)
        """
        thought = ""
        action = None
        action_input = {}

        lines = response.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                current_section = "thought"
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                current_section = "action"
                action = line[7:].strip()
            elif line.startswith("Action Input:"):
                current_section = "action_input"
                input_text = line[13:].strip()
                try:
                    action_input = json.loads(input_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse action input", input_text=input_text)
                    action_input = {}
            elif line.startswith("Answer:"):
                # Final answer - no action needed
                current_section = "answer"
                action = None
            elif current_section == "thought":
                thought += " " + line
            elif current_section == "action_input":
                try:
                    action_input = json.loads(line)
                except json.JSONDecodeError:
                    pass

        return thought.strip(), action, action_input

    def _generate_summary(
        self, steps: list[dict], proposals: list[dict], evidence: list[dict]
    ) -> str:
        """Generate a summary of the agent execution."""
        summary_parts = [f"Completed {len(steps)} reasoning steps."]

        if evidence:
            summary_parts.append(f"Gathered {len(evidence)} pieces of evidence.")

        if proposals:
            summary_parts.append(f"Generated {len(proposals)} action proposals requiring approval.")

        # Extract key findings from evidence
        findings = []
        for ev in evidence:
            if ev["source"] == "scan_environment":
                data = ev["data"]
                if "findings" in data:
                    findings.append(f"Found {len(data['findings'])} items in scan")

        if findings:
            summary_parts.extend(findings)

        return " ".join(summary_parts)

    def _calculate_confidence(
        self, steps: list[dict], evidence: list[dict], proposals: list[dict]
    ) -> float:
        """
        Calculate confidence score based on execution quality.

        Factors:
        - Completed steps
        - Evidence collected
        - Successful observations
        """
        if not steps:
            return 0.0

        # Base confidence from completed steps
        confidence = min(len(steps) / self.max_iterations, 1.0) * 0.4

        # Bonus for evidence collected
        if evidence:
            confidence += min(len(evidence) / 2, 0.3)

        # Bonus for successful observations
        successful_steps = sum(
            1 for step in steps if step.get("observation", {}).get("success", False)
        )
        confidence += (successful_steps / len(steps)) * 0.3

        return min(confidence, 1.0)


async def run_agent(req: AgentRequest) -> AgentResponse:
    """
    Convenience function to run the ReAct agent with default configuration.

    Args:
        req: Agent request with instruction and settings

    Returns:
        Agent response with results
    """
    # Import tools dynamically to avoid circular imports
    from src.services.chroma import ChromaService
    from src.services.telegram import TelegramService
    from src.tools.propose_action import ProposeActionTool
    from src.tools.query_threat_intel import QueryThreatIntelTool
    from src.tools.scan_environment import ScanEnvironmentTool

    # Initialize services
    chroma_service = ChromaService()
    telegram_service = TelegramService()

    # Initialize tools
    tools = {
        "scan_environment": ScanEnvironmentTool(),
        "query_threat_intel": QueryThreatIntelTool(chroma_service),
        "propose_action": ProposeActionTool(telegram_service),
    }

    # Create model and agent
    model = OllamaModel()
    agent = ReactAgent(model, tools, max_iterations=2, max_exec_time=45)

    try:
        return await agent.run(req)
    finally:
        await model.close()

"""
Unit tests for the advanced memory systems.
"""

import tempfile
from pathlib import Path

import pytest

from src.memory import (
    EpisodicMemory,
    MemorySystem,
    ProceduralMemory,
    SemanticMemory,
    WorkingMemory,
)


class TestEpisodicMemory:
    """Test cases for Episodic Memory."""

    @pytest.mark.asyncio
    async def test_add_memory(self):
        """Test adding a memory."""
        memory = EpisodicMemory()

        memory_id = await memory.add_memory(
            content={"query": "What is XSS?", "response": "Cross-site scripting..."},
            metadata={"user": "analyst1"},
        )

        assert memory_id is not None
        assert len(memory) == 1

    @pytest.mark.asyncio
    async def test_recall_similar(self):
        """Test recalling similar memories."""
        memory = EpisodicMemory()

        await memory.add_memory(
            content={"query": "What is SQL injection?", "response": "SQL injection is..."}
        )
        await memory.add_memory(
            content={"query": "How to prevent XSS?", "response": "XSS prevention..."}
        )
        await memory.add_memory(
            content={"query": "Explain SQL injection attacks", "response": "SQL attacks..."}
        )

        similar = await memory.recall_similar("SQL injection", k=2)

        assert len(similar) > 0
        assert any("SQL" in str(m["content"]) for m in similar)

    @pytest.mark.asyncio
    async def test_get_recent(self):
        """Test getting recent memories."""
        memory = EpisodicMemory()

        for i in range(5):
            await memory.add_memory(content={"query": f"Query {i}", "response": f"Response {i}"})

        recent = await memory.get_recent(n=3)

        assert len(recent) == 3

    @pytest.mark.asyncio
    async def test_save_and_load(self):
        """Test saving and loading memories."""
        memory = EpisodicMemory()

        await memory.add_memory(content={"query": "Test query", "response": "Test response"})

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "episodic.json"
            await memory.save(filepath)

            # Load into new instance
            new_memory = EpisodicMemory()
            await new_memory.load(filepath)

            assert len(new_memory) == 1


class TestSemanticMemory:
    """Test cases for Semantic Memory."""

    @pytest.mark.asyncio
    async def test_add_concept(self):
        """Test adding a concept."""
        memory = SemanticMemory()

        await memory.add_concept(
            concept="SQL injection is a code injection technique",
            metadata={"category": "vulnerability"},
        )

        assert len(memory) == 1

    @pytest.mark.asyncio
    async def test_query(self):
        """Test querying concepts."""
        memory = SemanticMemory()

        await memory.add_concept(
            "SQL injection exploits database vulnerabilities", metadata={"category": "red-team"}
        )
        await memory.add_concept(
            "XSS allows script injection in web pages", metadata={"category": "red-team"}
        )

        results = await memory.query("SQL database", k=2)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_get_by_category(self):
        """Test getting concepts by category."""
        memory = SemanticMemory()

        await memory.add_concept("Nmap for network scanning", metadata={"category": "red-team"})
        await memory.add_concept(
            "Snort for intrusion detection", metadata={"category": "blue-team"}
        )

        red_team = await memory.get_by_category("red-team")

        assert len(red_team) == 1
        assert "Nmap" in red_team[0]["text"]


class TestProceduralMemory:
    """Test cases for Procedural Memory."""

    @pytest.mark.asyncio
    async def test_add_procedure(self):
        """Test adding a procedure."""
        memory = ProceduralMemory()

        procedure_id = await memory.add_procedure(
            name="Basic Reconnaissance",
            steps=["Identify target", "Gather OSINT", "Perform network scan", "Analyze results"],
            category="red-team",
        )

        assert procedure_id is not None
        assert len(memory) == 1

    @pytest.mark.asyncio
    async def test_get_procedure(self):
        """Test getting a procedure."""
        memory = ProceduralMemory()

        await memory.add_procedure(
            name="Incident Response",
            steps=["Detect", "Contain", "Eradicate", "Recover"],
            category="blue-team",
        )

        procedure = await memory.get_procedure("Incident Response")

        assert procedure is not None
        assert len(procedure["steps"]) == 4

    @pytest.mark.asyncio
    async def test_find_procedures(self):
        """Test finding procedures."""
        memory = ProceduralMemory()

        await memory.add_procedure(
            name="SQL Injection Testing",
            steps=["Find input", "Test payload", "Extract data"],
            category="red-team",
        )
        await memory.add_procedure(
            name="WAF Configuration",
            steps=["Install WAF", "Configure rules", "Test protection"],
            category="blue-team",
        )

        results = await memory.find_procedures("SQL injection", k=5)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_save_and_load(self):
        """Test saving and loading procedures."""
        memory = ProceduralMemory()

        await memory.add_procedure(
            name="Test Procedure", steps=["Step 1", "Step 2"], category="test"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "procedural.json"
            await memory.save(filepath)

            new_memory = ProceduralMemory()
            await new_memory.load(filepath)

            assert len(new_memory) == 1


class TestWorkingMemory:
    """Test cases for Working Memory."""

    def test_add_and_get(self):
        """Test adding and getting items."""
        memory = WorkingMemory(capacity=5)

        memory.add("current_task", "Analyze logs")
        memory.add("threat_level", "high")

        assert memory.get("current_task") == "Analyze logs"
        assert memory.get("threat_level") == "high"

    def test_lru_eviction(self):
        """Test LRU eviction when capacity exceeded."""
        memory = WorkingMemory(capacity=3)

        memory.add("key1", "value1")
        memory.add("key2", "value2")
        memory.add("key3", "value3")
        memory.add("key4", "value4")  # Should evict key1

        assert memory.get("key1") is None
        assert memory.get("key4") == "value4"

    def test_clear(self):
        """Test clearing working memory."""
        memory = WorkingMemory()

        memory.add("key1", "value1")
        memory.add("key2", "value2")

        memory.clear()

        assert len(memory) == 0

    def test_get_all(self):
        """Test getting all items."""
        memory = WorkingMemory()

        memory.add("key1", "value1")
        memory.add("key2", "value2")

        all_items = memory.get_all()

        assert len(all_items) == 2
        assert "key1" in all_items


class TestMemorySystem:
    """Test cases for integrated Memory System."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test memory system initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = MemorySystem(persistence_path=tmpdir)
            await system.initialize()

            assert system.initialized
            assert system.episodic is not None
            assert system.semantic is not None
            assert system.procedural is not None
            assert system.working is not None

    @pytest.mark.asyncio
    async def test_add_interaction(self):
        """Test adding an interaction."""
        system = MemorySystem()
        await system.initialize()

        await system.add_interaction(
            query="What is SQL injection?",
            response="SQL injection is a code injection technique...",
            context={"severity": "high"},
        )

        assert len(system.episodic) == 1

    @pytest.mark.asyncio
    async def test_add_procedure(self):
        """Test adding a procedure."""
        system = MemorySystem()
        await system.initialize()

        await system.add_procedure(
            name="Test Procedure", steps=["Step 1", "Step 2"], category="test"
        )

        assert len(system.procedural) == 1

    @pytest.mark.asyncio
    async def test_working_memory_operations(self):
        """Test working memory operations."""
        system = MemorySystem()
        await system.initialize()

        system.add_to_working_memory("current_task", "Scan network")

        assert system.get_from_working_memory("current_task") == "Scan network"

    @pytest.mark.asyncio
    async def test_get_context_for_reasoning(self):
        """Test getting context for reasoning."""
        system = MemorySystem()
        await system.initialize()

        # Add some memories
        await system.add_interaction(query="What is XSS?", response="Cross-site scripting...")
        await system.add_concept("XSS is a web vulnerability")
        system.add_to_working_memory("task", "Security analysis")

        context = await system.get_context_for_reasoning("XSS attack", max_items=10)

        assert "similar_interactions" in context
        assert "relevant_knowledge" in context
        assert "relevant_procedures" in context
        assert "working_memory" in context

    @pytest.mark.asyncio
    async def test_save_and_load_persistence(self):
        """Test saving and loading persistent memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate system
            system = MemorySystem(persistence_path=tmpdir)
            await system.initialize()

            await system.add_interaction(query="Test query", response="Test response")
            await system.add_procedure(name="Test Procedure", steps=["Step 1"], category="test")

            # Save
            await system.save_persistent_memories()

            # Create new system and load
            new_system = MemorySystem(persistence_path=tmpdir)
            await new_system.initialize()

            assert len(new_system.episodic) == 1
            assert len(new_system.procedural) == 1

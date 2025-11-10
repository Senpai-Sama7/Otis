#!/usr/bin/env python3
"""Initialize RAG data with MITRE ATT&CK, NIST, and OWASP knowledge."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

from src.core.config import get_settings
from src.core.logging import configure_logging, get_logger
from src.services.chroma import ChromaService

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


async def download_mitre_attack() -> list[dict]:
    """Download MITRE ATT&CK framework data."""
    logger.info("Downloading MITRE ATT&CK data")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(settings.mitre_attack_url)
            response.raise_for_status()
            data = response.json()

            techniques = []
            for obj in data.get("objects", []):
                if obj.get("type") == "attack-pattern":
                    kill_chain_phases = obj.get("kill_chain_phases", [])
                    if kill_chain_phases and isinstance(kill_chain_phases, list) and "phase_name" in kill_chain_phases[0]:
                        tactic = ", ".join(kill_chain_phases[0].get("phase_name", "").split("-"))
                    else:
                        tactic = ""
                    techniques.append({
                        "id": obj.get("external_references", [{}])[0].get("external_id", ""),
                        "name": obj.get("name", ""),
                        "description": obj.get("description", ""),
                        "tactic": tactic,
                    })

            logger.info("Downloaded MITRE ATT&CK techniques", count=len(techniques))
            return techniques
    except Exception as e:
        logger.error("Failed to download MITRE ATT&CK", error=str(e))
        return []


def get_nist_data() -> list[dict]:
    """Get NIST Cybersecurity Framework data."""
    logger.info("Loading NIST CSF data")

    # Simplified NIST CSF core functions
    nist_data = [
        {
            "id": "NIST-ID",
            "name": "Identify",
            "description": "Develop organizational understanding to manage cybersecurity risk to systems, people, assets, data, and capabilities.",
        },
        {
            "id": "NIST-PR",
            "name": "Protect",
            "description": "Develop and implement appropriate safeguards to ensure delivery of critical services.",
        },
        {
            "id": "NIST-DE",
            "name": "Detect",
            "description": "Develop and implement appropriate activities to identify the occurrence of a cybersecurity event.",
        },
        {
            "id": "NIST-RS",
            "name": "Respond",
            "description": "Develop and implement appropriate activities to take action regarding a detected cybersecurity incident.",
        },
        {
            "id": "NIST-RC",
            "name": "Recover",
            "description": "Develop and implement appropriate activities to maintain plans for resilience and to restore any capabilities or services that were impaired due to a cybersecurity incident.",
        },
    ]

    logger.info("Loaded NIST CSF functions", count=len(nist_data))
    return nist_data


def get_owasp_data() -> list[dict]:
    """Get OWASP Top 10 data."""
    logger.info("Loading OWASP Top 10 data")

    owasp_data = [
        {
            "id": "A01:2021",
            "name": "Broken Access Control",
            "description": "Restrictions on what authenticated users are allowed to do are often not properly enforced.",
        },
        {
            "id": "A02:2021",
            "name": "Cryptographic Failures",
            "description": "Failures related to cryptography which often lead to exposure of sensitive data.",
        },
        {
            "id": "A03:2021",
            "name": "Injection",
            "description": "Application is vulnerable to injection attacks when user-supplied data is not validated, filtered, or sanitized.",
        },
        {
            "id": "A04:2021",
            "name": "Insecure Design",
            "description": "Risks related to design and architectural flaws, calling for more use of threat modeling, secure design patterns, and reference architectures.",
        },
        {
            "id": "A05:2021",
            "name": "Security Misconfiguration",
            "description": "Missing appropriate security hardening across any part of the application stack or improperly configured permissions.",
        },
        {
            "id": "A06:2021",
            "name": "Vulnerable and Outdated Components",
            "description": "Using components with known vulnerabilities or that are out of date or unsupported.",
        },
        {
            "id": "A07:2021",
            "name": "Identification and Authentication Failures",
            "description": "Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks.",
        },
        {
            "id": "A08:2021",
            "name": "Software and Data Integrity Failures",
            "description": "Code and infrastructure that does not protect against integrity violations.",
        },
        {
            "id": "A09:2021",
            "name": "Security Logging and Monitoring Failures",
            "description": "Without logging and monitoring, breaches cannot be detected.",
        },
        {
            "id": "A10:2021",
            "name": "Server-Side Request Forgery (SSRF)",
            "description": "SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL.",
        },
    ]

    logger.info("Loaded OWASP Top 10", count=len(owasp_data))
    return owasp_data


async def ingest_data():
    """Ingest all data into Chroma."""
    logger.info("Starting RAG data ingestion")

    chroma_service = ChromaService()

    # Download MITRE data
    mitre_data = await download_mitre_attack()

    # Get NIST and OWASP data
    nist_data = get_nist_data()
    owasp_data = get_owasp_data()

    # Prepare documents and metadata
    documents = []
    metadatas = []
    ids = []

    # Add MITRE techniques
    for i, technique in enumerate(mitre_data[:100]):  # Limit to first 100 for demo
        documents.append(f"{technique['name']}: {technique['description']}")
        metadatas.append({
            "source": "MITRE",
            "category": "attack_pattern",
            "external_id": technique['id'],
            "name": technique['name'],
        })
        ids.append(f"mitre_{i}")

    # Add NIST functions
    for i, function in enumerate(nist_data):
        documents.append(f"{function['name']}: {function['description']}")
        metadatas.append({
            "source": "NIST",
            "category": "framework",
            "external_id": function['id'],
            "name": function['name'],
        })
        ids.append(f"nist_{i}")

    # Add OWASP Top 10
    for i, item in enumerate(owasp_data):
        documents.append(f"{item['name']}: {item['description']}")
        metadatas.append({
            "source": "OWASP",
            "category": "vulnerability",
            "external_id": item['id'],
            "name": item['name'],
        })
        ids.append(f"owasp_{i}")

    # Ingest into Chroma
    logger.info("Ingesting documents into Chroma", total_documents=len(documents))
    chroma_service.add_documents(documents, metadatas, ids)

    logger.info("RAG data ingestion completed", total_documents=len(documents))
    logger.info("Collection count", count=chroma_service.get_collection_count())


if __name__ == "__main__":
    asyncio.run(ingest_data())

#!/usr/bin/env python3
"""Build RAG knowledge base from cybersecurity sources."""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import httpx
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def download_mitre_attack() -> List[Dict[str, Any]]:
    """Download and parse MITRE ATT&CK framework data."""
    logger.info("Downloading MITRE ATT&CK data...")

    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

    try:
        response = httpx.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        documents = []
        objects = data.get("objects", [])

        for obj in objects:
            obj_type = obj.get("type")

            if obj_type == "attack-pattern":
                # Extract technique information
                name = obj.get("name", "Unknown")
                description = obj.get("description", "")
                technique_id = obj.get("external_references", [{}])[0].get(
                    "external_id", "Unknown"
                )

                if description:
                    documents.append(
                        {
                            "id": f"mitre_{technique_id}",
                            "content": f"{name} ({technique_id}): {description}",
                            "metadata": {
                                "source": "MITRE",
                                "category": "attack_pattern",
                                "technique_id": technique_id,
                                "name": name,
                            },
                        }
                    )

        logger.info(f"Downloaded {len(documents)} MITRE ATT&CK techniques")
        return documents

    except Exception as e:
        logger.error(f"Failed to download MITRE ATT&CK: {e}")
        return []


def create_nist_csf_docs() -> List[Dict[str, Any]]:
    """Create NIST Cybersecurity Framework documents."""
    logger.info("Creating NIST CSF documentation...")

    # NIST CSF Core Functions and Categories
    nist_data = {
        "Identify": [
            "Asset Management: Identify physical devices, systems, data, and organizational roles",
            "Business Environment: Understand the organization's mission and stakeholders",
            "Governance: Establish policies to manage cybersecurity risk",
            "Risk Assessment: Identify and analyze cybersecurity risks",
            "Risk Management Strategy: Establish risk tolerance and priorities",
        ],
        "Protect": [
            "Access Control: Limit access to authorized users and processes",
            "Awareness and Training: Educate personnel on cybersecurity",
            "Data Security: Protect data confidentiality, integrity, and availability",
            "Protective Technology: Implement technical security controls",
        ],
        "Detect": [
            "Anomalies and Events: Detect anomalous activity",
            "Security Continuous Monitoring: Monitor systems continuously",
            "Detection Processes: Implement detection processes and procedures",
        ],
        "Respond": [
            "Response Planning: Execute response processes",
            "Communications: Coordinate response activities",
            "Analysis: Analyze detected events",
            "Mitigation: Contain and mitigate incidents",
            "Improvements: Improve response capabilities",
        ],
        "Recover": [
            "Recovery Planning: Execute recovery processes",
            "Improvements: Improve recovery capabilities",
            "Communications: Coordinate recovery activities",
        ],
    }

    documents = []
    for function, categories in nist_data.items():
        for i, category in enumerate(categories):
            documents.append(
                {
                    "id": f"nist_{function.lower()}_{i}",
                    "content": f"NIST CSF {function} - {category}",
                    "metadata": {
                        "source": "NIST",
                        "category": "framework",
                        "function": function,
                    },
                }
            )

    logger.info(f"Created {len(documents)} NIST CSF documents")
    return documents


def create_owasp_top10_docs() -> List[Dict[str, Any]]:
    """Create OWASP Top 10 documents."""
    logger.info("Creating OWASP Top 10 documentation...")

    owasp_top10 = [
        {
            "id": "A01",
            "name": "Broken Access Control",
            "description": "Failures related to access control that allow unauthorized access",
        },
        {
            "id": "A02",
            "name": "Cryptographic Failures",
            "description": "Failures related to cryptography which may lead to data exposure",
        },
        {
            "id": "A03",
            "name": "Injection",
            "description": "SQL, NoSQL, OS, and LDAP injection vulnerabilities",
        },
        {
            "id": "A04",
            "name": "Insecure Design",
            "description": "Flaws in design and architecture that create security weaknesses",
        },
        {
            "id": "A05",
            "name": "Security Misconfiguration",
            "description": "Insecure default configurations, incomplete setups, or exposed cloud storage",
        },
        {
            "id": "A06",
            "name": "Vulnerable and Outdated Components",
            "description": "Using components with known vulnerabilities",
        },
        {
            "id": "A07",
            "name": "Identification and Authentication Failures",
            "description": "Failures in authentication and session management",
        },
        {
            "id": "A08",
            "name": "Software and Data Integrity Failures",
            "description": "Code and infrastructure that does not protect against integrity violations",
        },
        {
            "id": "A09",
            "name": "Security Logging and Monitoring Failures",
            "description": "Insufficient logging, detection, monitoring, and response",
        },
        {
            "id": "A10",
            "name": "Server-Side Request Forgery (SSRF)",
            "description": "SSRF flaws that allow attackers to send crafted requests",
        },
    ]

    documents = []
    for item in owasp_top10:
        documents.append(
            {
                "id": f"owasp_{item['id'].lower()}",
                "content": f"OWASP Top 10 {item['id']}: {item['name']} - {item['description']}",
                "metadata": {
                    "source": "OWASP",
                    "category": "top10",
                    "vulnerability_id": item["id"],
                    "name": item["name"],
                },
            }
        )

    logger.info(f"Created {len(documents)} OWASP Top 10 documents")
    return documents


def build_chroma_index(documents: List[Dict[str, Any]], persist_directory: str) -> bool:
    """Build Chroma vector store index."""
    logger.info("Building Chroma index...")

    try:
        import chromadb
        from chromadb.utils import embedding_functions

        # Create persist directory
        persist_path = Path(persist_directory)
        persist_path.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client with persistence
        client = chromadb.PersistentClient(path=str(persist_path))

        # Use sentence-transformers embedding function
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get or create collection
        try:
            collection = client.get_collection(
                name="cybersecurity_knowledge", embedding_function=embedding_function
            )
            # Delete existing collection to rebuild
            client.delete_collection(name="cybersecurity_knowledge")
            logger.info("Deleted existing collection")
        except Exception:
            pass

        collection = client.create_collection(
            name="cybersecurity_knowledge",
            embedding_function=embedding_function,
            metadata={"description": "Cybersecurity knowledge base with MITRE, NIST, OWASP"},
        )

        # Add documents in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            ids = [doc["id"] for doc in batch]
            contents = [doc["content"] for doc in batch]
            metadatas = [doc["metadata"] for doc in batch]

            collection.add(documents=contents, metadatas=metadatas, ids=ids)

            logger.info(f"Added batch {i // batch_size + 1} ({len(batch)} documents)")

        logger.info(f"✅ Successfully built Chroma index with {len(documents)} documents")
        logger.info(f"📁 Persisted to: {persist_path.absolute()}")

        return True

    except Exception as e:
        logger.error(f"Failed to build Chroma index: {e}")
        return False


def main():
    """Main function to build RAG knowledge base."""
    logger.info("🚀 Starting RAG knowledge base build...")

    # Collect documents from all sources
    all_documents = []

    # MITRE ATT&CK
    mitre_docs = download_mitre_attack()
    all_documents.extend(mitre_docs)

    # NIST CSF
    nist_docs = create_nist_csf_docs()
    all_documents.extend(nist_docs)

    # OWASP Top 10
    owasp_docs = create_owasp_top10_docs()
    all_documents.extend(owasp_docs)

    logger.info(f"📊 Total documents collected: {len(all_documents)}")

    if not all_documents:
        logger.error("❌ No documents collected. Exiting.")
        sys.exit(1)

    # Build Chroma index
    persist_directory = "./data/chroma"
    success = build_chroma_index(all_documents, persist_directory)

    if success:
        logger.info("🎉 RAG knowledge base build complete!")
        sys.exit(0)
    else:
        logger.error("❌ RAG knowledge base build failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

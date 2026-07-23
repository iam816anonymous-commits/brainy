import os
from typing import List, Dict, Any
from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object
from brain.ingestion.filesystem.base_parser import BaseParser
from brain.ingestion.filesystem.python_parser import PythonParser
from brain.ingestion.filesystem.default_parser import DefaultParser

# Register pluggable language/file parsers
REGISTERED_PARSERS: List[BaseParser] = [
    PythonParser(),
    DefaultParser()  # should always be last as the fallback
]

def ingest_directory(directory_path: str, project_name: str) -> List[str]:
    """
    Recursively scans and ingests a folder into structured Project, Folder, File, Code KnowledgeObjects.
    Uses registered pluggable BaseParsers to parse deep inner-structures based on file extensions.
    """
    if not os.path.exists(directory_path):
        return []

    # 1. Create/Ensure Project node exists
    proj_id = f"project::{project_name.lower()}"
    proj_obj = KnowledgeObject(
        id=proj_id,
        type="Project",
        project=project_name,
        title=f"Project: {project_name}",
        summary=f"Ingested project directory: {directory_path}",
        content=f"Root path: {os.path.abspath(directory_path)}",
        importance=10.0,
        confidence=1.0,
        tags=["project", "root"],
        relations=[]
    )
    save_knowledge_object(proj_obj)

    ingested_ids = [proj_id]
    dir_to_id = {directory_path: proj_id}

    for root, dirs, files in os.walk(directory_path):
        # Ignore hidden/vcs directories and python cache
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        parent_id = dir_to_id.get(root, proj_id)

        # Ingest Subfolders
        for d in dirs:
            folder_path = os.path.join(root, d)
            rel_path = os.path.relpath(folder_path, directory_path)
            folder_id = f"folder::{project_name.lower()}::{rel_path}"
            dir_to_id[folder_path] = folder_id

            folder_obj = KnowledgeObject(
                id=folder_id,
                type="Folder",
                project=project_name,
                title=f"Folder {d}",
                summary=f"Subdirectory in {project_name}: {rel_path}",
                content=f"Relative path: {rel_path}",
                importance=4.0,
                confidence=1.0,
                tags=["folder", "module"],
                relations=[{"target": parent_id, "type": "part_of"}],
                source=folder_path
            )
            save_knowledge_object(folder_obj)
            ingested_ids.append(folder_id)

        # Ingest Files
        for f in files:
            if f.startswith("."):
                continue

            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, directory_path)
            file_id = f"file::{project_name.lower()}::{rel_path}"

            _, ext = os.path.splitext(f)
            doc_types = {".md": "Document", ".txt": "Document", ".json": "Document", ".yaml": "Document", ".yml": "Document"}
            file_type = doc_types.get(ext.lower(), "Code")

            content = ""
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file_handle:
                    content = file_handle.read()
            except Exception:
                pass

            summary = f"File {f} at relative path {rel_path}"
            if len(content) > 200:
                summary += f"\nSnippet: {content[:150]}..."

            file_obj = KnowledgeObject(
                id=file_id,
                type=file_type,
                project=project_name,
                title=f"File {f}",
                summary=summary,
                content=content,
                importance=3.0,
                confidence=1.0,
                tags=["file", ext.replace(".", "") or "unknown"],
                relations=[{"target": parent_id, "type": "part_of"}],
                source=file_path
            )

            # Match and execute pluggable parser
            for parser in REGISTERED_PARSERS:
                if parser.can_parse(file_path):
                    sub_objs = parser.parse(file_path, project_name, file_id)
                    for sub in sub_objs:
                        save_knowledge_object(sub)
                        ingested_ids.append(sub.id)
                        file_obj.relations.append({"target": sub.id, "type": "contains"})
                    break  # only execute the first matching parser

            save_knowledge_object(file_obj)
            ingested_ids.append(file_id)

    return ingested_ids

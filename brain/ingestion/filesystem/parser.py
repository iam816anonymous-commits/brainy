import os
import ast
import uuid
from typing import List, Dict, Any
from brain.storage.models import KnowledgeObject
from brain.storage.db import save_knowledge_object

def parse_python_file(filepath: str, project_name: str, file_obj_id: str) -> List[KnowledgeObject]:
    """
    Parses a python file using AST and extracts Classes, Functions, and Tests as KnowledgeObjects.
    """
    objs = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        # Ignore files we can't read
        return objs

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Code might be invalid or not Python, return empty or treat as standard Document/Code
        return objs

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_id = f"{file_obj_id}::class::{node.name}"
            # Extract docstring
            doc = ast.get_docstring(node) or ""

            # Count methods
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            summary = f"Class {node.name} containing methods: {', '.join(methods)}" if methods else f"Class {node.name}"

            class_obj = KnowledgeObject(
                id=class_id,
                type="Class",
                project=project_name,
                title=f"Class {node.name}",
                summary=summary,
                content=ast.unparse(node) if hasattr(ast, "unparse") else doc,
                importance=3.0,
                confidence=1.0,
                tags=["class", "python"],
                relations=[{"target": file_obj_id, "type": "part_of"}],
                source=filepath
            )
            objs.append(class_obj)

            # Parse class methods
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    sub_doc = ast.get_docstring(subnode) or ""
                    method_type = "Test" if subnode.name.startswith("test_") else "Function"
                    method_id = f"{class_id}::method::{subnode.name}"

                    method_obj = KnowledgeObject(
                        id=method_id,
                        type=method_type,
                        project=project_name,
                        title=f"Method {subnode.name}",
                        summary=sub_doc or f"Method {subnode.name} of class {node.name}",
                        content=ast.unparse(subnode) if hasattr(ast, "unparse") else sub_doc,
                        importance=2.0 if method_type == "Function" else 1.0,
                        confidence=1.0,
                        tags=[method_type.lower(), "python"],
                        relations=[{"target": class_id, "type": "belongs_to"}],
                        source=filepath
                    )
                    objs.append(method_obj)
                    # Link parent class to method as well
                    class_obj.relations.append({"target": method_id, "type": "contains_method"})

        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node) or ""
            func_type = "Test" if node.name.startswith("test_") else "Function"
            func_id = f"{file_obj_id}::function::{node.name}"

            func_obj = KnowledgeObject(
                id=func_id,
                type=func_type,
                project=project_name,
                title=f"Function {node.name}",
                summary=func_doc or f"Top-level function {node.name}",
                content=ast.unparse(node) if hasattr(ast, "unparse") else func_doc,
                importance=2.0 if func_type == "Function" else 1.0,
                confidence=1.0,
                tags=[func_type.lower(), "python"],
                relations=[{"target": file_obj_id, "type": "part_of"}],
                source=filepath
            )
            objs.append(func_obj)

    return objs

def ingest_directory(directory_path: str, project_name: str) -> List[str]:
    """
    Recursively scans and ingests a folder into structured Project, Folder, File, Code KnowledgeObjects.
    """
    if not os.path.exists(directory_path):
        return []

    # 1. Create/Ensure Project node exists
    proj_id = f"project::{project_name}"
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

    # Map paths to their respective knowledge object IDs so we can form accurate hierarchy
    dir_to_id = {directory_path: proj_id}

    for root, dirs, files in os.walk(directory_path):
        # Ignore hidden/vcs directories and python cache
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        parent_id = dir_to_id.get(root, proj_id)

        # Ingest Subfolders
        for d in dirs:
            folder_path = os.path.join(root, d)
            rel_path = os.path.relpath(folder_path, directory_path)
            folder_id = f"folder::{project_name}::{rel_path}"
            dir_to_id[folder_path] = folder_id

            folder_obj = KnowledgeObject(
                id=folder_id,
                type="Folder",  # Folder/Module
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
            # Skip hidden files
            if f.startswith("."):
                continue

            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, directory_path)
            file_id = f"file::{project_name}::{rel_path}"

            # Determine type based on extension
            _, ext = os.path.splitext(f)
            doc_types = {".md": "Document", ".txt": "Document", ".json": "Document", ".yaml": "Document", ".yml": "Document"}
            file_type = doc_types.get(ext.lower(), "Code")

            # Read snippet or complete content
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

            # If it's a Python file, parse its internal structure
            if ext.lower() == ".py":
                sub_objs = parse_python_file(file_path, project_name, file_id)
                for sub in sub_objs:
                    save_knowledge_object(sub)
                    ingested_ids.append(sub.id)
                    # Relate python components to the file object
                    file_obj.relations.append({"target": sub.id, "type": "contains"})

            save_knowledge_object(file_obj)
            ingested_ids.append(file_id)

    return ingested_ids

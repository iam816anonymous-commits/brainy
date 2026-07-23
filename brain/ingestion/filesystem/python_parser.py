import os
import ast
from typing import List
from brain.ingestion.filesystem.base_parser import BaseParser
from brain.core.models import KnowledgeObject

class PythonParser(BaseParser):
    def can_parse(self, filepath: str) -> bool:
        return filepath.lower().endswith(".py")

    def parse(self, filepath: str, project_name: str, parent_id: str) -> List[KnowledgeObject]:
        objs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            return objs

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return objs

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_id = f"{parent_id}::class::{node.name}"
                doc = ast.get_docstring(node) or ""

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
                    relations=[{"target": parent_id, "type": "part_of"}],
                    source=filepath
                )
                objs.append(class_obj)

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
                        class_obj.relations.append({"target": method_id, "type": "contains_method"})

            elif isinstance(node, ast.FunctionDef):
                func_doc = ast.get_docstring(node) or ""
                func_type = "Test" if node.name.startswith("test_") else "Function"
                func_id = f"{parent_id}::function::{node.name}"

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
                    relations=[{"target": parent_id, "type": "part_of"}],
                    source=filepath
                )
                objs.append(func_obj)

        return objs

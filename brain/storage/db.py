import os
import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from brain.storage.models import KnowledgeObject, KnowledgeObjectRelation

DEFAULT_DB_PATH = "brain.db"

def get_db_path() -> str:
    return os.environ.get("BRAIN_DB_PATH", DEFAULT_DB_PATH)

def get_connection() -> sqlite3.Connection:
    path = get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Expanded Knowledge Objects Table with platform engineering fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_objects (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        project TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        content TEXT,
        importance REAL DEFAULT 1.0,
        confidence REAL DEFAULT 1.0,
        created TEXT,
        updated TEXT,
        tags TEXT,          -- JSON list
        relations TEXT,     -- JSON list

        -- Platform engineering fields
        lifecycle TEXT DEFAULT 'Created',
        source TEXT,
        owner TEXT,
        created_from TEXT,
        derived_from TEXT,
        verified_by TEXT,
        last_verified TEXT,
        visibility TEXT DEFAULT 'internal',
        permissions TEXT,   -- JSON dict
        group_name TEXT,    -- SQLite keyword group bypass
        metadata TEXT,      -- JSON dict
        payload TEXT        -- JSON dict
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relations (
        source_id TEXT,
        target_id TEXT,
        relation_type TEXT,
        PRIMARY KEY (source_id, target_id, relation_type)
    )
    """)

    conn.commit()
    conn.close()

def save_knowledge_object(obj: KnowledgeObject) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    tags_str = json.dumps(obj.tags)
    relations_str = json.dumps(obj.relations)
    permissions_str = json.dumps(obj.permissions)
    metadata_str = json.dumps(obj.metadata)
    payload_str = json.dumps(obj.payload)

    cursor.execute("""
    INSERT OR REPLACE INTO knowledge_objects (
        id, type, project, title, summary, content, importance, confidence, created, updated, tags, relations,
        lifecycle, source, owner, created_from, derived_from, verified_by, last_verified, visibility, permissions, group_name, metadata, payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        obj.id, obj.type, obj.project, obj.title, obj.summary, obj.content,
        obj.importance, obj.confidence, obj.created, obj.updated,
        tags_str, relations_str,
        obj.lifecycle, obj.source, obj.owner, obj.created_from, obj.derived_from,
        obj.verified_by, obj.last_verified, obj.visibility, permissions_str, obj.group, metadata_str, payload_str
    ))

    # Refresh explicit relations
    cursor.execute("DELETE FROM relations WHERE source_id = ?", (obj.id,))
    for rel in obj.relations:
        target = rel.get("target")
        rel_type = rel.get("type", "related_to")
        if target:
            cursor.execute("""
            INSERT OR IGNORE INTO relations (source_id, target_id, relation_type)
            VALUES (?, ?, ?)
            """, (obj.id, target, rel_type))

    conn.commit()
    conn.close()

def get_knowledge_object(obj_id: str) -> Optional[KnowledgeObject]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_objects WHERE id = ?", (obj_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # Helper to load JSON with fallback
    def load_json(val: Any, default: Any) -> Any:
        if not val:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

    tags = load_json(row["tags"], [])
    relations = load_json(row["relations"], [])
    permissions = load_json(row["permissions"], {})
    metadata = load_json(row["metadata"], {})
    payload = load_json(row["payload"], {})

    return KnowledgeObject(
        id=row["id"],
        type=row["type"],
        project=row["project"],
        title=row["title"],
        summary=row["summary"] or "",
        content=row["content"] or "",
        importance=row["importance"],
        confidence=row["confidence"],
        created=row["created"],
        updated=row["updated"],
        tags=tags,
        relations=relations,

        # Platform engineering loaded values
        lifecycle=row["lifecycle"] or "Created",
        source=row["source"] or "",
        owner=row["owner"] or "",
        created_from=row["created_from"] or "",
        derived_from=row["derived_from"] or "",
        verified_by=row["verified_by"] or "",
        last_verified=row["last_verified"] or "",
        visibility=row["visibility"] or "internal",
        permissions=permissions,
        group=row["group_name"] or "",
        metadata=metadata,
        payload=payload
    )

def delete_knowledge_object(obj_id: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_objects WHERE id = ?", (obj_id,))
    cursor.execute("DELETE FROM relations WHERE source_id = ? OR target_id = ?", (obj_id, obj_id))
    conn.commit()
    conn.close()

def list_knowledge_objects(project: Optional[str] = None, obj_type: Optional[str] = None) -> List[KnowledgeObject]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM knowledge_objects"
    params = []
    conditions = []

    if project:
        conditions.append("project = ?")
        params.append(project)
    if obj_type:
        conditions.append("type = ?")
        params.append(obj_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Helper to load JSON with fallback
    def load_json(val: Any, default: Any) -> Any:
        if not val:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

    results = []
    for row in rows:
        tags = load_json(row["tags"], [])
        relations = load_json(row["relations"], [])
        permissions = load_json(row["permissions"], {})
        metadata = load_json(row["metadata"], {})
        payload = load_json(row["payload"], {})

        results.append(KnowledgeObject(
            id=row["id"],
            type=row["type"],
            project=row["project"],
            title=row["title"],
            summary=row["summary"] or "",
            content=row["content"] or "",
            importance=row["importance"],
            confidence=row["confidence"],
            created=row["created"],
            updated=row["updated"],
            tags=tags,
            relations=relations,

            # Platform engineering fields
            lifecycle=row["lifecycle"] or "Created",
            source=row["source"] or "",
            owner=row["owner"] or "",
            created_from=row["created_from"] or "",
            derived_from=row["derived_from"] or "",
            verified_by=row["verified_by"] or "",
            last_verified=row["last_verified"] or "",
            visibility=row["visibility"] or "internal",
            permissions=permissions,
            group=row["group_name"] or "",
            metadata=metadata,
            payload=payload
        ))
    return results

def get_all_relations() -> List[KnowledgeObjectRelation]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM relations")
    rows = cursor.fetchall()
    conn.close()

    return [
        KnowledgeObjectRelation(
            source_id=row["source_id"],
            target_id=row["target_id"],
            relation_type=row["relation_type"]
        )
        for row in rows
    ]

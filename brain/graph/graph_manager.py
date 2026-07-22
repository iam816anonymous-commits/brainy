import networkx as nx
from typing import List, Dict, Any, Set, Tuple, Optional
from brain.storage.db import list_knowledge_objects, get_all_relations, get_knowledge_object
from brain.storage.models import KnowledgeObject

class KnowledgeGraphManager:
    def __init__(self, project_name: Optional[str] = None):
        self.project_name = project_name
        self.graph = nx.DiGraph()
        self.build_graph()

    def build_graph(self) -> None:
        """
        Loads knowledge objects and relations from SQLite and populates the networkx directed graph.
        """
        self.graph.clear()

        # Load nodes
        nodes = list_knowledge_objects(project=self.project_name)
        for node in nodes:
            self.graph.add_node(
                node.id,
                type=node.type,
                project=node.project,
                title=node.title,
                importance=node.importance,
                confidence=node.confidence,
                created=node.created,
                updated=node.updated,
                tags=node.tags,
                source=node.source,
                owner=node.owner
            )

        # Load explicit relations
        relations = get_all_relations()
        for rel in relations:
            # Only add if both nodes exist in our loaded scope
            if self.graph.has_node(rel.source_id) and self.graph.has_node(rel.target_id):
                self.graph.add_edge(rel.source_id, rel.target_id, type=rel.relation_type)

    def get_related_nodes(self, node_id: str, max_distance: int = 2) -> Set[str]:
        """
        Returns a set of node IDs that are within `max_distance` (number of edges)
        from `node_id` in either direction (treating graph as undirected for connection discovery).
        """
        if not self.graph.has_node(node_id):
            return set()

        # Convert to undirected to traverse both ways
        undirected_g = self.graph.to_undirected()

        lengths = nx.single_source_shortest_path_length(undirected_g, node_id, cutoff=max_distance)
        return set(lengths.keys())

    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Returns a dictionary representation of nodes and edges for the subgraph of `node_ids`.
        Useful for visualization and serialization.
        """
        sub_g = self.graph.subgraph(node_ids)

        nodes_list = []
        for n, attrs in sub_g.nodes(data=True):
            nodes_list.append({
                "id": n,
                "type": attrs.get("type"),
                "project": attrs.get("project"),
                "title": attrs.get("title"),
                "importance": attrs.get("importance")
            })

        edges_list = []
        for u, v, attrs in sub_g.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "type": attrs.get("type", "related_to")
            })

        return {
            "nodes": nodes_list,
            "edges": edges_list
        }

    def get_all_paths(self, source_id: str, target_id: str) -> List[List[str]]:
        """
        Returns all simple paths from source to target.
        """
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return []
        try:
            return list(nx.all_simple_paths(self.graph, source_id, target_id))
        except Exception:
            return []

    def get_incoming_relations(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Returns incoming relations as a list of (source_id, relation_type)
        """
        if not self.graph.has_node(node_id):
            return []
        rels = []
        for u, v, attrs in self.graph.in_edges(node_id, data=True):
            rels.append((u, attrs.get("type", "related_to")))
        return rels

    def get_outgoing_relations(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Returns outgoing relations as a list of (target_id, relation_type)
        """
        if not self.graph.has_node(node_id):
            return []
        rels = []
        for u, v, attrs in self.graph.out_edges(node_id, data=True):
            rels.append((v, attrs.get("type", "related_to")))
        return rels

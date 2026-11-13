"""
SkillBridge AI - Skill Dependency Intelligence Service
Builds Directed Acyclic Graphs (DAG) of skill prerequisites, detects cycles,
computes topological learning sequences, and resolves missing prerequisites.
"""

from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any

class SkillDependencyGraph:
    def __init__(self, taxonomy: Dict[str, Any] = None):
        self.taxonomy = taxonomy or {}
        self.adj = defaultdict(set) # skill -> set of direct prerequisites
        self.reverse_adj = defaultdict(set) # prerequisite -> skills that depend on it
        self._build_graph()

    def _build_graph(self):
        for skill_name, info in self.taxonomy.items():
            prereqs = info.get("prerequisites", [])
            for p in prereqs:
                self.adj[skill_name].add(p)
                self.reverse_adj[p].add(skill_name)

    def detect_cycles(self) -> Tuple[bool, List[str]]:
        """
        Detects if there is any cycle in the dependency graph using DFS 3-coloring.
        Returns (has_cycle: bool, cycle_path: List[str]).
        """
        visited = {} # 0: unvisited, 1: visiting, 2: visited
        parent = {}
        all_nodes = set(self.taxonomy.keys()).union(self.adj.keys())

        for node in all_nodes:
            visited[node] = 0

        cycle_path = []

        def dfs(u):
            visited[u] = 1
            for v in self.adj.get(u, []):
                if visited.get(v, 0) == 1: # Back-edge found -> cycle!
                    curr = u
                    cycle_path.append(v)
                    while curr != v and curr in parent:
                        cycle_path.append(curr)
                        curr = parent[curr]
                    cycle_path.append(v)
                    cycle_path.reverse()
                    return True
                elif visited.get(v, 0) == 0:
                    parent[v] = u
                    if dfs(v):
                        return True
            visited[u] = 2
            return False

        for node in all_nodes:
            if visited[node] == 0:
                if dfs(node):
                    return True, cycle_path

        return False, []

    def get_missing_prerequisites(self, target_skill: str, acquired_skills: Set[str]) -> List[Dict[str, str]]:
        """
        Recursively discovers all missing prerequisites for a given target skill
        that the user has not yet acquired.
        """
        missing = []
        visited = set()

        def traverse(skill):
            for prereq in self.adj.get(skill, []):
                if prereq not in visited:
                    visited.add(prereq)
                    if prereq not in acquired_skills:
                        missing.append({
                            "prerequisite": prereq,
                            "for_skill": skill,
                            "reason": f"'{prereq}' is foundational to understanding and applying '{skill}' effectively."
                        })
                    # Recurse up the chain
                    traverse(prereq)

        traverse(target_skill)
        return missing

    def get_optimal_learning_sequence(self, skills_to_learn: List[str]) -> List[str]:
        """
        Topological sort of skills to learn plus their required dependencies.
        Ensures foundational skills always precede advanced applications.
        """
        # Expand skill set to include all upstream prerequisites
        required_nodes = set(skills_to_learn)
        queue = deque(skills_to_learn)
        while queue:
            curr = queue.popleft()
            for p in self.adj.get(curr, []):
                if p not in required_nodes:
                    required_nodes.add(p)
                    queue.append(p)

        # Compute in-degree within the required subgraph
        in_degree = {node: 0 for node in required_nodes}
        for node in required_nodes:
            for p in self.adj.get(node, []):
                if p in required_nodes:
                    in_degree[node] += 1

        # Kahn's algorithm
        zero_in = deque([node for node, deg in in_degree.items() if deg == 0])
        ordered = []

        while zero_in:
            u = zero_in.popleft()
            ordered.append(u)
            for v in self.reverse_adj.get(u, []):
                if v in required_nodes:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        zero_in.append(v)

        return ordered

    def get_dependency_tree(self) -> List[Dict[str, Any]]:
        """Returns structured nodes and links for frontend diagram/visualization."""
        nodes = []
        links = []
        for name, info in self.taxonomy.items():
            nodes.append({
                "id": name,
                "category": info.get("category", "General"),
                "domain": info.get("domain", "Core"),
                "importance": info.get("importance", "Medium")
            })
            for p in info.get("prerequisites", []):
                links.append({
                    "source": p,
                    "target": name,
                    "type": "prerequisite"
                })
        return {"nodes": nodes, "links": links}

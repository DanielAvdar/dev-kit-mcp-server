"""Semantic search tool for finding relevant code and documentation."""

import os
from typing import Any, Dict, Optional, cast

from fastmcp import Context

from .utils import get_file_contents


def semantic_search(query: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Run a natural language search for relevant code or documentation.
    
    Args:
        query: The query to search for
        ctx: Optional MCP context
        
    Returns:
        Dictionary containing search results
    """
    if ctx:
        ctx.info(f"Performing semantic search for: {query}")
    
    results = []
    
    # Get current directory (workspace root)
    workspace_root = os.getcwd()
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(workspace_root):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Simple keyword-based search (in a real implementation, this would be more sophisticated)
    for file_path in python_files:
        try:
            content = get_file_contents(file_path)
                
            # Calculate relevance score (simple check for query terms)
            relevance = 0
            query_terms = query.lower().split()
            
            for term in query_terms:
                term_count = content.lower().count(term)
                relevance += term_count
            
            # If any terms match, add to results
            if relevance > 0:
                relative_path = os.path.relpath(file_path, workspace_root)
                results.append({
                    "file_path": relative_path,
                    "relevance": relevance,
                    "preview": content[:500] + "..." if len(content) > 500 else content
                })
        except Exception as e:
            if ctx:
                ctx.warning(f"Error processing file {file_path}: {str(e)}")
    
    # Sort by relevance
    results.sort(key=lambda x: cast(int, x["relevance"]), reverse=True)
    
    # Limit results
    results = results[:20]
    
    return {
        "query": query,
        "results": results,
        "total_matches": len(results)
    }
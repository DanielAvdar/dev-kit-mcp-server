"""Tool for finding all usages of a function, class, method, or variable."""

import os
import re
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context


def list_code_usages(
    symbol_name: str, file_paths: Optional[List[str]] = None, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """List all usages of a symbol in the codebase.

    Args:
        symbol_name: The name of the symbol to find
        file_paths: Optional list of file paths to search in
        ctx: Optional MCP context

    Returns:
        Dictionary containing symbol usages

    """
    if ctx:
        ctx.info(f"Finding usages of symbol: {symbol_name}")

    workspace_root = os.getcwd()

    # If no file paths provided, search in all Python files
    if not file_paths:
        file_paths = []
        for root, _, files in os.walk(workspace_root):
            for file in files:
                if file.endswith(".py"):
                    file_paths.append(os.path.join(root, file))

    definitions = []
    references = []
    imports = []

    # Pattern for finding the symbol
    # This is a simplified version - a full implementation would use a proper parser
    symbol_pattern = re.compile(rf"\b{re.escape(symbol_name)}\b")
    definition_patterns = [
        re.compile(rf"def\s+{re.escape(symbol_name)}\s*\("),  # Function
        re.compile(rf"class\s+{re.escape(symbol_name)}\s*[:\(]"),  # Class
        re.compile(rf"\b{re.escape(symbol_name)}\s*="),  # Variable assignment
    ]
    import_patterns = [
        re.compile(rf"import\s+{re.escape(symbol_name)}"),
        re.compile(rf"from\s+[\w.]+\s+import\s+.*\b{re.escape(symbol_name)}\b.*"),
    ]

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                line_num = i + 1
                relative_path = os.path.relpath(file_path, workspace_root)

                # Check if it's a definition
                is_definition = any(pattern.search(line) for pattern in definition_patterns)
                if is_definition:
                    definitions.append({
                        "file_path": relative_path,
                        "line": line_num,
                        "content": line.strip(),
                        "type": "definition",
                    })
                    continue

                # Check if it's an import
                is_import = any(pattern.search(line) for pattern in import_patterns)
                if is_import:
                    imports.append({
                        "file_path": relative_path,
                        "line": line_num,
                        "content": line.strip(),
                        "type": "import",
                    })
                    continue

                # Check if it's a reference
                if symbol_pattern.search(line):
                    references.append({
                        "file_path": relative_path,
                        "line": line_num,
                        "content": line.strip(),
                        "type": "reference",
                    })
        except Exception as e:
            if ctx:
                ctx.warning(f"Error processing file {file_path}: {str(e)}")

    return {
        "symbol": symbol_name,
        "definitions": definitions,
        "references": references,
        "imports": imports,
        "total_usages": len(definitions) + len(references) + len(imports),
    }

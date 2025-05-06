"""Code analysis module using Python's AST and tokenize modules."""

import ast
import io
import tokenize
from typing import Any, Dict, List


class CodeAnalyzer:
    """Analyzes Python code using AST and tokenize modules."""

    @staticmethod
    def parse_ast(code: str) -> Dict[str, Any]:
        """Parse Python code into AST and extract key information.

        Args:
            code: Python code as string

        Returns:
            Dictionary containing extracted AST information

        """
        try:
            tree = ast.parse(code)

            # Extract key information
            result = {"imports": [], "functions": [], "classes": [], "variables": []}

            # Process imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["imports"].append({"name": name.name, "alias": name.asname})

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        result["imports"].append({"name": f"{module}.{name.name}", "alias": name.asname})

                # Process functions
                elif isinstance(node, ast.FunctionDef):
                    params = [p.arg for p in node.args.args]
                    result["functions"].append({"name": node.name, "params": params, "line_number": node.lineno})

                # Process classes
                elif isinstance(node, ast.ClassDef):
                    bases = [ast.unparse(base) for base in node.bases]
                    result["classes"].append({"name": node.name, "bases": bases, "line_number": node.lineno})

                # Process variables (at module level)
                elif isinstance(node, ast.Assign) and node.lineno <= len(code.splitlines()):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            result["variables"].append({"name": target.id, "line_number": node.lineno})

            return result

        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}

    @staticmethod
    def tokenize_code(code: str) -> List[Dict[str, Any]]:
        """Tokenize Python code.

        Args:
            code: Python code as string

        Returns:
            List of tokens with type and string value

        """
        tokens = []
        try:
            code_bytes = io.BytesIO(code.encode("utf-8"))
            for token in tokenize.tokenize(code_bytes.readline):
                token_info = {
                    "type": tokenize.tok_name[token.type],
                    "string": token.string,
                    "start": (token.start[0], token.start[1]),
                    "end": (token.end[0], token.end[1]),
                }
                tokens.append(token_info)
            return tokens
        except Exception as e:
            return [{"error": f"Tokenization error: {str(e)}"}]

    @staticmethod
    def analyze(code: str) -> Dict[str, Any]:
        """Perform comprehensive code analysis using both AST and tokenize.

        Args:
            code: Python code as string

        Returns:
            Dictionary with combined analysis results

        """
        ast_analysis = CodeAnalyzer.parse_ast(code)
        tokens = CodeAnalyzer.tokenize_code(code)

        # Count token types
        token_types = {}
        for token in tokens:
            if "type" in token:
                token_type = token["type"]
                token_types[token_type] = token_types.get(token_type, 0) + 1

        return {
            "ast_analysis": ast_analysis,
            "tokens": tokens[:100],  # Limit token output
            "token_summary": token_types,
        }

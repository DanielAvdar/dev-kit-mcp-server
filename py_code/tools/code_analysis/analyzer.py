"""Code analysis module using Python's AST and tokenize modules."""

import ast
import io
import os
import tokenize
from typing import Any, Dict, List, Optional, Set


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
            result: Dict[str, List[Dict[str, Any]]] = {"imports": [], "functions": [], "classes": [], "variables": []}

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
    def parse_raw_ast(code: str) -> ast.AST:
        """Parse Python code into raw AST object.

        Args:
            code: Python code as string

        Returns:
            Raw AST object for further analysis

        """
        return ast.parse(code)

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
        token_types: Dict[str, int] = {}
        for token in tokens:
            if "type" in token:
                token_type = token["type"]
                token_types[token_type] = token_types.get(token_type, 0) + 1

        return {
            "ast_analysis": ast_analysis,
            "tokens": tokens[:100],  # Limit token output
            "token_summary": token_types,
        }

    @staticmethod
    def analyze_repository(repo_path: str, file_filter: Optional[str] = None) -> Dict[str, Any]:
        """Analyze an entire repository or a specific path within it.

        Args:
            repo_path: Path to the repository or directory to analyze
            file_filter: Optional filter to limit analysis to specific file types

        Returns:
            Dictionary with repository analysis results

        """
        if not os.path.exists(repo_path):
            return {"error": f"Repository path does not exist: {repo_path}"}

        results: Dict[str, Any] = {
            "repository": repo_path,
            "files_analyzed": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_imports": 0,
            "file_analyses": {},
        }

        python_files = CodeAnalyzer._find_python_files(repo_path, file_filter)

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()

                file_analysis = CodeAnalyzer.analyze(code)
                rel_path = os.path.relpath(file_path, repo_path)

                # Extract counts for summary
                functions = len(file_analysis["ast_analysis"].get("functions", []))
                classes = len(file_analysis["ast_analysis"].get("classes", []))
                imports = len(file_analysis["ast_analysis"].get("imports", []))

                results["total_functions"] += functions
                results["total_classes"] += classes
                results["total_imports"] += imports
                results["files_analyzed"] += 1

                # Store individual file analysis
                results["file_analyses"][rel_path] = {
                    "functions": functions,
                    "classes": classes,
                    "imports": imports,
                    "details": file_analysis["ast_analysis"],
                }

            except Exception as e:
                rel_path = os.path.relpath(file_path, repo_path)
                results["file_analyses"][rel_path] = {"error": str(e)}

        return results

    @staticmethod
    def _find_python_files(path: str, file_filter: Optional[str] = None) -> List[str]:
        """Find all Python files in a directory or its subdirectories.

        Args:
            path: Path to search for Python files
            file_filter: Optional filter to limit to specific files

        Returns:
            List of paths to Python files

        """
        python_files = []

        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    if file_filter is None or file_filter in file:
                        python_files.append(os.path.join(root, file))

        return python_files

    @staticmethod
    def find_dependencies(repo_path: str) -> Dict[str, Any]:
        """Analyze repository to find module dependencies between files.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary with dependency information

        """
        dependency_map: Dict[str, Set[str]] = {}
        module_map: Dict[str, str] = {}

        # First pass: identify all Python modules in the repo
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Convert file path to module name
                    module_name = rel_path.replace(os.path.sep, ".")
                    if module_name.endswith(".py"):
                        module_name = module_name[:-3]

                    module_map[module_name] = rel_path
                    dependency_map[rel_path] = set()

        # Second pass: analyze imports
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    try:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_path)

                        with open(file_path, "r", encoding="utf-8") as f:
                            code = f.read()

                        tree = ast.parse(code)
                        imported_modules = CodeAnalyzer._extract_imports(tree)

                        # Map imports to files in the repo
                        for imported_module in imported_modules:
                            for module_name, target_path in module_map.items():
                                if imported_module == module_name or imported_module.startswith(f"{module_name}."):
                                    dependency_map[rel_path].add(target_path)
                    except (SyntaxError, UnicodeDecodeError):
                        # Skip files with syntax errors or encoding issues
                        pass

        # Convert sets to lists for JSON serialization
        result = {}
        for file_path, dependencies in dependency_map.items():
            result[file_path] = list(dependencies)

        return {"dependencies": result}

    @staticmethod
    def _extract_imports(tree: ast.AST) -> Set[str]:
        """Extract all imported module names from an AST.

        Args:
            tree: AST parsed from Python code

        Returns:
            Set of imported module names

        """
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)

        return imports

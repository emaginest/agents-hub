"""
Code Analyzer Tool for the Agents Hub framework.

This module provides a tool for analyzing code quality and structure.
"""

from agents_hub.tools.base import BaseTool
from typing import Dict, Any, Optional
import os
import logging
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

class CodeAnalyzerTool(BaseTool):
    """
    Tool for analyzing code quality and structure.
    
    This tool provides methods for analyzing code files and directories
    to identify issues, patterns, and structure.
    
    Example:
        ```python
        from agents_hub.tools.coding import CodeAnalyzerTool
        
        # Initialize Code Analyzer tool
        code_analyzer = CodeAnalyzerTool()
        
        # Use the tool
        result = await agent.run_tool("code_analyzer", {
            "operation": "analyze_file",
            "path": "/path/to/file.py",
            "language": "python",
        })
        ```
    """
    
    def __init__(self):
        """Initialize the code analyzer tool."""
        super().__init__(
            name="code_analyzer",
            description="Analyze code quality and structure",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["analyze_file", "analyze_directory", "count_lines", "find_patterns"],
                        "description": "Operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for (for find_patterns operation)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (for language-specific analysis)",
                    },
                },
                "required": ["operation", "path"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the code analyzer tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        path = parameters.get("path")
        
        logger.info(f"Running code analyzer {operation} operation on {path}")
        
        try:
            if operation == "analyze_file":
                language = parameters.get("language")
                return await self._analyze_file(path, language)
            
            elif operation == "analyze_directory":
                language = parameters.get("language")
                return await self._analyze_directory(path, language)
            
            elif operation == "count_lines":
                return await self._count_lines(path)
            
            elif operation == "find_patterns":
                pattern = parameters.get("pattern", "")
                return await self._find_patterns(path, pattern)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown operation: {operation}",
                    "operation": operation,
                    "path": path,
                }
        
        except Exception as e:
            logger.exception(f"Error executing {operation} operation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing {operation} operation: {str(e)}",
                "operation": operation,
                "path": path,
            }
    
    async def _analyze_file(self, path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a code file.
        
        Args:
            path: File path
            language: Programming language
            
        Returns:
            Analysis results
        """
        # Check if file exists
        if not os.path.exists(path) or not os.path.isfile(path):
            return {
                "status": "error",
                "message": f"File does not exist: {path}",
                "operation": "analyze_file",
                "path": path,
            }
        
        # Determine language if not provided
        if not language:
            language = self._detect_language(path)
        
        # Read file
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Analyze file
        analysis = {
            "file_path": path,
            "language": language,
            "size_bytes": os.path.getsize(path),
            "line_count": content.count("\n") + 1,
            "character_count": len(content),
        }
        
        # Language-specific analysis
        if language == "python":
            analysis.update(self._analyze_python(content))
        elif language == "javascript" or language == "typescript":
            analysis.update(self._analyze_js(content))
        elif language == "java":
            analysis.update(self._analyze_java(content))
        
        return {
            "status": "success",
            "message": f"File analyzed: {path}",
            "operation": "analyze_file",
            "path": path,
            "analysis": analysis,
        }
    
    async def _analyze_directory(self, path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a directory of code files.
        
        Args:
            path: Directory path
            language: Programming language
            
        Returns:
            Analysis results
        """
        # Check if directory exists
        if not os.path.exists(path) or not os.path.isdir(path):
            return {
                "status": "error",
                "message": f"Directory does not exist: {path}",
                "operation": "analyze_directory",
                "path": path,
            }
        
        # Analyze directory
        file_count = 0
        directory_count = 0
        total_lines = 0
        language_counts = {}
        
        for root, dirs, files in os.walk(path):
            directory_count += len(dirs)
            
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                
                # Detect language
                file_language = language or self._detect_language(file_path)
                
                # Count lines
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                        total_lines += line_count
                    
                    # Update language counts
                    if file_language:
                        language_counts[file_language] = language_counts.get(file_language, 0) + 1
                
                except Exception as e:
                    logger.warning(f"Error analyzing file {file_path}: {str(e)}")
        
        return {
            "status": "success",
            "message": f"Directory analyzed: {path}",
            "operation": "analyze_directory",
            "path": path,
            "analysis": {
                "file_count": file_count,
                "directory_count": directory_count,
                "total_lines": total_lines,
                "language_counts": language_counts,
            },
        }
    
    async def _count_lines(self, path: str) -> Dict[str, Any]:
        """
        Count lines of code in a file or directory.
        
        Args:
            path: File or directory path
            
        Returns:
            Line count results
        """
        # Check if path exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Path does not exist: {path}",
                "operation": "count_lines",
                "path": path,
            }
        
        # Count lines
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    line_count = sum(1 for _ in f)
                
                return {
                    "status": "success",
                    "message": f"Lines counted: {path}",
                    "operation": "count_lines",
                    "path": path,
                    "line_count": line_count,
                }
            
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error counting lines: {str(e)}",
                    "operation": "count_lines",
                    "path": path,
                }
        
        else:  # Directory
            total_lines = 0
            file_counts = {}
            
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            line_count = sum(1 for _ in f)
                            total_lines += line_count
                            file_counts[file_path] = line_count
                    
                    except Exception as e:
                        logger.warning(f"Error counting lines in {file_path}: {str(e)}")
            
            return {
                "status": "success",
                "message": f"Lines counted: {path}",
                "operation": "count_lines",
                "path": path,
                "total_line_count": total_lines,
                "file_counts": file_counts,
            }
    
    async def _find_patterns(self, path: str, pattern: str) -> Dict[str, Any]:
        """
        Find regex patterns in code files.
        
        Args:
            path: File or directory path
            pattern: Regex pattern to search for
            
        Returns:
            Pattern search results
        """
        # Check if path exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Path does not exist: {path}",
                "operation": "find_patterns",
                "path": path,
            }
        
        # Compile regex pattern
        try:
            regex = re.compile(pattern)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Invalid regex pattern: {str(e)}",
                "operation": "find_patterns",
                "path": path,
                "pattern": pattern,
            }
        
        # Find patterns
        matches = []
        
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    for match in regex.finditer(content):
                        matches.append({
                            "file": path,
                            "start": match.start(),
                            "end": match.end(),
                            "match": match.group(),
                        })
            
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error searching for patterns: {str(e)}",
                    "operation": "find_patterns",
                    "path": path,
                    "pattern": pattern,
                }
        
        else:  # Directory
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                            for match in regex.finditer(content):
                                matches.append({
                                    "file": file_path,
                                    "start": match.start(),
                                    "end": match.end(),
                                    "match": match.group(),
                                })
                    
                    except Exception as e:
                        logger.warning(f"Error searching for patterns in {file_path}: {str(e)}")
        
        return {
            "status": "success",
            "message": f"Patterns found: {len(matches)}",
            "operation": "find_patterns",
            "path": path,
            "pattern": pattern,
            "matches": matches,
        }
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect the programming language of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language or None
        """
        extension = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
        }
        
        return language_map.get(extension)
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """
        Analyze Python code.
        
        Args:
            content: File content
            
        Returns:
            Analysis results
        """
        # Count imports
        import_count = len(re.findall(r"^\s*import\s+", content, re.MULTILINE))
        from_import_count = len(re.findall(r"^\s*from\s+.+\s+import\s+", content, re.MULTILINE))
        
        # Count classes and functions
        class_count = len(re.findall(r"^\s*class\s+", content, re.MULTILINE))
        function_count = len(re.findall(r"^\s*def\s+", content, re.MULTILINE))
        
        # Count comments
        comment_count = len(re.findall(r"^\s*#", content, re.MULTILINE))
        
        return {
            "import_count": import_count + from_import_count,
            "class_count": class_count,
            "function_count": function_count,
            "comment_count": comment_count,
        }
    
    def _analyze_js(self, content: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript code.
        
        Args:
            content: File content
            
        Returns:
            Analysis results
        """
        # Count imports
        import_count = len(re.findall(r"^\s*import\s+", content, re.MULTILINE))
        require_count = len(re.findall(r"require\s*\(", content))
        
        # Count classes and functions
        class_count = len(re.findall(r"^\s*class\s+", content, re.MULTILINE))
        function_count = len(re.findall(r"function\s+\w+\s*\(", content))
        arrow_function_count = len(re.findall(r"=>\s*{", content))
        
        # Count comments
        single_line_comment_count = len(re.findall(r"^\s*//", content, re.MULTILINE))
        multi_line_comment_count = len(re.findall(r"/\*", content))
        
        return {
            "import_count": import_count + require_count,
            "class_count": class_count,
            "function_count": function_count + arrow_function_count,
            "comment_count": single_line_comment_count + multi_line_comment_count,
        }
    
    def _analyze_java(self, content: str) -> Dict[str, Any]:
        """
        Analyze Java code.
        
        Args:
            content: File content
            
        Returns:
            Analysis results
        """
        # Count imports
        import_count = len(re.findall(r"^\s*import\s+", content, re.MULTILINE))
        
        # Count classes and methods
        class_count = len(re.findall(r"^\s*(public|private|protected)?\s*class\s+", content, re.MULTILINE))
        interface_count = len(re.findall(r"^\s*(public|private|protected)?\s*interface\s+", content, re.MULTILINE))
        method_count = len(re.findall(r"^\s*(public|private|protected)?\s*\w+\s+\w+\s*\(", content, re.MULTILINE))
        
        # Count comments
        single_line_comment_count = len(re.findall(r"^\s*//", content, re.MULTILINE))
        multi_line_comment_count = len(re.findall(r"/\*", content))
        
        return {
            "import_count": import_count,
            "class_count": class_count,
            "interface_count": interface_count,
            "method_count": method_count,
            "comment_count": single_line_comment_count + multi_line_comment_count,
        }

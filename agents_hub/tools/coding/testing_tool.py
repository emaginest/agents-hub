"""
Testing Tool for the Agents Hub framework.

This module provides a tool for running tests and analyzing test results.
"""

from agents_hub.tools.base import BaseTool
from typing import Dict, List, Any, Optional
import os
import logging
import asyncio
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

class TestingTool(BaseTool):
    """
    Tool for running tests and analyzing test results.
    
    This tool provides methods for running tests, analyzing test results,
    and generating test reports.
    
    Example:
        ```python
        from agents_hub.tools.coding import TestingTool
        
        # Initialize Testing tool
        testing_tool = TestingTool()
        
        # Use the tool
        result = await agent.run_tool("testing_tool", {
            "operation": "run_pytest",
            "path": "/path/to/tests",
            "coverage": True,
        })
        ```
    """
    
    def __init__(self):
        """Initialize the testing tool."""
        super().__init__(
            name="testing_tool",
            description="Run tests and analyze test results",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["run_tests", "run_pytest", "run_jest", "analyze_coverage"],
                        "description": "Operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the test directory or file",
                    },
                    "test_args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional arguments for the test command",
                    },
                    "coverage": {
                        "type": "boolean",
                        "description": "Whether to generate coverage report",
                        "default": False,
                    },
                },
                "required": ["operation", "path"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the testing tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        path = parameters.get("path")
        
        logger.info(f"Running testing tool {operation} operation on {path}")
        
        try:
            if operation == "run_tests":
                test_args = parameters.get("test_args", [])
                coverage = parameters.get("coverage", False)
                return await self._run_tests(path, test_args, coverage)
            
            elif operation == "run_pytest":
                test_args = parameters.get("test_args", [])
                coverage = parameters.get("coverage", False)
                return await self._run_pytest(path, test_args, coverage)
            
            elif operation == "run_jest":
                test_args = parameters.get("test_args", [])
                coverage = parameters.get("coverage", False)
                return await self._run_jest(path, test_args, coverage)
            
            elif operation == "analyze_coverage":
                return await self._analyze_coverage(path)
            
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
    
    async def _run_tests(self, path: str, test_args: List[str] = None, coverage: bool = False) -> Dict[str, Any]:
        """
        Run tests based on the project type.
        
        Args:
            path: Path to the test directory or file
            test_args: Additional arguments for the test command
            coverage: Whether to generate coverage report
            
        Returns:
            Test results
        """
        # Check if path exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Path does not exist: {path}",
                "operation": "run_tests",
                "path": path,
            }
        
        # Detect test framework
        if os.path.exists(os.path.join(path, "pytest.ini")) or os.path.exists(os.path.join(path, "conftest.py")):
            return await self._run_pytest(path, test_args, coverage)
        
        elif os.path.exists(os.path.join(path, "package.json")):
            # Check if Jest is in package.json
            try:
                with open(os.path.join(path, "package.json"), "r", encoding="utf-8") as f:
                    package_json = json.load(f)
                    
                    if "jest" in package_json.get("devDependencies", {}) or "jest" in package_json.get("dependencies", {}):
                        return await self._run_jest(path, test_args, coverage)
            
            except Exception as e:
                logger.warning(f"Error reading package.json: {str(e)}")
        
        # Default to pytest
        return await self._run_pytest(path, test_args, coverage)
    
    async def _run_pytest(self, path: str, test_args: List[str] = None, coverage: bool = False) -> Dict[str, Any]:
        """
        Run Python tests with pytest.
        
        Args:
            path: Path to the test directory or file
            test_args: Additional arguments for pytest
            coverage: Whether to generate coverage report
            
        Returns:
            Test results
        """
        test_args = test_args or []
        
        # Build command
        cmd = ["pytest"]
        
        if coverage:
            cmd.extend(["--cov", "--cov-report", "term"])
        
        cmd.extend(test_args)
        cmd.append(path)
        
        # Run tests
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()
            
            # Parse test results
            test_results = self._parse_pytest_output(stdout_text)
            
            return {
                "status": "success" if process.returncode == 0 else "failure",
                "message": f"Pytest tests {'passed' if process.returncode == 0 else 'failed'}",
                "operation": "run_pytest",
                "path": path,
                "return_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "test_results": test_results,
            }
        
        except Exception as e:
            logger.exception(f"Error running pytest: {str(e)}")
            return {
                "status": "error",
                "message": f"Error running pytest: {str(e)}",
                "operation": "run_pytest",
                "path": path,
            }
    
    async def _run_jest(self, path: str, test_args: List[str] = None, coverage: bool = False) -> Dict[str, Any]:
        """
        Run JavaScript tests with Jest.
        
        Args:
            path: Path to the test directory or file
            test_args: Additional arguments for Jest
            coverage: Whether to generate coverage report
            
        Returns:
            Test results
        """
        test_args = test_args or []
        
        # Build command
        cmd = ["npx", "jest"]
        
        if coverage:
            cmd.append("--coverage")
        
        cmd.extend(test_args)
        
        if os.path.isfile(path):
            cmd.append(path)
        
        # Run tests
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=os.path.dirname(path) if os.path.isfile(path) else path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()
            
            # Parse test results
            test_results = self._parse_jest_output(stdout_text)
            
            return {
                "status": "success" if process.returncode == 0 else "failure",
                "message": f"Jest tests {'passed' if process.returncode == 0 else 'failed'}",
                "operation": "run_jest",
                "path": path,
                "return_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "test_results": test_results,
            }
        
        except Exception as e:
            logger.exception(f"Error running Jest: {str(e)}")
            return {
                "status": "error",
                "message": f"Error running Jest: {str(e)}",
                "operation": "run_jest",
                "path": path,
            }
    
    async def _analyze_coverage(self, path: str) -> Dict[str, Any]:
        """
        Analyze test coverage reports.
        
        Args:
            path: Path to the coverage report directory
            
        Returns:
            Coverage analysis
        """
        # Check if path exists
        if not os.path.exists(path):
            return {
                "status": "error",
                "message": f"Path does not exist: {path}",
                "operation": "analyze_coverage",
                "path": path,
            }
        
        # Check for coverage reports
        coverage_files = []
        
        # Python coverage
        if os.path.exists(os.path.join(path, ".coverage")):
            coverage_files.append(os.path.join(path, ".coverage"))
        
        # JavaScript coverage
        if os.path.exists(os.path.join(path, "coverage")):
            coverage_files.append(os.path.join(path, "coverage"))
        
        if not coverage_files:
            return {
                "status": "error",
                "message": f"No coverage reports found in {path}",
                "operation": "analyze_coverage",
                "path": path,
            }
        
        # Analyze coverage
        coverage_analysis = {
            "files": coverage_files,
        }
        
        # Run coverage report
        if os.path.exists(os.path.join(path, ".coverage")):
            try:
                process = await asyncio.create_subprocess_exec(
                    "coverage", "report",
                    cwd=path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                stdout_text = stdout.decode().strip()
                stderr_text = stderr.decode().strip()
                
                coverage_analysis["python_coverage"] = {
                    "report": stdout_text,
                    "error": stderr_text if stderr_text else None,
                }
            
            except Exception as e:
                logger.warning(f"Error running Python coverage report: {str(e)}")
        
        return {
            "status": "success",
            "message": f"Coverage analyzed: {path}",
            "operation": "analyze_coverage",
            "path": path,
            "coverage_analysis": coverage_analysis,
        }
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse pytest output to extract test results.
        
        Args:
            output: Pytest output
            
        Returns:
            Parsed test results
        """
        # Extract test summary
        summary_match = re.search(r"=+ (.*) in (.*) =+", output)
        summary = summary_match.group(1) if summary_match else "Unknown"
        
        # Extract test counts
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        skipped_match = re.search(r"(\d+) skipped", output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        
        # Extract coverage
        coverage_match = re.search(r"TOTAL\s+.*\s+(\d+)%", output)
        coverage = int(coverage_match.group(1)) if coverage_match else None
        
        return {
            "summary": summary,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
            "coverage": coverage,
        }
    
    def _parse_jest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Jest output to extract test results.
        
        Args:
            output: Jest output
            
        Returns:
            Parsed test results
        """
        # Extract test summary
        summary_match = re.search(r"Tests:\s+(\d+) passed,\s+(\d+) failed,\s+(\d+) total", output)
        
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2))
            total = int(summary_match.group(3))
        else:
            # Alternative format
            passed_match = re.search(r"(\d+) passing", output)
            failed_match = re.search(r"(\d+) failing", output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            total = passed + failed
        
        # Extract coverage
        coverage_match = re.search(r"All files.*\|.*\|.*\|.*\|.*\| (\d+\.?\d*)%", output)
        coverage = float(coverage_match.group(1)) if coverage_match else None
        
        return {
            "summary": f"{passed} passed, {failed} failed, {total} total",
            "passed": passed,
            "failed": failed,
            "skipped": 0,  # Jest doesn't report skipped tests in the summary
            "total": total,
            "coverage": coverage,
        }

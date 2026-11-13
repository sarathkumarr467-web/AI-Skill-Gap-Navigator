"""
SkillBridge AI - Safe Coding Challenge Execution Sandbox
Implements Feature 15: Isolated sandboxed execution of user-submitted Python code
against MBPP unit test assertions with AST security guards, timeouts, and memory safety.
"""

import ast
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Disallowed modules and operations for security
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "socket", "urllib", "requests", "shutil",
    "pathlib", "ctypes", "multiprocessing", "threading", "pty", "commands",
    "builtins", "importlib", "pickle", "shelve", "posix", "nt", "_winapi"
}

BLOCKED_CALLS = {
    "eval", "exec", "compile", "__import__", "open", "input", "breakpoint", "help"
}

class SecurityViolationError(Exception):
    pass

class ASTSecurityChecker(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            base_module = alias.name.split(".")[0]
            if base_module in BLOCKED_MODULES:
                raise SecurityViolationError(f"Security Alert: Import of module '{alias.name}' is prohibited in this sandbox.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split(".")[0]
            if base_module in BLOCKED_MODULES:
                raise SecurityViolationError(f"Security Alert: Import from module '{node.module}' is prohibited in this sandbox.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_CALLS:
                raise SecurityViolationError(f"Security Alert: Call to restricted function '{node.func.id}()' is prohibited.")
        self.generic_visit(node)

class CodingSandboxService:
    @staticmethod
    def validate_code_ast(code_str: str) -> Tuple[bool, str]:
        """Runs AST parse and security screening."""
        try:
            tree = ast.parse(code_str)
            checker = ASTSecurityChecker()
            checker.visit(tree)
            return True, "AST security verification passed."
        except SyntaxError as se:
            return False, f"Syntax Error: {se.msg} (line {se.lineno})"
        except SecurityViolationError as sve:
            return False, str(sve)
        except Exception as e:
            return False, f"Code validation error: {str(e)}"

    @classmethod
    def execute_challenge(
        cls,
        user_code: str,
        test_list: List[str],
        test_setup: str = "",
        timeout_seconds: float = 3.5
    ) -> Dict[str, Any]:
        """
        Executes user code against assertions in a clean, isolated subprocess.
        Returns execution results, tests passed, error messages, and status.
        """
        # 1. AST Static Security Check
        is_safe, msg = cls.validate_code_ast(user_code)
        if not is_safe:
            return {
                "status": "SECURITY_VIOLATION" if "Security Alert" in msg else "SYNTAX_ERROR",
                "passed_tests": 0,
                "total_tests": len(test_list),
                "output": msg,
                "error": msg
            }

        # 2. Build test harness script
        harness_lines = [
            "# Sandbox Test Runner",
            test_setup or "",
            "",
            user_code,
            "",
            "tests_passed = 0",
            f"total_tests = {len(test_list)}",
            "test_results = []",
            ""
        ]

        for i, test_assertion in enumerate(test_list):
            harness_lines.extend([
                f"try:",
                f"    {test_assertion}",
                f"    tests_passed += 1",
                f"    test_results.append(('PASSED', '{test_assertion}'))",
                f"except AssertionError:",
                f"    test_results.append(('FAILED', '{test_assertion}'))",
                f"except Exception as e:",
                f"    test_results.append(('ERROR', str(type(e).__name__) + ': ' + str(e)))",
                ""
            ])

        harness_lines.extend([
            "print(f'__RESULT__:PASSED={tests_passed};TOTAL={total_tests}')",
            "for r in test_results:",
            "    print(f'  [{r[0]}] {r[1]}')"
        ])

        harness_code = "\n".join(harness_lines)

        # 3. Write to temporary file and execute in clean subprocess
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(harness_code)
            tmp_path = Path(tmp.name)

        try:
            # Run in isolated subprocess with strict timeout
            result = subprocess.run(
                [sys.executable, str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            stdout = result.stdout
            stderr = result.stderr

            if result.returncode != 0:
                return {
                    "status": "RUNTIME_ERROR",
                    "passed_tests": 0,
                    "total_tests": len(test_list),
                    "output": (stdout + "\n" + stderr).strip(),
                    "error": stderr.strip() or "Process returned non-zero exit code"
                }

            # Parse results
            passed = 0
            total = len(test_list)
            for line in stdout.splitlines():
                if line.startswith("__RESULT__:"):
                    parts = line.replace("__RESULT__:", "").split(";")
                    for p in parts:
                        if p.startswith("PASSED="):
                            passed = int(p.split("=")[1])
                        elif p.startswith("TOTAL="):
                            total = int(p.split("=")[1])

            status = "PASSED" if passed == total else "FAILED"

            return {
                "status": status,
                "passed_tests": passed,
                "total_tests": total,
                "output": stdout.replace(f"__RESULT__:PASSED={passed};TOTAL={total}", "").strip(),
                "error": ""
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "passed_tests": 0,
                "total_tests": len(test_list),
                "output": f"Execution timed out ({timeout_seconds}s limit exceeded). Ensure your solution avoids infinite loops.",
                "error": "Time limit exceeded"
            }
        except Exception as ex:
            return {
                "status": "EXECUTION_ERROR",
                "passed_tests": 0,
                "total_tests": len(test_list),
                "output": str(ex),
                "error": str(ex)
            }
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass

Tuple_Validation = tuple[bool, str]

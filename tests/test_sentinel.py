import os
import sys
import json
import pytest
from pathlib import Path
from sentinel.runner import MindCoreSentinel

class TestMindCoreSentinel:
    
    @pytest.fixture
    def node_project(self, tmp_path):
        """Create a fake Node.js project."""
        project_dir = tmp_path / "node_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text(json.dumps({
            "name": "test-project",
            "version": "1.0.0",
            "main": "index.js",
            "scripts": {
                "test": "echo 'test'"
            }
        }))
        (project_dir / "index.js").write_text("console.log('hello');")
        return project_dir

    def test_detect_project_type_node(self, node_project):
        sys.argv = ["sentinel", str(node_project)]
        sentinel = MindCoreSentinel(str(node_project))
        assert sentinel.detect_project_type() == "nodejs"

    def test_find_entry_points(self, node_project):
        sentinel = MindCoreSentinel(str(node_project))
        entry_points = sentinel.find_entry_points("nodejs")
        
        # Should find package.json main, script, and index.js
        # main -> node index.js
        # script test -> npm run test
        # file index.js -> node index.js
        
        descriptions = [ep["description"] for ep in entry_points]
        assert any("Main entry point" in d for d in descriptions)
        assert any("npm script: test" in d for d in descriptions)
        assert any("Common Node.js entry file: index.js" in d for d in descriptions)

    def test_run_analysis_smoke(self, node_project):
        """Smoke test that runs analysis on the fake project."""
        # Create a dummy executable for node/npm just in case environment doesn't have it?
        # Actually in CI we expect node. But here we might not have it.
        # We can mock subprocess.Popen if needed, but let's try running it.
        # The tool says "Mock or short-circuit subprocess runs if needed".
        # Let's mock execute_entry_point to avoid actually running node.
        
        sentinel = MindCoreSentinel(str(node_project))
        
        # Mock execute_entry_point
        original_execute = sentinel.execute_entry_point
        
        def mock_execute(entry_point):
            return {
                "entry_point": entry_point,
                "success": True,
                "stdout": "Mock output",
                "stderr": "",
                "exit_code": 0,
                "error": None,
                "duration": 0.1
            }
            
        sentinel.execute_entry_point = mock_execute
        
        success = sentinel.run_analysis()
        assert success is True
        
        report = sentinel.generate_report()
        assert "# MindCore · Sentinel Bug Report" in report
        assert "✅ **No bugs detected!**" in report

    def test_high_severity_bug_reporting(self, node_project):
        sentinel = MindCoreSentinel(str(node_project))
        
        # Inject a bug
        sentinel.bugs.append({
            "type": "non_zero_exit",
            "severity": "HIGH",
            "title": "Process exited with code 1",
            "description": "Test bug",
            "reproduction": ["cmd"],
            "output": {"stderr": "error"}
        })
        
        report = sentinel.generate_report()
        assert "Found **1** potential bug(s)" in report
        assert "### HIGH Severity" in report
        assert "Test bug" in report

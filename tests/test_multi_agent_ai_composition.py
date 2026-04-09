import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import compose  # noqa: E402


class MultiAgentAiCompositionTest(unittest.TestCase):
    def test_strict_python_multi_agent_stateful_example_renders_expected_sections(self):
        spec_path = REPO_ROOT / "examples" / "strict-python-multi-agent-stateful-ai.yml"

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "CLAUDE.md"

            result = compose.main(["compose.py", str(spec_path), str(out_path)])

            self.assertEqual(result, 0)
            output = out_path.read_text(encoding="utf-8")

        self.assertIn("**Profile:** strict", output)
        self.assertIn("**Targets:** base, python, multi-agent-ai, stateful-ai", output)
        self.assertIn("## Agent Architecture", output)
        self.assertIn("Define each agent with a single, explicit responsibility.", output)
        self.assertIn("## State Model", output)
        self.assertIn(
            "Define canonical state explicitly and distinguish it from derived summaries or transient working memory.",
            output,
        )


if __name__ == "__main__":
    unittest.main()

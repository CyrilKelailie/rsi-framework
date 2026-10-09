"""CLI regression tests; run with python3 -m unittest discover -s tests -v."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/rsi/scripts/rsi_state.py"


class RsiStateCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rsi-state-test-")
        self.addCleanup(self.tmp.cleanup)
        self.state_path = Path(self.tmp.name) / "state.json"
        self.env = dict(os.environ, RSI_STATE=str(self.state_path),
                        PYTHONIOENCODING="utf-8")

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.tmp.name, env=self.env, capture_output=True,
            text=True, encoding="utf-8", timeout=10, check=False,
        )

    def run_ok(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return result

    def make_solution(self, level="L2"):
        self.run_ok("init", "校验回归测试", "--success", "保留旧状态格式")
        args = ["add", "E1", "branch", "Evidence", "--tag", "fact"]
        if level is not None:
            args += ["--level", level]
        self.run_ok(*args)
        self.run_ok("add", "Solution", "solution", "Conclusion", "--sources", "E1")

    def read_state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def write_state(self, state):
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8",
        )

    def check_state(self):
        before = self.state_path.read_bytes()
        result = self.run_cli("check")
        self.assertEqual(self.state_path.read_bytes(), before, "check rewrote the state")
        self.assertEqual(result.stderr, "", result.stderr)
        return result

    def assert_check_fails(self, *messages):
        result = self.check_state()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Check passed", result.stdout)
        for message in messages:
            self.assertIn(message, result.stdout)
        return result

    def assert_check_passes(self):
        result = self.check_state()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Check passed", result.stdout)
        self.assertNotIn("⚠️", result.stdout)

    def test_omitted_level_is_recorded_as_empty_and_fails_check(self):
        self.make_solution(level=None)
        self.assertEqual(self.read_state()["rounds"][-1]["nodes"]["E1"]["level"], "")
        self.assert_check_fails("E1", "needs >= L2")

    def test_explicit_empty_level_fails_check(self):
        self.make_solution(level="")
        self.assert_check_fails("E1", "needs >= L2")

    def test_legacy_source_without_level_key_fails_without_traceback(self):
        self.make_solution()
        state = self.read_state()
        del state["rounds"][-1]["nodes"]["E1"]["level"]
        self.write_state(state)
        self.assert_check_fails("E1", "needs >= L2")

    def test_null_or_invalid_legacy_level_fails_check(self):
        for level in (None, " ", "L5", "l2"):
            with self.subTest(level=level):
                self.make_solution()
                state = self.read_state()
                state["rounds"][-1]["nodes"]["E1"]["level"] = level
                self.write_state(state)
                self.assert_check_fails("E1", "needs >= L2")

    def test_l0_and_l1_evidence_warn_and_exit_one(self):
        for level in ("L0", "L1"):
            with self.subTest(level=level):
                self.make_solution(level=level)
                self.assert_check_fails("low-evidence conclusions: E1", "needs >= L2")

    def test_l2_through_l4_evidence_pass_and_exit_zero(self):
        for level in ("L2", "L3", "L4"):
            with self.subTest(level=level):
                self.make_solution(level=level)
                self.assert_check_passes()

    def test_multiple_valid_sources_pass(self):
        self.make_solution()
        self.run_ok("add", "E3", "branch", "External evidence", "--level", "L3")
        self.run_ok("add", "E4", "branch", "Executed evidence", "--level", "L4")
        self.run_ok("add", "Solution", "solution", "Conclusion", "--sources", "E1,E3,E4")
        self.assert_check_passes()

    def test_one_weak_source_among_valid_sources_fails(self):
        for level in ("", "L0", "L1"):
            with self.subTest(level=level):
                self.make_solution(level="L4")
                self.run_ok("add", "Weak", "branch", "Weak evidence", "--level", level)
                self.run_ok("add", "Solution", "solution", "Conclusion",
                            "--sources", "E1,Weak", "--level", "L4")
                result = self.assert_check_fails("low-evidence conclusions: Weak", "needs >= L2")
                self.assertNotIn("low-evidence conclusions: E1", result.stdout)

    def test_unrated_uncited_node_is_allowed(self):
        self.make_solution()
        self.run_ok("add", "Uncited", "branch", "Work in progress")
        self.assert_check_passes()
        state = self.read_state()
        del state["rounds"][-1]["nodes"]["Uncited"]["level"]
        self.write_state(state)
        self.assert_check_passes()

    def test_missing_sources_fail_for_existing_summary_types(self):
        for node_type in ("summary", "synthesis", "solution"):
            with self.subTest(node_type=node_type):
                self.run_ok("init", "Missing sources")
                self.run_ok("add", "Result", node_type, "Unsupported result")
                self.assert_check_fails("Result cites no source IDs")

    def test_rated_assumption_still_fails_check(self):
        self.make_solution()
        self.run_ok("add", "E1", "branch", "Assumption", "--tag", "assumption", "--level", "L4")
        self.assert_check_fails("unverified assumption", "Unconfirmed points")

    def test_existing_plan_warnings_are_all_reported_before_exit(self):
        self.run_ok("init", "Plan warnings")
        self.run_ok("add", "A", "plan", "User proposal", "--user")
        self.assert_check_fails(
            "Plan A has no score", "Plan A has no rebuttal",
            "All plans come from the user's proposal", "No real-world examples",
        )

    def test_excessive_retries_fail_check(self):
        self.make_solution()
        for _ in range(4):
            self.run_ok("retry", "Solution", "Verify again")
        self.assert_check_fails("Solution retried 4 times")

    def test_failed_check_can_be_fixed_without_migrating_state(self):
        self.make_solution(level=None)
        original = self.read_state()
        self.assert_check_fails("E1", "needs >= L2")
        self.run_ok("add", "E1", "branch", "Verified evidence", "--tag", "fact", "--level", "L2")
        updated = self.read_state()
        self.assertEqual(set(updated), set(original))
        self.assertEqual(updated["created"], original["created"])
        self.assertEqual(updated["rounds"][-1]["nodes"]["E1"]["version"], 2)
        self.assert_check_passes()

    def test_legacy_metadata_and_previous_rounds_are_preserved(self):
        self.make_solution()
        state = self.read_state()
        previous = json.loads(json.dumps(state["rounds"][-1]))
        previous["nodes"]["E1"]["level"] = ""
        state["rounds"].insert(0, previous)
        state["rounds"][-1]["round"] = 2
        state["custom_metadata"] = {"备注": "保留"}
        state["rounds"][-1]["nodes"]["E1"]["custom_metadata"] = [1, 2, 3]
        self.write_state(state)
        self.assert_check_passes()

    def test_other_commands_keep_success_exit_codes(self):
        self.make_solution()
        self.run_ok("status")
        self.run_ok("handoff")
        self.run_ok("export", "--patch", "Validation only")
        self.run_ok("retry", "Solution", "Check again")
        self.run_ok("round")


if __name__ == "__main__":
    unittest.main()

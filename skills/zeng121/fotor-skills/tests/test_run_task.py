import importlib.util
import unittest
from pathlib import Path


def _load_run_task_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_task.py"
    spec = importlib.util.spec_from_file_location("run_task_module", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


run_task = _load_run_task_module()


class RunTaskFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_insufficient_credits_skips_fallback(self):
        calls = 0

        async def failing_task(_client, **_params):
            nonlocal calls
            calls += 1
            raise run_task.FotorAPIError("No enough credits", code="510")

        original_fn = run_task._TASK_FN["text2image"]
        run_task._TASK_FN["text2image"] = failing_task
        try:
            result = await run_task._run_single(
                client=object(),
                spec={
                    "task_type": "text2image",
                    "params": {"prompt": "cat", "model_id": "gemini-3.1-flash-image-preview"},
                    "tag": "demo-text2image",
                },
            )
        finally:
            run_task._TASK_FN["text2image"] = original_fn

        self.assertEqual(calls, 1)
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["original_model_id"], "gemini-3.1-flash-image-preview")
        self.assertEqual(result["fallback_model_id"], "")
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("code=510", result["error"])

    async def test_non_credit_api_error_still_uses_fallback(self):
        calls = []

        async def flaky_task(_client, **params):
            calls.append(params["model_id"])
            if len(calls) == 1:
                raise run_task.FotorAPIError("temporary upstream issue", code="503")
            return _FakeTaskResult()

        original_fn = run_task._TASK_FN["text2image"]
        run_task._TASK_FN["text2image"] = flaky_task
        try:
            result = await run_task._run_single(
                client=object(),
                spec={
                    "task_type": "text2image",
                    "params": {"prompt": "cat", "model_id": "gemini-3.1-flash-image-preview"},
                    "tag": "demo-text2image",
                },
            )
        finally:
            run_task._TASK_FN["text2image"] = original_fn

        self.assertEqual(calls, ["gemini-3.1-flash-image-preview", "seedream-5-0-260128"])
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["original_model_id"], "gemini-3.1-flash-image-preview")
        self.assertEqual(result["fallback_model_id"], "seedream-5-0-260128")
        self.assertTrue(result["success"])


class _FakeStatus:
    name = "COMPLETED"


class _FakeTaskResult:
    def __init__(self):
        self.task_id = "task-123"
        self.status = _FakeStatus()
        self.success = True
        self.result_url = "https://example.com/image.png"
        self.error = None
        self.elapsed_seconds = 1.23
        self.creditsIncrement = 5
        self.metadata = {}


if __name__ == "__main__":
    unittest.main()

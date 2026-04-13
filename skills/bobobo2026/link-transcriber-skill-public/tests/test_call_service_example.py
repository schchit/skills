import unittest

from skill.scripts.call_service_example import IN_PROGRESS_STATUSES, format_failure, infer_platform


class CallServiceExampleTests(unittest.TestCase):
    def test_infer_platform_from_known_hosts(self):
        self.assertEqual(infer_platform("https://v.douyin.com/abc123/"), "douyin")
        self.assertEqual(infer_platform("http://xhslink.com/o/abc123"), "xiaohongshu")

    def test_in_progress_statuses_match_service_workflow(self):
        self.assertTrue({"PENDING", "PARSING", "DOWNLOADING", "TRANSCRIBING"}.issubset(IN_PROGRESS_STATUSES))

    def test_cookie_failure_is_reframed_as_server_side_issue(self):
        payload = {"msg": "success", "data": {"error_message": "小红书 Cookie 缺失，请先配置有效 Cookie"}}
        self.assertIn("服务端配置问题", format_failure(payload))


if __name__ == "__main__":
    unittest.main()

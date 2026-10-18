"""Publication guards must fail before mutations, with no overwrite/retry path."""
import argparse
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import publish_cli_release as publish

SHA = "a" * 40
ENV = {"GITHUB_REPOSITORY": publish.REPOSITORY, "GITHUB_EVENT_NAME": "push",
       "GITHUB_REF": "refs/tags/v0.2.0", "GITHUB_SHA": SHA}


class PublicationTests(unittest.TestCase):
    def test_api_failure_preserves_service_reason(self):
        import subprocess
        result = subprocess.CompletedProcess([], 1, b'{"message":"denied"}', b'gh: denied (HTTP 403)')
        with patch.object(publish.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "HTTP 403.*denied"):
                publish.api("repos/example/repo/releases", method="POST", body={})

    def test_non_tag_wrong_repo_event_or_revision_cannot_call_api(self):
        for key, value in (("GITHUB_REPOSITORY", "fork/repo"), ("GITHUB_EVENT_NAME", "workflow_dispatch"),
                           ("GITHUB_REF", "refs/heads/main"), ("GITHUB_SHA", "b" * 40)):
            with self.subTest(key=key), patch.dict(os.environ, {**ENV, key: value}), patch.object(publish, "api") as api:
                with self.assertRaisesRegex(RuntimeError, "exact repository/tag"):
                    publish.publish(argparse.Namespace(revision=SHA), {}, lambda: None)
                api.assert_not_called()

    def test_extra_missing_and_symlink_assets_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "six distribution"):
                publish.candidate(directory, SHA)
            for target in publish.package.SLUGS:
                (directory / publish.package.archive_name(target)).touch()
            (directory / "SHA256SUMS").touch()
            (directory / "extra").touch()
            with self.assertRaisesRegex(RuntimeError, "six distribution"):
                publish.candidate(directory, SHA)
            (directory / "extra").unlink()
            with patch.object(Path, "is_symlink", return_value=True):
                with self.assertRaisesRegex(RuntimeError, "Regular assets"):
                    publish.candidate(directory, SHA)

    def test_checksum_mismatch_and_archive_revision_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for target in publish.package.SLUGS:
                (directory / publish.package.archive_name(target)).write_bytes(b"archive")
            (directory / "SHA256SUMS").write_bytes(b"incorrect\n")
            with patch.object(publish.package, "read_archive", return_value={}), patch.object(publish.package, "verify_contents"):
                with self.assertRaisesRegex(RuntimeError, "SHA256SUMS differs"):
                    publish.candidate(directory, SHA)
            with patch.object(publish.package, "read_archive", return_value={}), patch.object(
                    publish.package, "verify_contents", side_effect=RuntimeError("Archive identity differs")):
                with self.assertRaisesRegex(RuntimeError, "Archive identity"):
                    publish.candidate(directory, SHA)

    def test_remote_metadata_and_download_tampering_rejected(self):
        expected = publish.package.record(b"right")
        asset = {"id": 1, "name": "asset", "state": "uploaded", "size": 5,
                 "digest": "sha256:" + expected["sha256"]}
        with tempfile.TemporaryDirectory() as temporary, patch.object(publish, "api", return_value=b"wrong"):
            with self.assertRaisesRegex(RuntimeError, "Downloaded release asset"):
                publish.uploaded_assets({"assets": [asset]}, {"asset": expected}, Path(temporary))
            for changed in ({"digest": "sha256:bad"}, {"size": 99}, {"state": "new"}):
                with self.subTest(changed=changed), self.assertRaisesRegex(RuntimeError, "metadata"):
                    publish.uploaded_assets({"assets": [{**asset, **changed}]}, {"asset": expected}, Path(temporary))
            with self.assertRaisesRegex(RuntimeError, "asset set"):
                publish.uploaded_assets({"assets": [asset, asset]}, {"asset": expected}, Path(temporary))

    def scenario(self, *, visibility="private", tag_sha=SHA, existing=False, upload_failure=False):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            notes = directory / "notes.md"
            notes.write_text("# Lingose 0.2.0\n", encoding="utf-8")
            args = argparse.Namespace(revision=SHA, assets=directory, notes=notes, output=directory)
            rows = {"asset": publish.package.record(b"right")}
            value = {"id": 1, "tag_name": publish.TAG, "name": "Lingose 0.2.0", "draft": True,
                     "prerelease": False, "body": notes.read_text(encoding="utf-8"), "assets": []}
            calls = []

            def api(endpoint, *, method="GET", body=None, binary=False):
                calls.append((endpoint, method, body))
                if endpoint == "repos/" + publish.REPOSITORY:
                    return {"full_name": publish.REPOSITORY, "visibility": visibility}
                if "/git/ref/" in endpoint:
                    return {"object": {"type": "tag", "sha": "c" * 40}}
                if "/git/tags/" in endpoint:
                    return {"object": {"type": "commit", "sha": tag_sha}}
                if "?per_page=" in endpoint:
                    return [value] if existing else []
                if method == "PATCH":
                    return {**value, "draft": False, "published_at": "2026-10-18T00:00:00Z", "html_url": "https://example.test"}
                return value

            report, saved = {}, []
            error = None
            with patch.dict(os.environ, ENV), patch.object(publish, "candidate", return_value=rows), patch.object(
                    publish, "api", side_effect=api), patch.object(publish, "uploaded_assets", return_value=[]), patch.object(
                    publish.subprocess, "run", side_effect=RuntimeError("upload interrupted") if upload_failure else None) as command:
                try:
                    publish.publish(args, report, lambda: saved.append(report.copy()))
                except RuntimeError as caught:
                    error = caught
                if command.called:
                    self.assertNotIn("--clobber", command.call_args.args[0])
            return calls, report, saved, error

    def test_wrong_visibility_tag_or_existing_release_never_mutates(self):
        for change, message in (({"visibility": "public"}, "visibility differs"),
                                ({"tag_sha": "b" * 40}, "tag commit"),
                                ({"existing": True}, "already exists")):
            with self.subTest(change=change):
                calls, _, _, error = self.scenario(**change)
                self.assertIn(message, str(error))
                self.assertTrue(all(method == "GET" for _, method, _ in calls))

    def test_publish_only_after_verified_draft_and_durable_intent(self):
        calls, report, saved, error = self.scenario()
        self.assertIsNone(error)
        self.assertEqual(report["status"], "passed")
        self.assertEqual([row["status"] for row in saved], ["creating-draft", "uploading", "verified-draft", "passed"])
        self.assertEqual([method for _, method, _ in calls if method != "GET"], ["POST", "PATCH"])

    def test_interrupted_upload_preserves_draft_id_and_never_publishes(self):
        calls, report, saved, error = self.scenario(upload_failure=True)
        self.assertIn("upload interrupted", str(error))
        self.assertEqual(report["release_id"], 1)
        self.assertEqual(saved[-1]["status"], "uploading")
        self.assertFalse(any(method == "PATCH" for _, method, _ in calls))


if __name__ == "__main__":
    unittest.main()

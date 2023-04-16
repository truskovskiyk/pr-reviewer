from typing import Any, Dict, Union
import pytest
from unittest.mock import MagicMock, patch
from pr_review_bot import analyze_pr, submit_review
from typer.testing import CliRunner
from pr_review_bot import app


runner = CliRunner()

@pytest.fixture
def mock_pr() -> MagicMock:
    pr = MagicMock()
    pr.body = "This is a test PR description."
    pr.number = 1
    return pr

@pytest.fixture
def mock_file() -> MagicMock:
    file = MagicMock()
    file.filename = "file1.txt"
    file.status = "added"
    file.patch = "This is a test patch."
    return file

def test_analyze_pr(mock_pr: MagicMock, mock_file: MagicMock) -> None:
    with patch("pr_review_bot.ghapi") as mock_ghapi:
        mock_ghapi.pulls.list_files.return_value = [mock_file]
        mock_ghapi.issues.list_comments.return_value = []

        with patch("pr_review_bot.openai") as mock_openai:
            response_mock = MagicMock()
            response_mock.choices = [
                    MagicMock(
                        message={
                            "role": "assistant",
                            "content": "This is a test review."
                        },
                        finish_reason="stop",
                        index=0
                    )
                ]
            response_mock.usage = {"prompt_tokens": 56, "completion_tokens": 31, "total_tokens": 87}
            mock_openai.ChatCompletion.create.return_value = response_mock

            review = analyze_pr(mock_pr)
            assert "This is a test review." in review["body"]


def test_submit_review(mock_pr: MagicMock) -> None:
    review = {"body": "This is a test review.", "event": "COMMENT"}

    with patch("pr_review_bot.ghapi") as mock_ghapi:
        submit_review(mock_pr, review)
        mock_ghapi.pulls.create_review.assert_called_once_with(mock_pr.number, body=review["body"], event=review["event"])


def test_review_all_open_pr(mock_pr: MagicMock) -> None:
    with patch("pr_review_bot.get_open_prs") as mock_get_open_prs:
        mock_get_open_prs.return_value = [mock_pr]
        
        with patch("pr_review_bot.analyze_pr") as mock_analyze_pr:
            mock_analyze_pr.return_value = {"body": "This is a test review.", "event": "COMMENT"}
            
            with patch("pr_review_bot.submit_review") as mock_submit_review:
                result = runner.invoke(app, ["review-all-open-pr"])
                assert f"Review submitted for PR #{mock_pr.number}" in result.output

def test_review_pr(mock_pr: MagicMock) -> None:
    with patch("pr_review_bot.ghapi") as mock_ghapi:
        mock_ghapi.pulls.get.return_value = mock_pr
        
        with patch("pr_review_bot.analyze_pr") as mock_analyze_pr:
            mock_analyze_pr.return_value = {"body": "This is a test review.", "event": "COMMENT"}
            
            with patch("pr_review_bot.submit_review") as mock_submit_review:
                result = runner.invoke(app, ["review-pr", str(mock_pr.number)])  # Convert input to string
                assert f"Review submitted for PR #{mock_pr.number}" in result.output



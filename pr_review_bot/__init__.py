import openai
from ghapi.all import GhApi
from pydantic import BaseSettings
import typer
from typing import Optional, List, Dict, Any, Union

class Settings(BaseSettings):
    TOKEN: str
    OPEN_AI_KEY: str
    OWNER: str
    REPO_NAME: str
    PRICE_PER_TOKEN: float = 2.0000000000000002e-07
    MODEL_NAME: str = "gpt-3.5-turbo"

    class Config:
        env_file = '.env'
        env_prefix = "PR_REVIEW_BOT_"

settings = Settings()

openai.api_key = settings.OPEN_AI_KEY
ghapi = GhApi(token=settings.TOKEN, owner=settings.OWNER, repo=settings.REPO_NAME)

app = typer.Typer()

def get_open_prs() -> List[Any]:
    return ghapi.pulls.list(state='open')

def analyze_pr(pr: Any) -> Dict[str, Union[str, float]]:
    pr_description = pr.body

    # Read all PR files
    pr_files = ghapi.pulls.list_files(pr.number)
    pr_content = "\n".join(f"filename: {file.filename}: status: {file.status} patch: {file.patch}" for file in pr_files)

    # Read all PR comments
    comments = ghapi.issues.list_comments(pr.number)
    pr_comments = "\n".join(comment.body for comment in comments)

    text = f"pr_description\n {pr_description}, \npr_content\n = {pr_content}, \npr_comments\n = {pr_comments}"

    messages = [
        {"role": "system", "content": "You are github PR reviwer assistant."},
        {"role": "user", "content": f"Analyze this pull request text and provide a review:\n\n{text}"}
    ]

    response = openai.ChatCompletion.create(
        model=settings.MODEL_NAME,
        messages=messages,
    )

    review_cost = response['usage']['total_tokens'] * settings.PRICE_PER_TOKEN
    review = response.choices[0].message['content'].strip()
    review = f"Review \n\n{review}\n \n\nReview costs \n\n{review_cost} USD"

    event = "COMMENT"

    if "approve" in review.lower():
        event = "APPROVE"
    elif "request changes" in review.lower():
        event = "REQUEST_CHANGES"

    return {
        'body': review,
        'event': event
    }

def submit_review(pr: Any, review: Dict[str, Union[str, float]]) -> None:
    ghapi.pulls.create_review(pr.number, body=review['body'], event=review['event'])

@app.command()
def review_all_open_pr() -> None:
    open_prs = get_open_prs()
    for pr in open_prs:
        review = analyze_pr(pr)
        if review:
            submit_review(pr, review)
            typer.echo(f"Review submitted for PR #{pr.number}")

@app.command()
def review_pr(pr_number: Optional[int] = typer.Argument(None)) -> None:
    if pr_number is not None:
        pr = ghapi.pulls.get(pr_number)
        review = analyze_pr(pr)
        if review:
            submit_review(pr, review)
            typer.echo(f"Review submitted for PR #{pr.number}")
    else:
        typer.echo("Please provide a valid PR number.")

if __name__ == "__main__":
    app()

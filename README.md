# pr-reviewer

Streamline Your GitHub Pull Requests with AI, co-authored with GPT4.

## Install

```
pip install pr-review-bot
```


## Setup

```
export PR_REVIEW_BOT_TOKEN='your github token'
export PR_REVIEW_BOT_OPEN_AI_KEY='your open ai key'
export PR_REVIEW_BOT_OWNER='github user'
export PR_REVIEW_BOT_REPO_NAME='github repo'
```

How to get [Github token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
How to get [Open AI key](https://platform.openai.com/account/api-keys)


## Usage

To review all open pull requests:

```
pr-review-bot review-all-open-pr
```

To review a specific pull request:

```
pr-review-bot review-pr <PR nuber>
```

For help:


```
pr-review-bot --help
```

## Testing 


```
pytest --cov=pr_review_bot test_pr_review_bot.py
```

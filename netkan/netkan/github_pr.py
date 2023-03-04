import logging
from typing import Optional, List, Dict, Any
from github import Github, GithubException
from github.Repository import Repository

from .common import USER_AGENT


class GitHubPR:
    token: str
    git_repo: str
    user: str
    _repo: Repository

    def __init__(self, token: str, repo: str, user: str) -> None:
        self.token = token
        self.git_repo = repo
        self.user = user

    @property
    def repo(self) -> Repository:
        if getattr(self, '_repo', None) is None:
            self._repo = Github(self.token, user_agent=USER_AGENT).get_repo(
                f'{self.user}/{self.git_repo}')
        return self._repo

    def create_pull_request(self, title: str, branch: str, body: str, labels: Optional[List[str]] = None) -> None:
        try:
            pull = self.repo.create_pull(title, body, 'master', branch)
            logging.info('Pull request for %s opened at %s',
                         branch, pull.html_url)

            if labels:
                # Labels have to be set separately
                pull.set_labels(*labels)

        except GithubException as exc:
            logging.error('Pull request for %s failed: %s',
                          branch, self.get_error_message(exc.data))
            for pull in self.repo.get_pulls(head=f'{self.repo.owner}:{branch}'):
                # Post description as a comment if pull request exists
                pull.create_issue_comment(body)

    @staticmethod
    def get_error_message(exc_data: Dict[str, Any]) -> str:
        return ' - '.join([exc_data.get('message',
                                        'Unknown error'),
                           *(err['message']
                             for err in exc_data.get('errors', [])
                             if 'message' in err)])

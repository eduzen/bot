import pytest

from eduzenbot.plugins.commands.hackernews.command import hackernews


@pytest.mark.vcr()
def test_hackernews():
    msg = hackernews()

    assert "*Topstories stories from* [HackerNews](https://news.ycombinator.com)\n" in msg

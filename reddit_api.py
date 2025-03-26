import praw
from config import *
from tqdm.notebook import tqdm
import pandas as pd
from datetime import datetime


START_DATE = 1677625200  #March 1st
END_DATE = 1679698800    #March 25th
KEYWORDS = ['svb', 'silicon valley bank']


def get_posts(subreddit: str, include_comments: bool = False) -> pd.DataFrame:
    """Fetching all posts and comments from a subreddit."""
    data = []
    submissions = reddit.subreddit(subreddit).new(limit=None)

    for submission in tqdm(submissions):
        if submission.created_utc > END_DATE:
            continue
        elif submission.created_utc < START_DATE:
            break

        if submission.author:
            svb = int(any(k in submission.title.lower() or k in submission.selftext.lower() for k in KEYWORDS))
            data.append({
                'datetime': submission.created_utc,
                'type': 'post',
                'id': submission.id,
                'author': submission.author.name,
                'parent_id': None,
                'parent_author': None,
                'link_id': None,
                'score': submission.score,
                'svb': svb
            })

        if include_comments:
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                if comment.created_utc > END_DATE:
                    continue
                elif comment.created_utc < START_DATE:
                    break

                if comment.author and comment.author.name != 'AutoModerator':
                    data.append({
                        'datetime': comment.created_utc,
                        'type': 'comment',
                        'id': comment.id,
                        'author': comment.author.name,
                        'parent_id': comment.parent_id,
                        'parent_author': comment.parent().author.name if comment.parent().author else submission.author,
                        'link_id': comment.link_id,
                        'score': comment.score,
                        'svb': svb
                    })

    posts = pd.DataFrame(data)
    posts['datetime'] = posts['datetime'].apply(datetime.fromtimestamp)
    posts.set_index('datetime', inplace=True)

    return posts

def get_post_content(post_id: str, include_comments: bool = False) -> praw.models.Submission:
    """Get submission content using their ID."""
    submission = reddit.submission(post_id)
    if include_comments:
        submission.comments.replace_more(limit=None)
    return submission


# Calling the initializer
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=f"Comment Extraction (by u/{USERNAME})",
)

# Fetching posts and comments on the Economics subreddit and write them to a file
posts = get_posts('Economics', include_comments=True)
posts.to_csv('data.csv')


# Extract information from a post
post_id = '12110vv'
post = get_post_content(post_id, include_comments=True)
print('Post title:', post.title)
print('Post content:', post.selftext)

# Print comments
for comment in post.comments:
    if comment.author and comment.author.name != 'AutoModerator':
        print('Comment content:', comment.body)

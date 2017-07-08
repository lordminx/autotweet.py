# autotweet.py
A CLI script written in python which tweets/toots based on an RSS/Atom feed.

## Installation

`git clone` this repository and then run `pip install -r requirements.txt` to get the necessary libraries. Doing that in a virtual environment is probably a good idea.

## Usage

```
Usage:
    autotweet [-hc CONFIG] [ tweet | toot | all ]

    -h --help   Print out this help message.
    -c FILE     Specify config file. [default: ./autotweet.json]
    tweet       Post to Twitter.
    toot        Post to Mastodon.
    all         Post to all configured sites.
```

See the example config file `autotweet.json` for how the config file is structured. To send tweets, you will need to register a new twitter app at [dev.twitter.com](https://dev.twitter.com) to get the CONSUMER_KEY and CONSUMER_SECRET as well as get the OAUTH tokens for the Twitter account you want to use. For an example how that could work see the [Python twitter Tools documentation](https://github.com/sixohsix/twitter).

To get the Mastodon credential files see the [Mastodon.py docs](http://mastodonpy.readthedocs.io/en/latest/).

I start this script from a post-receive hook on the git repo where my blog lives, so that it automatically tweets when I push a new blogpost.

## Todo

* Better documentation.
* Less `print` statements.
* Proper logging.

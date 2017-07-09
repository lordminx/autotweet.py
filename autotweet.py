#!/usr/bin/env python
# coding: utf-8

"""\
Usage:
    autotweet [-hc CONFIG] [ tweet | toot | all ]

    -h --help   Print out this help message.
    -c FILE     Specify config file. [default: ./autotweet.json]
    tweet       Post to Twitter.
    toot        Post to Mastodon.
    all         Post to all configured sites.

"""


import sys
import json
import feedparser
import docopt

from urllib.parse import urlparse, urljoin
from twitter import *
from mastodon import Mastodon
from bs4 import BeautifulSoup

import requests as r


defaultconf = {
        "template":'"{}"\n{}'
}


def loadjson(conf):
    """ Load json-formatted config file."""
    with open(conf) as f:
        conf = json.load(f)
        defaultconf.update(conf)
    return defaultconf

def checkfeed(feed):
    """ Load and parse the given rss/atom feed."""

    root = "://".join(urlparse(feed)[:2])

    fp = feedparser.parse(feed)

    title = fp["entries"][0]["title"]
    link = fp["entries"][0]["link"]
    content = fp["entries"][0]["summary"]

    print("Feed fetched and parsed.")


    """ Check post for image links."""

    soup = BeautifulSoup(content, "html.parser")

    if soup.img:
        src = soup.img["src"]
        print("Image link found.")

        if src[0] == "/":       # relative link
            src = urljoin(root, src)

    else:
        src, img, mime = None, None, None

    if src:
        res = r.get(src)
        if res.status_code == 200:
            img = res.content
            mime = res.headers["Content-Type"]
            print("Image downloaded.")

    return title, link, content, img, mime

def makepost(title, link, config, content=None):
    """ Build tweet/toot text. """
    return config["template"].format(title, link, content)

def twitterconf(config):
    """Extract Twitter connection data from config dict."""
    tc = config["twitter"]
    keys = ["OAUTH_TOKEN",
            "OAUTH_SECRET",
            "CONSUMER_KEY",
            "CONSUMER_SECRET"]

    return tuple([tc[key] for key in keys])


def tweet(post, conf, img=None):
    """ Post to Twitter."""

    # extract twitter confg values
    conf = twitterconf(config)

    # Create Twitter connection
    t = Twitter(auth=OAuth(*conf))

    # make twitter post
    if img:
        print("Uploading Image to Twitter...")
        t_upload = Twitter(domain='upload.twitter.com', auth=OAuth(*conf))
        img_id = t_upload.media.upload(media=img)["media_id_string"]
        print("Done.")

    print("Tweeting...")

    if img:
        t.statuses.update(status=post, media_ids=",".join([img_id]))
    else:
        t.statuses.update(status=post)

    print("Done.")

def mastodonconf(config):
    """Extract Mastodon connection data from config dict."""
    conf = config["mastodon"]
    keys = ["clientfile", "userfile"]

    return tuple([conf[key] for key in keys])

def toot(post, config, img=None, mime=None):
    """Post to Mastodon."""
    try:
        clientfile, userfile = mastodonconf(config)

        # Create Mastodon Connection
        m = Mastodon(client_id=clientfile, access_token=userfile)

        # make mastodon post
        if img:
            print("Uploading Image to Mastodon...")
            media = m.media_post(media_file=img, mime_type=mime)
            print("Done.")

        print("Tooting...")

        if img:
            m.status_post(post, media_ids=[media["id"]])
        else:
            m.toot(post)

        print("Done.")
    except Exception as e:
        print(e, file=sys.stderr)
        print()
        print("Sending Mastodon Message failed: Please check the config for errors and try again.", file=sys.stderr)


if __name__ == "__main__":
    options = docopt.docopt(__doc__)

    try:
        config = loadjson(options["-c"])
    except OSError as e:
        print(e)
        sys.exit()

    try:

        feed = config["feed"]

        title, link, content, img, mime = checkfeed(feed)

        post = makepost(title, link, config)

    except IndexError:
        print("Feed could not be loaded.")
        sys.exit()

    if options["tweet"]:
        tweet(post, config, img)

    if options["toot"]:
        toot(post, config, img, mime)

    if options["all"]:
        toot(post, config, img, mime)
        tweet(post, config, img)

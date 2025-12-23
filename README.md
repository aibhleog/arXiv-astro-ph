# arXiv-astro-ph

playing around with pulling code from arXiv to post new JWST extragalactic papers to slack workspaces


### where taylor is

okay, so I got the code up and running, but for integrating this code into Slack (to work like an app that can run on a schedule, without human interaction), I've hit a few snags:

* If I run the app in my terminal, linked to the Slack workspace I've chosen, then calling the app will run the code -- _however_, I don't yet know how to make it run without the terminal active.  I think this may require HTTPS linking instead of the socket mode (which I believe is just for local development testing).
* Before fixing that/trying that switch out, I realized that the selenium scraping code I have written will still require opening a browser & all of that.  I MAY be able to do a headless version -- ignoring that generally such a thing is not recommended -- but I encountered another issue:
* The export.arxiv.org API-friendly website I use to scrape the postings (which I learned existed the hard way 5yrs ago lol, see arXiv-order repository) looks like it's a week behind the real arxiv.org astro-ph new listings?  Which, if so, makes this plan useless unless I want to risk using the real site.


### Tabling for now until I have energy again lol this series of snags made me lose steam.
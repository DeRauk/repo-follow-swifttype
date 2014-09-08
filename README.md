RepoFollow
=====================

A Twitter-style commit reader. Enjoy!


* [Setup](https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#setup)
* [How to Use It](https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#how-to-use-it)
* [Scaling] (https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#scaling)
* [Design Decisions] (https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#design-decisions)
* [Bugs and Things I Could Have Done Better](https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#bugs-and-things-i-could-have-done-better)
* [What it Doesn't Do] (https://github.com/DeRauk/repo-follow-swifttype/blob/master/README.md#what-it-doesnt-do)


## Setup
I used postgres as a backend persistent store and memcached as my cache.  Both of these will need to be installed.

#### Postgres
The postgres settings can be found at /repofollow/repofollow/settings.py on line 121. You'll need to update the user, password, schema name, and possibly host and port.

#### Memcached
The Memcached settings can be found at /repofollow/repofollow/settings.py on line 88. You might need to change the host on port, I have them set as the default.

#### Python libraries
1. If you're using virtualenv, start a new virtual environment and activate it.
2. Install everything in the requirements file at /docs/requirements.txt with pip. `pip install -r requirements.txt`

### Database Setup
After installing postgres, you can run the setup script in /repofollow/, `./setup`.  This will sync up the database and create users.

## How to Use It
1. Run the devrun script in /repofollow `./devrun`
2. Navigate to localhost:8000 in a browser
3. login with "derauk/derauk" or "swifttype/swifttype"
4. Paste a github repository url in the text input on the header and click follow
5. Choose your branches from the modal dialog
6. Click on your username in the top right on the nav bar and select "Manage Repositories"
7. You can edit branches or delete repositories from this page

## Scaling
I specifically tried started tackling two bottlenecks.

### Bottleneck 1: Rate Limiting
The biggest bottleneck to me, when scaling to thousands of users, is definitely the rate limit on Github's apis.  With an authorized app I have 5000 requests an hour, which would be pretty hard to distribute across a thousand users with a real time feed. I did the following:

1. Put all repositories, branches, and commits in my local database to limit the information I need to get from the Github api
2. Made it less real time.  I only allow a repository to check for updates every 30 seconds, this could be designed to dynamically grow and shrink based on how many repositories I'm keeping track of.
3. Make sure there was a push to the repository before getting updated information about branches and commits. If there wasn't, I only used one rate-limit currency thing-a-majig instead of one for each branch + 1 for the commits.
4. Only ask Github for commits created later than the latest commit we have in the database. This reduces the number of pages/rate limits we use. (My objective here was to only get new commits, but it's faulty logic, I explain more in the bugs section.)  Because of this, I don't limit how far back we store commits.  We don't lose much by this, except our database tables getting too large, and for that we could just add older history tables that perform a little worse and keep the 'current' commits table small and fresh.

### Bottleneck 2: The Database
Easy answer, but I'll take a freebie when I can get it. I added in a caching framework to avoid database hits when possible and use it in 2 places:

1. Sessions: Session information is high read low write and it's not a big deal if we lose it if/when Memcached goes down. No brainer.
2. My commit html blocks - In /repofollow/commitfollower/templates/commitfollower/commit_list.html. The newsfeed is a series of blocks displaying commit information. I cache the html in that block with a key of {repository name}-{commit sha}.  Commit html blocks won't change from a repository update from the apis or when a different user is viewing it.

There's a lot more places that could and should be cached, given time. My goal was to do enough to show competency with caching.

## Design Decisions
I wanted to write down some reasoning behind my design and some tradeoffs I thought about. 

### Database Design
There's 4 main models: User, Repository, Branch, Commit.  Note that user refers to a repo-follow user and is not synonymous with a Github user. The important relations are:

* Repository has a one-to-many relationship with Branch
* Branch has a one-to-many repository with Commit
* Branch has a many-to-many relationship with User

I think this design is solid up until you start getting around the hundred-thousand user mark.  If you have 100k users following 100s of repos each you're getting to 10s of millions of records in the user to branch many to many table. At that point some options:

* Denormalize: I already opted out of creating Github users in the database and just put any data describing them in with their commit.  But, I think I could also denormalize Repository and Branch to just a Branches table.  One less fk lookup would help out with performance.
* Partition: Spread the database across multiple servers. Maybe put users starting with a-f on db 1 and users starting with g-m on db 2 etc... Then have a lookup to find out which db a user is based on the first letter of their name.  The same could go for repository or branch names.
* Look to NOSQL.  I could offload the users-branches m2m table to a good key-value store since it's just a 2 column table,  I think that would get pretty messy though and wouldn't be worth it since it limits what I can do with my sql queries.  I might look into using a document store instead.

Of course, I would profile all of these options to get the best combination.

### Code Design
I just wanted to point out one thing I consciously coded toward since I started.  I currently use both Github and Bitbucket a lot, and it seemed at least possible that an app like this would want to add in support for other version control repositories (or systems).  So I made sure to abstract all of the Github api calls in their own class and write a VCSFollower class that the business logic calls into.  The VCSFollower inspects the repository url given to decide which apis to call. The Repositories tables also stores information on the type of vcs system and the site hosting it.  To add in another support for another host, say Bitbucket, I would just need to write a BitBucket class and tell the VCSFollower abstraction that repositories from bitbucket.com should use that class.


## Bugs and Things I Could Have Done Better
I had to cut the app off somewhere, and scope creep would have had me on this till Chrismas. So I gave in and opted to list the problems I know of here.
* Time Zones: They're inconsistent right now.  Everything should be in UTC, but I had a lot of trouble when telling Github how far back I wanted commits for.  Everything was off by 7 hours, even when I passed in the Time-Zone header they ask for...  I hacked it by asking for commits 12 hours earlier than I wanted to.  The worst thing that can happen that way is a couple extra rate limit hits.  Also, Timezones display in UTC time to the user, when they should display in local time.
* Missing Commits: I got around some rate limiting by only taking commits for a branch that are newer than the latest one we have in our database. However, it's perfectly possible and likely that someone will merge in a branch with commits older than the newest commit in that branch.  Which means I would never pick up those commits for that branch :/.

## What it Doesn't Do
Missing functions or features I'd like to add.
* Handle Deleted Repositories
* Show any activity other than commits (Like pull requests, commit comments, and more)
* Handle BitBucket repos (discussed in Code Design)

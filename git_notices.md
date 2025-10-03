## zero: add remote to github repo
git remote add <name> <url>
----

## first: add files to the git version
git add .

## second: commit the changes of files to the git version
git commit -m "message"

(-m stands for 'message')


## third: push the changes to github repo
git push <remote> <branch>

git push origin main

- "origin" is the name we gave to the current remote. A repo can have different remotes.
- "main" is the branch we are pushing the code to. A repo can have different branches for different purposes.

-----

# pull the repo code from another laptop/account/environment
## add remote to the repo
git remote add <name> <URL>

- <name> is the name we can custom give to the remote (commonly 'origin')
- <url> is the github https url of the remote

## pull the code
git pull (remote) (branch)
git pull origin main
#/!bin/bash

echo "Updating submodules: event_scraper, event_scraper_celery.."
cd /home/cheki/workspace/event_scraper_web/event_scraper
git pull --rebase origin master
git add .
git commit -m "Update event_scraper submodule"
git push origin master

cd /home/cheki/workspace/event_scraper_web/event_scraper_celery
git pull --rebase origin master
git add .
git commit -m "Update event_scraper_celery submodule"
git push origin master

echo "Removing notes.txt from repository.."
cd /home/cheki/workspace/event_scraper_web/webserver
git rm notes.txt
git commit -m "Remove notes.txt from repository and add to .gitignore"
git push origin master

echo "Pushing changes to event_scraper_web.."
cd /home/cheki/workspace/event_scraper_web
git submodule update --remote
git add .
git commit -m "Update submodules: event_scraper, event_scraper_celery"
git push origin main


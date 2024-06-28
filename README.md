# Space Ledger

### This is an application written in python using FastAPI to produce a website where people can compete and share information on trading runs done in games. Particularly written for my friend who plays Star Citizen.

## Project Description

After taking Python courses and a FastAPI course, I wanted to see if I could create a basic website that utilizes those skills. I'm working on getting into data, so I wanted to to have a database that got queried against and used in the process of the application. 

The layout of the website is very simple currently, using a very simple bootstrap and css layout but everything should be able to be navigated to using the Navbar and buttons currently 

The point of the website is for multiple users to be able to sign up and enter in information on different cargo runs they make in a game. You can only edit and delete your own, but there's a page to view everyone's currently. That way you can all benefit from seeing profitable runs.

There is also a page where you can view the months top contributors and also last months winners, incase you wanted to add a little competition into the mix. 

This webapp could easily be altered for any game. While I had space trucking in mind, there is no reason it couldn't be used for trading in other games as well. The database is flexible on its inputs.

## Standouts

The main point of this application to start was to work on my skills with databases and FastAPI. The layout and web design are a distant second. To that affect I accomplished my goal. 

The feature I'm most proud of in this app is the Leaderboard. It was much hard to put together than I thought it would be. Querying the database for last month and making a table for it was more difficult using SQLalchemy than I thought it should be. Learning to merge two different languages took some practice and questioning on StackOverflow. 

## Future Workings

I currently do not have a way to recover passwords if one is lost to the user. I played with emailing a user a reset link, but no matter what I did the route I used would cause a 404 error. I decided against it currently as I wasn't going to sign up to a SMTP Server for it anyways at this time. I will work on it in the future though.

The layout is barebones. It functions but is not pretty. I plan on spicing up the look the app. This will include a more "space" vibe and graphics to match.

I also want goods to be from a dropdown menu. There is no good way to scrape StarCitizen files that I know of, so prices need to be done manually still I think.

Something is weird with my time column. I'm not sure where to start with it but it's thinking it's a 24:00 hour cycle. No run should take over 24 hours so it isn't a big deal currently. But for consistency and accuracy I need to look into it. The time formats gave me issues the whole way.

## Utilization

Clone the repository and open the folder in your favorite Python IDE. Make sure to install dependencies in your terminal from Requirements.txt using:
```
pip install -r requirements.txt
```
After requirements are installed run:
```
uvicorn main:app --reload
```
This should launch the app. As long as no errors occur you should be able to click the link or go to http://127.0.0.1:8000 on your browser to launch the app.

Once there, there are two users in the database you can log in as: Zot and Phorvuld. Both should have a password of Trial123! Feel free to make a new user too!

## Credits
I highly studied Eric Roby's code, using snippits of it, from his FastAPI course and used his Bootstrap and CSS from his last project. That has plans to be replace and not sure if it is his but giving credit just incase.
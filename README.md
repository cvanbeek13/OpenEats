# Cvanbeek13 Fork

With this Fork I'm trying to get OpenEats running on a Raspberry Pi 4 running the standard Raspberry Pi OS (32-bit).  This website will be used
by a few members of my family including my mom who is an avid cook.  Here are my goals for this fork:

## Initial Goals

- [x] Run OpenEats on the Raspberry Pi and access the web server from my local network
- [ ] Import my Mom's existing recipes from her [Cook'n](http://www.dvo.com/?fbclid=IwAR1EH1wiRhb03MtFBsI7yXU9zqk__C5YiUEas-ax4ck2d0dU11LlopQnyJY) software
- [ ] Purchase a domain and run my fork through that so it can be accessed off the network
- [ ] Add SSL and a firewall to secure the server
- [ ] Develop a cron job for backing up the database to an external location.  I've had bad luck with RPi SD cards failing.
- [ ] Provide in-depth documentation of all these steps so others can do the same if desired

## Stretch Goals

- [ ] In the Browse Recipe's Page I want to add a way to filter Tags like you can with courses and cuisines.
- [ ] I would like to add my [Recipe Scraper Fork](https://github.com/cvanbeek13/recipe-scrapers) into a new import page.

# OpenEats Project

OpenEats is a recipe management site that allows users to create, share, and store their personal collection of recipes. This fork uses Django Rest Framework as a backend and React (with flux) as a front end.

The usage for the app is intended for a single user or a small group. For my personal use, I would be an admin user and a few (about 5-6) friends and family would be normal users. Admin users can add other users to the project (no open sign-ups), make changes to the available Cuisines and Courses, and add to the homepage banner. Normal users just have the ability to add recipes. Below are a few of the core features the app provides.

- Creating, viewing, sharing, and editing recipes.
- Update Serving information on the fly.
- Browsing and searching for recipes.
- Creating grocery lists.
- Automatically add recipes to your grocery lists.
- Quickly print recipe.
- Linking recipes and ingredient grouping.

### [Read the docs on getting started here!](docs/Running_the_App.md)

If you don't wish to use docker, see installation instructions here:
[Markdown](docs/Running_the_App_Without_Docker.md) OR [Media Wiki!](https://wiki.tothnet.hu/books/other/page/install-openeats-without-docker-and-run-on-apache2)


### [The Update guide can be found here!](docs/Updating_the_App.md)

# Contributing
Please read the [contribution guidelines](CONTRIBUTING.md) in order to make the contribution process easy and effective for everyone involved.

For a guide on how to setup an environment for development see [this guide](docs/Running_the_App_in_dev.md).

- [Running the App on Raspberry Pi (RPi)](#running-the-app-on-raspberry-pi-rpi)
  - [My Process to get OpenEats Running](#my-process-to-get-openeats-running)
    - [Project Structure](#project-structure)
    - [Containers and Dependencies](#containers-and-dependencies)
    - [Troubles and Workarounds with MariaDB](#troubles-and-workarounds-with-mariadb)
      - [Docker-Host](#docker-host)
  - [How to Start OpenEats from my Fork](#how-to-start-openeats-from-my-fork)
    - [Pulling the Projects](#pulling-the-projects)
    - [Installing MariaDb](#installing-mariadb)
    - [Configuring env Files](#configuring-env-files)
    - [Running in Development Mode](#running-in-development-mode)
    - [Seeding the Database](#seeding-the-database)
    - [Running in Production Mode](#running-in-production-mode)
    - [Other Recommendations](#other-recommendations)
    - [Additional Troubleshooting](#additional-troubleshooting)
      - [Images not Appearing](#images-not-appearing)

# Running the App on Raspberry Pi (RPi)

This doc page will go through the steps I took to get Raspberry Pi OpenEats running which deviated from the standard [OpenEats Repository](https://github.com/open-eats/OpenEats).  At the end it can be run and accessed by IP address from another machine on the same network.  I will also show the steps that you would need to take to run this fork on your own Raspberry Pi.

## My Process to get OpenEats Running

I ran into a number of issues when trying to run OpenEats on my Raspberry Pi, this section documents those issues and how I worked around them to get the app running on my local network.  I mostly followed the [Running_the_App_in_dev.md](Running_the_App_in_dev.md) instructions, but these are instances where I deviated from them.

### Project Structure

To start, all my forked repos were cloned to my RPi in the required locations.

```bash
git clone https://github.com/cvanbeek13/OpenEats.git
cd OpenEats
git clone https://github.com/cvanbeek13/openeats-api.git
git clone https://github.com/cvanbeek13/openeats-web.git
git clone https://github.com/cvanbeek13/openeats-nginx.git
```

I'm pretty new to Docker, and I didn't want to mess around with creating my own images and publishing to DockerHub.  To keep it simple, I modified my [docker-prod.yml](../docker-prod.yml) file to build the from local files instead of pulling images.  This wasn't an issue with how OpenEats worked but just a shortcut on my part that I wanted to acknowledge.

### Containers and Dependencies

The next step was running the app in dev mode with `docker-compose build` which was where I first ran into problems with all the repositories.  The API, web, and nginx (nginx isn't needed for dev mode but it failed later when building for production).  

I ended up updating container image versions for all three projects, as well as a dependency in the API project.  I didn't do more than the minimum changes to get it working.  I do know there are a number of very [outdated dependencies](https://github.com/open-eats/openeats-web/issues/55) in the OpenEats project, but I'm leaving them for now.  Here are the changes I made to each project's Dockerfile.

| Project | Original | Updated to |
| ----- | ----- | ----- |
| API | Used `python:3.6.5-alpine3.7` container | Changed to `python:3.9.0-alpine3.12` container |
| API | Used `py-mysqldb` library | Changed to `py3-mysqlclient` |
| Web | Used `node:8.11.1-alpine` container | Changed to `node:10-alpine3.11` container |
| Web | Build failures due to `node-sass` | Added `RUN apk update && apk add yarn python2 g++ make && rm -rf /var/cache/apk/*` to the [Dockerfile](https://github.com/cvanbeek13/openeats-web/blob/bringup-rpi/Dockerfile) |
| Nginx | Used `nginx:1.13.8-alpine` | Changed to `nginx:1.19-alpine` |

### Troubles and Workarounds with MariaDB

After fixing the container versions, I still had problems with running the db image.  I tried a couple other images (like [this fork](https://github.com/Slinky-Wrangle-Punch/OpenEats/blob/master/docs/Setting_up_env_file.md) did), but eventually decided it would be easier to just host the database on my Raspberry Pi and allow the Docker container to access it.

For installing MariaDb, I mostly followed [this blog](https://pimylifeup.com/raspberry-pi-mysql/) and I've listed these instructions later in this doc.

After setting up MariaDb, I had my own MySQL server running on port 3306 of the Raspberry Pi.  It had a user named `openeats` and a database named `openeats`.  In hind-site, that's confusing and you use different names if you'd like.

Since I'm technically now using a remote database, the [env_dev.list](../env_dev.list), [env_stg.list](../env_stg.list), and `env_prod.list` files all needed to be updated with this information.  They already has `MYSQL_DATABASE` and `MYSQL_ROOT_PASSWORD` fields which I updated.  I also added the `MYSQL_USER`, `MYSQL_HOST`, and `MYSQL_PORT` fields.  Here's what that part of those files looked like for me:

```
MYSQL_DATABASE=openeats
MYSQL_ROOT_PASSWORD=<redacted>

MYSQL_USER=openeats
MYSQL_HOST=dockerhost
MYSQL_PORT=3306
```

With the database setup, I removed the `db` Docker container from all the Docker `.yml` files.

#### Docker-Host

The issue with running the database on the RPi is since the API Docker container gets a separate IP, it can't access the database using `localhost:3306`.

To get around this, I used the [Docker-Host](https://github.com/qoomon/docker-host) project.  It was easy to add to the [docker-compose.yml](../docker-compose.yml), [docker-stage.yml](../docker-stage.yml), and [docker-prod.yml](../docker-prod.yml) files.  I added this container to each:

```yml
  dockerhost:
    image: qoomon/docker-host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: on-failure
```

In each `.yml` file, I also made the `api` container depend on the `dockerhost` container.

## How to Start OpenEats from my Fork

If you don't care about the changes I made and just want to get this thing running, this is where you should be.  I'll walk through the process to the best of my ability.  I haven't tried it on a fresh RPi, but these are all the steps I can remember.

One thing to note is my RPi is running on a static IP at `192.168.0.199`.  I recommend [these instructions](https://pimylifeup.com/raspberry-pi-static-ip-address/) for setting that up.

### Pulling the Projects

Run the following commands to pull all the source code for my forks:

```bash
git clone https://github.com/cvanbeek13/OpenEats.git
cd OpenEats
git clone https://github.com/cvanbeek13/openeats-api.git
git clone https://github.com/cvanbeek13/openeats-web.git
git clone https://github.com/cvanbeek13/openeats-nginx.git
```

### Installing MariaDb

Run these commands to start the MariaDb installation:

```bash
sudo apt install mariadb-server
sudo mysql_secure_installation
```

The second command prompts you to provide a password for the root user, and runs you through a list of security questions.  Make sure you remember this password.  Answering yes to all the questions should make this the most secure installation.

When finished, open MySQL as the root user (you'll be prompted for the password you just created):

```sh
sudo mysql -u root -p
```

Next we will create a database and user (with a different username and password than root) which OpenEats will access.  For this example, I'm sticking with the username `openeats` and database also named `openeats`.  Password is replaced with `<password>` so use your own new one in its place.  Run these SQL commands to create the database and user:

```sql
CREATE DATABASE openeats;
CREATE USER 'openeats'@'localhost' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON openeats.* TO 'openeats'@'%' IDENTIFIED BY '<password>';
FLUSH PRIVILEGES;
```

You can then exit MySQL by running `exit`.

By default, MariaDb only allows the server to be accessed from `localhost`.  We need to override this in the conf files so the Docker container has access.  This is often done in the `/etc/mysql/my.cnf` file, but for me, the line I needed to change was in `/etc/mysql/mariadb.conf.d/50-server.cnf`.  Find the line that defines `bind-address` and change it to `0.0.0.0`.

### Configuring env Files

The first step is creating the `docker-prod.override.yml` and `env_prod.yml` files by copying them from the samples folder:

```bash
cp docs/samples/sample_docker_prod_override.yml docker-prod.override.yml
cp docs/samples/sample_env_file.list env_prod.list
```

The `env_dev.list`, `env_stg.list`, and `env_prod.list` files will all need to be edited with your value of `MYSQL_ROOT_PASSWORD` and `DJANGO_SECRET_KEY`.  Here are [some instructions](https://stackoverflow.com/a/16630719/7274584) to generate a secret key.  If you used a different database name or user, update those fields as well.

If you didn't use `192.168.0.199` as your static IP address for the RPi, you will need to update the `ALLOWED_HOST` and `NODE_API_URL` variables as well in `env_stg.list` and `env_prod.list`.

### Running in Development Mode

At this point we should be able to build and run OpenEats in dev mode and access it from the Raspberry Pi's web browser.  Run these commands to build and run Openeats:

```bash
docker-compose build
docker-compose up
```

Then in the RPi, open the Chromium Web browser and type `http://localhost:8080` into the url.  It won't be accessible from another machine on the network yet.

### Seeding the Database

As in the Directions for the [Running the App](Running_the_App.md#First-Time-Setup) instructions, you must create a superuser and seed the database.  This can be done in dev mode and is probably a little faster to do here.  Run these commands:

``` bash
docker-compose run --rm --entrypoint 'python manage.py createsuperuser' api
docker-compose run --rm --entrypoint 'sh' api
./manage.py loaddata course_data.json
./manage.py loaddata cuisine_data.json
./manage.py loaddata news_data.json
./manage.py loaddata recipe_data.json
./manage.py loaddata ing_data.json
```

### Running in Production Mode

With the database seeded we can run in production mode and access the website while on the same network.  Run these commands to build and run the app in production mode:

```bash
docker-compose -f docker-prod.yml -f docker-prod.override.yml build
docker-compose -f docker-prod.yml -f docker-prod.override.yml up
```

From another computer, open a web browser and navigate to `http://192.168.0.199:8000`, using the IP address of the RPi and port 8000.

### Other Recommendations

I'm not a security expert, and based on how old some of these dependencies are, I wouldn't fully trust the security of OpenEats.  Therefore, I setup my Raspberry Pi to require a password for `sudo` calls.  It's an extra percaution that I'd recommend for others as well.  Simply run `sudo visudo /etc/sudoers.d/010_pi-nopasswd` and change the `pi` line to `pi ALL=(ALL) PASSWD: ALL`.

As I make changes I'll do my best to keep this up to date.  I'll also try to keep the `bringup-pi` branches on all my projects around and stable for bringing up a basic build like this.

### Additional Troubleshooting

I did have a other issues which I'm not sure are related to the Raspberry Pi project, or Open-Eats in general

#### Images not Appearing

Images I added to my recipes weren't appearing.  I found the solution in this closed issue on the OpenEats project helpful.  To fix it, I opened sh on the docker api container:

```bash
docker-compose -f docker-prod.yml -f docker-prod.overwrite.yml run --rm --entrypoint 'sh' api
```

And once inside the shell, change the permissions of the site-media folder:

```bash
chmod -R 755 /code/site-media/
```

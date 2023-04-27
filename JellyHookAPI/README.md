# JellyHookAPI

This is a Flask API that gather all the necessary information from Jellyfin and allow you to send to any other API you want.

*For now, the collected information is only for "item added".*

So the goal is simple: on Jellyfin you'll add only one webhook, [this one](../webhooks/jellyfin/global-item.handlebars), and then you modify [jellyhookapi.py](ellyhookapi.py) to add your function to send a requests to your desired API.

The [global-item](../webhooks/jellyfin/global-item.handlebars) webhook has:

- this "Webhook Url": `http://10.10.66.199:7777/api` (internal docker subnet ip - unless you changed)
- this "Request Header": Key:`Content-Type`, Value:`application/json`

To modify the program in order to send the information to your API, you need to create a new function (take example on the existing one), and add the call to this function in the `receive_data()` function (instead of or under the existing one).

## Build

To build and run the API, follow these steps:

```bash
$ cd JellyHookAPI
$ docker-compose build
$ docker-compose up -d
# and check if everything is fine
$ docker-compose ps -a
```

If you have modified the program and want to restart the API with the new modifications:

```bash
$ cd JellyHookAPI
$ docker-compose down
$ docker-compose rm jellyhookapi # or $ docker rm jellyhookapi
$ docker images     # list images
$ docker rmi -f jellyhookapi-jellyhookapi   # delete the image (it can be another name, you can also use the IMAGE ID instead)
```

Now you can build again the image.


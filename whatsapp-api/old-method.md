# Old Method - Whatsapp Webhook

> [!WARNING]
> ***Old method - please refer to the [new and better method](README.md#whatsapp-api).**

To add a **WhatsApp** webhook:

Not as easy as the others.

You need to connect your WhatsApp account as if you were logging on WhatsApp Web.

To achieve this, you're going to use another docker-compose to self-host a WhatsApp HTTP API. I'm using [this API](https://github.com/devlikeapro/whatsapp-http-api).

Follow these steps:

```bash
$ cd /opt/chill
$ wget https://raw.githubusercontent.com/garnajee/home-server/master/whatsapp-api/old-method-docker-compose-whatsapp.yml
$ docker-compose --file old-method-docker-compose.yml up -d
```

> [!NOTE]
> Note that the docker-compose I provided is not really optimized, you can add environment variable to better configure. You can check the documentation [here](https://waha.devlike.pro/docs/how-to/config/).


Then follow the [official](https://github.com/devlikeapro/whatsapp-http-api#3-start-a-new-session) from step **3** to **5**. For any further information, like the id of a contact or a group, please read the [documentation](https://waha.devlike.pro/docs/how-to/).

Go back to Jellyfin > Plugin > Webhook:

- click on "Add Generic Form Destination"
- "*Webhook Url*": the **internal** docker ip, if you don't change anything in the docker-compose it should be: `http://10.10.66.200:3000/api/sendText`
- then check what you want depending on the template

Then copy and paste the template you want:

1. "*Item Added*": [whatsapp-items.handlebars](../webhooks/jellyfin/whatsapp/whatsapp-items.handlebars)
2. (very basic) "*User created/deleted*": [whatsapp-basic-user.handlebars](../webhooks/jellyfin/whatsapp/whatsapp-basic-user.handlebars)

And finally you need to 2 Headers:

1. "*Key*": "accept", "*Value*": "application/json"
2. "*Key*": "Content-Type", "*Value*": "application/json"

> [!IMPORTANT]
> Please note, that we cannot send images with this API (it's a paid feature).
>
> (The new method can).

And that's it, you can save.


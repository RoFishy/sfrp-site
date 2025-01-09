from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
import aiohttp
from dotenv import dotenv_values
config = dotenv_values(".env")

app = Quart(__name__)
app.config["SECRET_KEY"] = str(config["SECRET_KEY"])
app.config["DISCORD_CLIENT_ID"] = int(config["DISCORD_CLIENT_ID"])
app.config["DISCORD_CLIENT_SECRET"] = str(config["DISCORD_CLIENT_SECRET"])
app.config["DISCORD_REDIRECT_URI"] = str(config["DISCORD_REDIRECT_URI"])

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    return await render_template("index.html", authorized = await discord.authorized)

@app.route("/login")
async def login():
    return await discord.create_session()

@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except:
        return redirect(url_for("login"))
    
    return redirect(url_for("staff"))

@app.route("/invalid")
async def invalid():
    return await render_template("invalid.html")

@app.route("/staff")
async def staff():
    if not await discord.authorized:
        return redirect(url_for("login"))
    try:
        user = await discord.fetch_user()
    except:
        return redirect(url_for("login"))
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url="http://127.0.0.1:8080/staff_check", params={"id": user.id}) as resp:
            if resp.status == 200:
                value = await resp.json()
                if value["value"] == "False":
                    return redirect(url_for("invalid"))
                else:
                    return await render_template("staff.html", username=user.name)

if __name__ == "__main__":
    app.run(debug=True)
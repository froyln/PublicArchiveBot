import main
import discord
from discord.ext import commands
from discord import app_commands
import buttons.ThreadButtons as btnThread

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="###", intents=intents)

TOKEN = main.TOKEN
ForumId = main.ForumId
MemberRoleId = main.MemberRoleId

# Create the post
@bot.tree.command(name="post", description="Create an a post in public archive")
@app_commands.describe(
    title="Post Title", 
)
@app_commands.checks.has_role(MemberRoleId)
async def post(
    interaction: discord.Interaction,
    title: str, 
):
    await interaction.response.defer(ephemeral=True) 
    ForumChannel = interaction.client.get_channel(ForumId)

    try:
        # create the thread
        buttons = btnThread.ThreadButtons()
        if isinstance(ForumChannel, discord.ForumChannel):
            thread_with_message = await ForumChannel.create_thread(
                name=title,
                view=buttons
            )
        await interaction.followup.send(f"Post '{title}' created.", ephemeral=True)
        print(f"Post {title} created")
    except Exception as e:
        await interaction.followup.send(f"Exception: {e}", ephemeral=True)

#error message
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # missing role
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message(
            f"You are not a Member, you can't execute this command", 
            ephemeral=True
        )
    else:
        print(f"Error en comando: {error}")

@bot.event
async def on_ready():
    bot.add_view(btnThread.ThreadButtons())
    print(f'{bot.user} Ready.')
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands ready: {len(synced)}")
    except Exception as e:
        print(f"Slash command error: {e}")

bot.run(TOKEN)
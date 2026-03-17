import discord
from discord.ext import commands
from discord import app_commands
import os 
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="###", intents=intents)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ForumId = int(os.getenv("FORUM_ID"))
MemberRoleId = int(os.getenv("MEMBER_ROLE_ID"))

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
        buttons = ThreadButtons()
        if isinstance(ForumChannel, discord.ForumChannel):
            thread_with_message = await ForumChannel.create_thread(
                name=title,
                view=buttons
            )
        await interaction.followup.send(f"Post '{title}' created.", ephemeral=True)
        print(f"Post {title} created")
    except Exception as e:
        await interaction.followup.send(f"Exception: {e}", ephemeral=True)

class ThreadButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Change Message", custom_id=f"changebutton", style=discord.ButtonStyle.blurple)
    async def change_message(self, interaction:discord.interaction, Button:discord.ui.Button):
        user = interaction.user  
        if (any(role.id == MemberRoleId for role in user.roles)):
            target = interaction.message
            await interaction.response.send_message("Select what you want to modify in the post", ephemeral=True, view=ModifyMessageButtons(target_message=target))
        else:
            await interaction.response.send_message("You are not a Member, you can't modify this message", ephemeral=True)

class ModifyMessageButtons(discord.ui.View):
    def __init__(self, target_message: discord.Message):
        super().__init__(timeout=60)
        self.target_message = target_message
    
    async def role_check(self, interaction: discord.Interaction) -> bool:
        user = interaction.user
        has_role = any(role.id == MemberRoleId for role in user.roles)
        if has_role:
            return True
        else:
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return False
        
    # change title button 
    @discord.ui.button(label="Title", custom_id=f"changemtitle", style=discord.ButtonStyle.blurple)
    async def change_title(self, interaction:discord.interaction, Button:discord.ui.Button):
        title = self.target_message.channel
        user = interaction.user
        if not any(role.id == MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(
            ModifyTitleModal(current_title=title.name, target=title)
        )
    
    # change message button
    @discord.ui.button(label="Message", custom_id=f"changemessage", style=discord.ButtonStyle.blurple)
    async def change_content(self, interaction:discord.interaction, Button:discord.ui.Button):
        message = self.target_message
        user = interaction.user
        if not any(role.id == MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(
            ModifyTextModal(current_text=message.content, target=message)
        )
    
    # change Add Files button
    @discord.ui.button(label="Add Files", custom_id=f"addfiles", style=discord.ButtonStyle.green)
    async def change_schems(self, interaction:discord.interaction, Button:discord.ui.Button):
        user = interaction.user
        if not any(role.id == MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            "Send a single message containing all the new files you want to add, you have 180 seconds.",
            ephemeral=True
        )

        def UserCheck(message: discord.Message):
            return (
                message.author == interaction.user and message.channel == interaction.channel
            )
    
        try:
            user_message = await interaction.client.wait_for('message', timeout=180.0, check=UserCheck)
            if not user_message.attachments:
                await user_message.delete()
                await interaction.followup.send(
                    f"Error: You didn't send any file", 
                    ephemeral=True
                )
                return

            message = await interaction.channel.fetch_message(self.target_message.id)
            old_files = message.attachments
            new_files = user_message.attachments

            # Discord only allows 10 files per message
            if len(old_files) + len(new_files) > 10:
                await user_message.delete()
                await interaction.followup.send(
                    f"Discord message can only have 10 fies.", 
                    ephemeral=True
                )
                return 0
            files = []
            for file in new_files:
                files.append(await file.to_file())
            
            combined_files = old_files + files

            await self.target_message.edit(attachments=combined_files)

            await user_message.delete()

            await interaction.followup.send(
                    f"Files successfully added", 
                    ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                    f"Error {e}", 
                    ephemeral=True
            )

    # change Replace Files button
    @discord.ui.button(label="Replace All Files", custom_id=f"replacefiles", style=discord.ButtonStyle.danger)
    async def change_images(self, interaction:discord.interaction, Button:discord.ui.Button):
        user = interaction.user
        if not any(role.id == MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return        
        await interaction.response.send_message(
            "Send a single message containing all the new files you want to add, you have 180 seconds.",
            ephemeral=True
        )

        def UserCheck(message: discord.Message):
            return (
                message.author == interaction.user and message.channel == interaction.channel
            )
    
        try:
            user_message = await interaction.client.wait_for('message', timeout=180.0, check=UserCheck)
            new_files = user_message.attachments

            if not user_message.attachments:
                await user_message.delete()
                await interaction.followup.send(
                    f"Error: You didn't send any file.", 
                    ephemeral=True
                )
                return

            # Discord only allows 10 files per message
            if len(new_files) > 10:
                await user_message.delete()
                await interaction.followup.send(
                    f"Discord message can only have 10 fies.", 
                    ephemeral=True
                )
                return 0
            files = []
            for file in new_files:
                files.append(await file.to_file())

            await self.target_message.edit(attachments=files)

            await user_message.delete()

            await interaction.followup.send(
                    f"Files successfully replaced", 
                    ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                    f"Error {e}", 
                    ephemeral=True
            )

class ModifyTitleModal(discord.ui.Modal, title='Modify Title'):
    title_input = discord.ui.TextInput(
        label='Edit title of the post',
        style=discord.TextStyle.short,
        max_length=100,
        required=True
    )

    def __init__(self, current_title: str, target: discord.Thread):
        super().__init__()
        self.title_input.default = current_title
        self.target_thread = target 
    
    async def on_submit(self, interaction: discord.Integration):
        new_title = self.title_input.value 

        await self.target_thread.edit(name=new_title)

        await interaction.response.send_message(
            "Title updated successfully",
            ephemeral=True
        )

class ModifyTextModal(discord.ui.Modal, title='Modify Content'):
    text_input = discord.ui.TextInput(
        label='Edit content of the post',
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, current_text: str, target: discord.Message):
        super().__init__()
        self.text_input.default = current_text
        self.target = target 
    
    async def on_submit(self, interaction: discord.Integration):
        new_text = self.text_input.value 

        await self.target.edit(content=new_text)

        await interaction.response.send_message(
            "Text updated successfully",
            ephemeral=True
        )

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
    bot.add_view(ThreadButtons())
    print(f'{bot.user} Ready.')
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands ready: {len(synced)}")
    except Exception as e:
        print(f"Slash command error: {e}")

bot.run(TOKEN)

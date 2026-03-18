import discord
import bot
import buttons.ModifyMessageButtons as modMessage

class ThreadButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Change Message", custom_id=f"changebutton", style=discord.ButtonStyle.blurple)
    async def change_message(self, interaction:discord.interaction, Button:discord.ui.Button):
        user = interaction.user  
        if (any(role.id == bot.MemberRoleId for role in user.roles)):
            target = interaction.message
            await interaction.response.send_message("Select what you want to modify in the post", ephemeral=True, view=modMessage.ModifyMessageButtons(target_message=target))
        else:
            await interaction.response.send_message("You are not a Member, you can't modify this message", ephemeral=True)
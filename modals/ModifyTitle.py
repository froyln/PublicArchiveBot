import discord

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
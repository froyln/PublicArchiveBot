import discord

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
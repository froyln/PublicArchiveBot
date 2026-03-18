import discord
import bot
import modals.ModifyText as modText 
import modals.ModifyTitle as modTitle

class ModifyMessageButtons(discord.ui.View):
    def __init__(self, target_message: discord.Message):
        super().__init__(timeout=60)
        self.target_message = target_message
    
    async def role_check(self, interaction: discord.Interaction) -> bool:
        user = interaction.user
        has_role = any(role.id == bot.MemberRoleId for role in user.roles)
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
        if not any(role.id == bot.MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(
            modTitle.ModifyTitleModal(current_title=title.name, target=title)
        )
    
    # change message button
    @discord.ui.button(label="Message", custom_id=f"changemessage", style=discord.ButtonStyle.blurple)
    async def change_content(self, interaction:discord.interaction, Button:discord.ui.Button):
        message = self.target_message
        user = interaction.user
        if not any(role.id == bot.MemberRoleId for role in user.roles):
            await interaction.response.send_message(
                "You lost Member. You can no longer use this.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(
            modText.ModifyTextModal(current_text=message.content, target=message)
        )
    
    # change Add Files button
    @discord.ui.button(label="Add Files", custom_id=f"addfiles", style=discord.ButtonStyle.green)
    async def change_schems(self, interaction:discord.interaction, Button:discord.ui.Button):
        user = interaction.user
        if not any(role.id == bot.MemberRoleId for role in user.roles):
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
        if not any(role.id == bot.MemberRoleId for role in user.roles):
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
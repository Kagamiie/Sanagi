import discord, re, datetime, asyncio, requests, json, os.path

class BanView(discord.ui.View):
    def __init__(self, user_id, messages_file):
        super().__init__(timeout=180.0)
        self.user_id = user_id
        self.messages_file = messages_file

    @discord.ui.button(label="🔓", style=discord.ButtonStyle.danger)
    async def on_unban_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.permissions.ban_members:
            await interaction.response.send_message("T'a pas les perm mon con", ephemeral=True)
            return
        await interaction.guild.unban(self.user_id)
        embed = discord.Embed(title="Unban",description=f"`{self.user_id}` has been unbanned.",color=discord.Color.green())
        embed.add_field(name="Ban author", value=f"{interaction.user.mention}", inline=True)
        embed.set_footer(text=f"Unbanned by: {interaction.user}")
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="📜", style=discord.ButtonStyle.primary)
    async def on_messages_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open(self.messages_file, "r", encoding="utf-8") as file:
            if not interaction.permissions.ban_members:
                await interaction.response.send_message("T'a pas les perm mon con", ephemeral=True)
                return
        
            file_contents = file.read()
            try:
                embed = discord.Embed(title="Message Log", description=f"Here the log of `{self.user_id}` :", color=discord.Color.blue())
                embed.set_footer(text=f"Ask by: {interaction.user}")
                await interaction.user.send(embed=embed)
                await interaction.user.send(file=discord.File(self.messages_file, filename="messages.txt"))
                await interaction.response.send_message(f"The log of `{self.user_id}` has been sent to your DM.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I cannot send you the file of the messages because you have disabled private messages.", ephemeral=True)

async def banz(ctx, user: discord.User, reason:str, duration:str):
    reason="".join(reason) 
    duration_timedelta = None
    
    if duration:
        duration_regex = r'(\d+)(d|h|m|s)'
        matches = re.findall(duration_regex, duration)
        if matches:
            duration_dict = {unit: int(time) for time, unit in matches}
            duration_dict = {'days': duration_dict.get('d', 0),'hours': duration_dict.get('h', 0),'minutes': duration_dict.get('m', 0),'seconds': duration_dict.get('s', 0)}
            duration_timedelta = datetime.timedelta(**duration_dict)
        else:
            duration_timedelta = None

    # Archives locally the message's user and ban him
    messages_file = f"archives/restriction/{user.id}_messages.txt"
    with open(f"archives/restriction/{user.id}_messages.txt", "a", encoding="utf-8") as file:
        file.write(f"\n{user} ({user.id}):\nBan Reason: {reason}\n\n")
        for channel in ctx.guild.text_channels:
            async for message in channel.history():
                if message.author.id == user.id:
                    file.write(f"{message.author} ({message.author.id}) | {message.created_at} | ({message.jump_url}) | in #{message.channel.name}: ")
                    if message.content:
                        file.write(f" {message.content}")
                    if message.attachments:
                        file.write("Attachments:")
                        for attachment in message.attachments:
                            file.write(f" {attachment.url}")
                    file.write("\n")


    await ctx.guild.ban(user, delete_message_days=7 if duration_timedelta else 0, reason=reason)
    
    if duration_timedelta:
        unban_time = datetime.datetime.utcnow() + duration_timedelta
        unban_time_str = unban_time.strftime("%d/%m/%Y %H:%M:%S")
        description = f"`{user}` has been banned for {duration}."
    else:
        unban_time_str = "Never"
        description = f"`{user}` has been permanently banned."
            
    embed = discord.Embed(title="Ban",description=description,color=discord.Color.red())
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Ban duration", value=f"{unban_time_str}", inline=True)
    embed.add_field(name="ID", value=f"{user.id}", inline=True)
    embed.set_footer(text=f"Banned by: {ctx.user}")
    await ctx.response.send_message(embed=embed, view=BanView(user, messages_file))
    

    # Archives locally the messages from the banned user in every channel
    for channel in ctx.guild.text_channels:
        messages = []
        async for message in channel.history():
            if message.author.id == user.id:
                messages.append(message)
        if messages:
            await channel.delete_messages(messages)

    if duration_timedelta:
        await asyncio.sleep(duration_timedelta.total_seconds())
        await ctx.guild.unban(user, reason="Ban duration has expired.")

async def kickz(ctx,Interaction, user: discord.Member, *, reason: str = "Nada"):
    await Interaction.response.defer()
    try:
        member = await ctx.guild.fetch_member(user.id)
    except discord.NotFound:
        await ctx.response.send_message("User not found.")
        return

    # Save messages from the user in all channels to a text file
    with open(f"archives/restriction/{user.id}_messages.txt", "a", encoding="utf-8") as file:
        file.write(f"\n{user} ({user.id}):\nBan Reason: {reason}\n\n")
        for channel in ctx.guild.text_channels:
            async for message in channel.history():
                if message.author.id == user.id:
                    file.write(f"{message.author} ({message.author.id}) | {message.created_at} | ({message.jump_url}) | in #{message.channel.name}: ")
                    file.write(f"{message.content}" if message.content else "")
                    file.write(f"Attachments: {' '.join(attachment.url for attachment in message.attachments)}\n" if message.attachments else "\n")


    # Kick the user and send a confirmation message
    await ctx.guild.kick(user, reason=reason)
    embed = discord.Embed(title="Kick", description=f"{user} has been kicked.", color=discord.Color.orange())
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.set_footer(text=f"Kicked by: {ctx.user}")
    await ctx.response.send_message(embed=embed)

    # Delete all messages from the kicked user in every channel
    for channel in ctx.guild.text_channels:
        messages = []
        async for message in channel.history():
            if message.author.id == user.id:
                messages.append(message)
        if messages:
            await channel.delete_messages(messages)




gist_id = "gist_id.txt"
if os.path.isfile("archives/gist_id.txt"):
    with open("archives/gist_id.txt", "r") as f:
        gist_id = f.read().strip()
else:
    gist_id = None

async def clearz(Interaction, nombre: int):
    global gist_id
    await Interaction.response.defer()

    deleted_messages = await Interaction.channel.purge(limit=nombre + 1)
    with open("archives/restriction/deleted_messages.txt", "a", encoding='utf-8') as file:
        for message in deleted_messages:
            file.write(f"{message.author} ({message.author.id}) | {message.created_at} | ({message.jump_url}) | in #{message.channel.name}: ")
            if message.content:
                file.write(f" {message.content}")
            if message.attachments:
                file.write("Attachments:")
                for attachment in message.attachments:
                    file.write(f" {attachment.url}")
            file.write("\n")

    # set up the API endpoint URL and headers
    url = "https://api.github.com/gists"
    headers = {"Authorization": "Bearer YOUR_GITHUG_GIST_TOKEN"}

    if gist_id is None:
        # create a new Gist if no Gist has been created yet
        payload = {
            "description": "My code snippet",
            "public": False,
            "files": {"Deleted Message": {"content": "\n".join([f"{message.author} ({message.author.id}) | {message.created_at} | ({message.jump_url}) | in #{message.channel.name}: {message.content} {attachment.url}"for message in deleted_messages for attachment in message.attachments])}}}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    else:
        # update the existing Gist by adding the content of the deleted messages
        url += f"/{gist_id}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            gist_data = response.json()
            content = (gist_data["files"]["Deleted Message"]["content"]+ "\n" + "\n".join([f"{message.author} ({message.author.id}) | {message.created_at} | ({message.jump_url}) | in #{message.channel.name}: {message.content} {attachment.url}"for message in deleted_messages for attachment in message.attachments]))
            payload = {"files": {"Deleted Message": {"content": content}}}
            response = requests.patch(url, headers=headers, data=json.dumps(payload))

    # check the response status code
    if response.status_code == 201 or response.status_code == 200:
        # extract the gist URL and ID from the response JSON data
        gist_url = response.json()["html_url"]
        gist_id = response.json()["id"]
        print(f"Gist created/updated successfully: {gist_url}")
        try:
            await Interaction.user.send(f"Github Gist created/updated successfully: {gist_url}")
            await Interaction.channel.send("Github Gist created/updated successfully sent in dm.", delete_after=3)
        except discord.errors.NotFound:
            pass

    # update the Gist ID if a new Gist was created
    if response.status_code == 201:
        gist_id = response.json()["id"]
        with open("archives/gist_id.txt", "w") as f:
            f.write(gist_id)
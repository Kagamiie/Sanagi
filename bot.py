from archives.command.cmd import banz, kickz, clearz
from archives.command.serv import srvinf
from discord import app_commands
import discord


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        
    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync()
        print(f"\nUser: {self.user}\nBot ID: {self.user.id}\n")

bot = Bot()
tree = app_commands.CommandTree(bot)


@tree.command(name='send_dm', description="Just a command where you can send a message through me!")
async def send_dm(ctx,member:discord.Member,*,content:str):
    try:
        await member.send(content)
        await ctx.response.send_message('Message send.', delete_after=1)
    except:
        await ctx.response.send_message("User not found.", delete_after=1)

@tree.command(name='server', description="Did you need any information about the server ?")
async def serv(ctx):
    await srvinf(ctx)



@tree.command(name='clear', description="Only administrator can do this, It's the ultimate command to erase any trace")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(Interaction,nombre : int):
    await clearz(Interaction,nombre)

@tree.command(name='ban', description="Only administrator can do this, just a command bana user.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, reason:str, duration:str):
    await banz(ctx, user, duration, reason)

@tree.command(name="kick",  description="Only administrator can do this, just a command kick a user. (Doesn't work anymore, need to see why.)")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason: str = "Nada"):
    await kickz(ctx, user, *reason)

@tree.command(name='unban', description="Only administrator can do this, just a command unbana user.")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(ctx, user_id:str):

    if user_id.isdigit():
        user = await bot.fetch_user(int(user_id))
    else:
        try:
            user_id, user_id = user_id.split("#")
            user = discord.utils.get(await ctx.guild.bans(), name=user_id, discriminator=user_id).user
        except ValueError:
            await ctx.send(f"Invalid input: {user_id}")
            return
    
    await ctx.guild.unban(user)

    embed = discord.Embed(title="Unban",description=f"`{user}` has been unbanned.",color=discord.Color.green())
    embed.add_field(name="Ban author", value=f"> {ctx.user.mention}", inline=True)
    embed.set_footer(text=f"Unbanned by: {ctx.user}")
    await ctx.response.send_message(embed=embed)

@clear.error
async def on_kick_error(Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await Interaction.response.send_message("You don't have the necessary permission to clear messages from a channel, if you need help please contact an Administrator.", ephemeral=True)
@unban.error
async def on_unban_error(Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await Interaction.response.send_message("You don't have the necessary permission to unban a user, if you need help please contact an Administrator.", ephemeral=True)
@ban.error
async def on_ban_error(Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await Interaction.response.send_message("You don't have the necessary permission to ban a user, if you need help please contact an Administrator.", ephemeral=True)
@kick.error
async def on_kick_error(Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await Interaction.response.send_message("You don't have the necessary permission to kick a user, if you need help please contact an Administrator.", ephemeral=True)
    

bot.run('TOKEN')
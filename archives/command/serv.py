import discord

async def srvinf(ctx):
    embed=discord.Embed(title=f"Information about: {ctx.guild.name}", url="https://github.com/Kagamiie", description="Just a few information about the server, any information in dm : Kagami#4844 or on my twitter.", color=discord.Color.blue())
    embed.add_field(name="Owner", value=f"{ctx.guild.owner.mention}", inline=True)
    embed.add_field(name ='Server ID', value = f"{ctx.guild.id}", inline = True)
    embed.add_field(name ='Created On', value = ctx.guild.created_at.strftime("%b %d %Y"), inline = True)
    embed.add_field(name="Member Count", value=f'{ctx.guild.member_count} Members', inline=True)
    embed.add_field(name="Channel Count", value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice', inline=True)
    embed.set_footer(text=f"You got no bitches.")
    
    await ctx.response.send_message(embed=embed)
    

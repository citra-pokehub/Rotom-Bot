import discord
from discord.ext import commands
import asyncio
from replit import db
import json

file = ""


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.channel.DMChannel):

            raise commands.NoPrivateMessage("This command can't be used in DM.")

        else:
            return True

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):

        if ctx.author == member:
            await ctx.send("You cannot kick yourself.")
            return

        role = discord.utils.get(ctx.guild.roles, name="moderator")

        if role in member.roles:
            await ctx.send("You cannot kick a Moderator.")
            return

        if member == ctx.guild.owner:
            await ctx.send("You cannot kick the owner of the server.")
            return

        await member.kick(reason=reason)

        if reason is None:
            await ctx.send(f"{member.mention} has been kicked from the server.")
            try:
                await member.send(f"You have been kicked from {ctx.guild.name}")
            except discord.errors.HTTPException:
                pass

        else:
            await ctx.send(f"{member.mention} has been kicked from the server for {reason}")
            try:
                await member.send(f"You have been kicked from {ctx.guild.name} for {reason}")
            except discord.errors.HTTPException:
                pass

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):

        if ctx.author == member:
            await ctx.send("You cannot ban yourself.")
            return

        role = discord.utils.get(ctx.guild.roles, name="moderator")

        if role in member.roles:
            await ctx.send("You cannot ban a Moderator.")
            return

        if member == ctx.guild.owner:
            await ctx.send("You cannot kick the owner of the server.")
            return

        await member.ban(reason=reason)

        if reason is None:
            await ctx.send(f"{member.mention} has been banned from the server.")
            try:
                await member.send(f"You have been banned from {ctx.guild.name}")
            except discord.errors.HTTPException:
                pass

        else:
            await ctx.send(f"{member.mention} has been banned from the server for {reason}")
            try:
                await member.send(f"You have been banned from {ctx.guild.name} for {reason}")
            except discord.errors.HTTPException:
                pass

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"I have deleted {amount} messages.")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def emoji(self, ctx, ji: discord.Emoji = None):
        if ji is None:
            for emojis in ctx.guild.emojis:
                await ctx.send(f"ID: {emojis.id}, Emoji: `{emojis}`, {emojis}")
        else:
            await ctx.send(f"ID: {ji.id}, Emoji: `{ji}`")

    @commands.command()
    @commands.is_owner()
    async def history(self, ctx, member: discord.Member, limit=1):
        async for msg in member.history(limit=limit):
            await ctx.send(msg.content)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, member: discord.Member):

        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if role not in member.roles:
            await ctx.send(f"{member.mention} is not Muted!")
            return

        else:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} has been unmuted!")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, member: discord.Member, *, time=None):

        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not role:
            perms = discord.Permissions(send_messages=False, add_reactions=False)
            
            await ctx.guild.create_role(name="Muted", permissions=perms)

            role = discord.utils.get(ctx.guild.roles, name="Muted")

        for channels in ctx.guild.channels:
            await channels.set_permissions(role, send_messages=False, add_reactions=False)

        if role in member.roles:
            await ctx.send(f"{member.mention} is already Muted!")
            return

        if time is None:
            await member.add_roles(role)
            await ctx.send(f"{member.mention} has been muted!")
            return

        else:
            time = time.lower()
            if "s" in time or "sec" in time or "seconds" in time or "second" in time:
                int_time = ''.join(filter(lambda i: i.isdigit(), time))
                wait = int(int_time) * 1

                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been muted for {int_time} seconds!")

                await asyncio.sleep(wait)

            elif "m" in time or "min" in time or "minute" in time or "minutes" in time:
                int_time = ''.join(filter(lambda i: i.isdigit(), time))
                wait = int(int_time) * 60

                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been muted for {int_time} minutes!")

                await asyncio.sleep(wait)

            elif "h" in time or "hour" in time or "hours" in time or "hr" in time or "hrs" in time:
                int_time = ''.join(filter(lambda i: i.isdigit(), time))
                wait = int(int_time) * 60 * 60

                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been muted for {int_time} hours!")

                await asyncio.sleep(wait)

            elif "d" in time or "day" in time or "days" in time:
                int_time = ''.join(filter(lambda i: i.isdigit(), time))
                wait = int(int_time) * 60 * 60 * 24

                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been muted for {int_time} days!")

                await asyncio.sleep(wait)

            else:
                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been muted!")
                return

        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has been unmuted!")
        return

    # @commands.command()
    # @commands.has_permissions(manage_guild=True)
    # async def tour(self, ctx):

    #     gen6 = db["tour"]["gen6"]
    #     gen7 = db["tour"]["gen7"]

    #     await ctx.send(f"Gen VI: {gen6}\nGen VII: {gen7}")
    #     await ctx.send(f"Total Gen VI = {len(gen6)}, Gen VII = {len(gen7)}")

    @commands.command(aliases=["change-prefix", "prefix"])
    @commands.has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new_prefix):
        prefixes = db["prefixes"]
        prefixes[(str(ctx.guild.id))] = new_prefix
        db["preixes"] = prefixes
        await ctx.send(f"Server Prefix has been changed to `{new_prefix}`")


def setup(client):
    client.add_cog(Mod(client))

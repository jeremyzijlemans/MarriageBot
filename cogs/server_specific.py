from asyncpg import UniqueViolationError
from discord.ext.commands import command, Context, check, CheckFailure, MissingPermissions, MissingRequiredArgument, BadArgument

from cogs.utils.checks.is_bot_moderator import is_bot_moderator
from cogs.utils.custom_bot import CustomBot 
from cogs.utils.custom_cog import Cog 


class NotServerSpecific(CheckFailure):
    pass


def is_server_specific():
    def predicate(ctx):
        if ctx.bot.is_server_specific:
            return True
        raise NotServerSpecific()
    return check(predicate)


def ServerSpecific(Cog):

    def __init__(self, bot:CustomBot):
        super().__init__(self.__class__.__name__)
        self.bot = bot 


    async def cog_command_error(self, ctx:Context, error):
        '''
        Local error handler for the cog
        '''

        # Throw errors properly for me
        if ctx.original_author_id in self.bot.config['owners'] and not isinstance(error, (CommandOnCooldown, MissingPermissions)):
            text = f'```py\n{error}```'
            await ctx.send(text)
            raise error

        # Missing argument
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("You need to specify a person for this command to work properly.")
            return

    
        # Argument conversion error
        elif isinstance(error, BadArgument):
            try:
                argument_text = self.bot.bad_argument.search(str(error)).group(2)
                await ctx.send(f"User `{argument_text}` could not be found.")
            except Exception:
                await ctx.send(str(error))
            return

        # Missing permissions
        elif isinstance(error, MissingPermissions):
            if ctx.original_author_id in self.bot.config['owners']:
                await ctx.reinvoke()
                return
            if error.missing_perms[0] == 'SSF MarriageBot moderator' and [i.name for i in ctx.author.roles if i.name.lower() == 'marriagebot moderator']:
                await ctx.reinvoke()
                return
            await ctx.send(f"You need the `{error.missing_perms[0]}` permission to run this command.")
            return

    
    @command()
    @is_server_specific()
    @is_bot_moderator('SSF MarriageBot moderator')
    async def allowincest(self, ctx:Context):
        '''Toggles allowing incest on your guild'''

        # Database it
        async with self.bot.database() as db:
            try:
                await db(
                    'INSERT INTO guild_settings (guild_id, prefix, allow_incest) VALUES ($1, $2, $3)',
                    ctx.guild.id, self.bot.config['prefix']['default_prefix'], True,
                )
            except UniqueViolationError:
                await db(
                    'UDPATE guild_settings SET allow_incest=$2 WHERE guild_id=$1',
                    ctx.guild.id, True,
                )
        
        # Cache it 
        try:
            self.bot.guild_settings[ctx.guild.id]['allow_incest'] = True 
        except KeyError:
            self.bot.guild_settings[ctx.guild.id] = {
                'allow_incest': True,
                'prefix': self.bot.config['prefix']['default_prefix'],
            }

        # Boop the user
        await ctx.send("Incest is now **ALLOWED** on your guild.")

    
    @command()
    @is_server_specific()
    @is_bot_moderator('SSF MarriageBot moderator')
    async def disallowincest(self, ctx:Context):
        '''Toggles allowing incest on your guild'''

        # Database it
        async with self.bot.database() as db:
            try:
                await db(
                    'INSERT INTO guild_settings (guild_id, prefix, allow_incest) VALUES ($1, $2, $3)',
                    ctx.guild.id, self.bot.config['prefix']['default_prefix'], False,
                )
            except UniqueViolationError:
                await db(
                    'UDPATE guild_settings SET allow_incest=$2 WHERE guild_id=$1',
                    ctx.guild.id, False,
                )
        
        # Cache it 
        try:
            self.bot.guild_settings[ctx.guild.id]['allow_incest'] = False 
        except KeyError:
            self.bot.guild_settings[ctx.guild.id] = {
                'allow_incest': False,
                'prefix': self.bot.config['prefix']['default_prefix'],
            }

        # Boop the user
        await ctx.send("Incest is now **DISALLOWED** on your guild.")


def setup(bot:CustomBot):
    x = ServerSpecific(bot)
    bot.add_cog(x)
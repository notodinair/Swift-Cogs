from discord.ext.commands import check

from redbot.core import RedContext
from redbot.core.utils.chat_formatting import warning

from starboard import base
from starboard.i18n import _


def can_use_starboard():
    async def predicate(ctx):
        if not ctx.guild:
            return True
        _starboard = await base.get_starboard(ctx.guild)
        if _starboard.is_ignored(ctx.channel):
            return False
        if _starboard.is_ignored(ctx.author):
            if await _starboard.bot.is_owner(ctx.author):
                pass
            elif await _starboard.bot.is_mod(ctx.author):
                pass
            else:
                return False
        return True

    return check(predicate)


async def guild_has_starboard(ctx: RedContext):
    _starboard = await base.get_starboard(ctx.guild)
    if _starboard.channel is None:
        await ctx.send(warning(_("This server has no starboard channel setup")))
        return False
    return True

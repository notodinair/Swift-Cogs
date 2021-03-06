from typing import Type, Awaitable

import discord
from discord.ext import commands
from redbot.core.commands import Context
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import warning

from cog_shared.swift_libs import tick, prompt, confirm, Menu, PostAction
from quotes.quote import Quote, i18n


class StopLoop(Exception):
    pass


class ContinueLoop(Exception):
    pass


class QuoteEditor:

    def __init__(self, ctx: Context, quote: Quote):
        self.ctx = ctx
        self.quote = quote

    def __call__(self) -> Awaitable:
        return self.prompt()

    @property
    def bot(self) -> Red:
        return self.ctx.bot

    @property
    def send(self):
        return self.ctx.send

    def parse_embed(self, actions: dict):
        desc = "What action(s) would you like to take?\n\n{}".format(
            "\n".join(
                [
                    "{} \N{EM DASH} {}".format(y["emoji"], y["description"])
                    for x, y in actions.items()
                ]
            )
        )

        return discord.Embed(description=desc, colour=self.quote.embed_colour).set_author(
            name=i18n("Editing Quote #{}").format(self.quote.id), icon_url=self.quote.icon_uri
        )

    @property
    def actions(self):

        async def _creator_check(editor: "QuoteEditor"):
            return any(
                [
                    editor.ctx.author == editor.quote.creator,
                    await editor.bot.is_admin(editor.ctx.author),
                    await editor.bot.is_owner(editor.ctx.author),
                ]
            )

        return {
            "change_attributed": {
                "emoji": "\N{BUST IN SILHOUETTE}",
                "description": i18n("Change attributed author"),
            },
            "change_creator": {
                "emoji": "\N{PERSON WITH BALL}",
                "description": i18n("Change quote creator"),
                "only_if": _creator_check,
            },
            "change_content": {"emoji": "\N{MEMO}", "description": i18n("Change quote contents")},
            "delete_quote": {"emoji": "\N{WASTEBASKET}", "description": i18n("Delete quote")},
            "save": {"emoji": "\N{WHITE HEAVY CHECK MARK}", "description": i18n("Save changes")},
            "exit": {"emoji": "\N{CROSS MARK}", "description": i18n("Exit without saving")},
        }

    async def _prompt_user_input(
        self, content: str, *, converter: Type[commands.Converter] = None, **kwargs
    ):
        response = await prompt(self.ctx, content=content, delete_messages=True, **kwargs)
        if response is None:
            raise ContinueLoop

        if converter is None:
            return response.content

        try:
            return await converter().convert(self.ctx, response.content)
        except commands.BadArgument:
            await self.send(
                "I failed to properly parse your response; please try again.", delete_after=15.0
            )
            return await self._prompt_user_input(content, converter=converter, **kwargs)

    async def exit(self, save: bool = False):
        if save is True:
            await self.quote.save()
            await self.send(tick(i18n("Your changes have been carefully recorded and saved.")))
        raise StopLoop

    async def save(self):
        await self.exit(True)

    async def change_content(self):
        content = await self._prompt_user_input(i18n("Please respond with the new quote content"))
        self.quote.text = content
        await self.send(tick(i18n("Changed quote content successfully.")))

    async def change_attributed(self):
        attribute_to = await self._prompt_user_input(
            i18n("Which user would you like to attribute this quote to?"),
            converter=commands.MemberConverter,
        )
        self.quote.message_author = attribute_to
        await self.send(tick(i18n("Attributed quote to **{}**.").format(str(attribute_to))))

    async def change_creator(self):
        attribute_to = await self._prompt_user_input(
            i18n("Which user would you like to make the new quote creator?"),
            converter=commands.MemberConverter,
        )
        self.quote.message_author = attribute_to
        await self.send(tick(i18n("Attributed quote to **{}**.").format(str(attribute_to))))

    async def delete_quote(self):
        if await confirm(
            self.ctx,
            content=warning(
                i18n(
                    "Are you sure you want to delete this quote?\n\n"
                    "Unless you have a time machine, **this action is irreversible!**"
                )
            ),
        ):
            await self.quote.delete()
            await self.send(tick(i18n("Quote deleted.")))
            raise StopLoop

    async def prompt(self):
        actions = {}
        for action, data in self.actions.items():
            if "only_if" in data:
                if not await discord.utils.maybe_coroutine(data.get("only_if"), self):
                    continue
            actions[action] = data

        menu = Menu(
            ctx=self.ctx,
            actions={x: y["emoji"] for x, y in actions.items()},
            embed=self.parse_embed(actions),
        )

        while True:
            result = await menu.prompt(post_action=PostAction.DELETE_MESSAGE)
            if result.timed_out:
                await self.send(i18n("Menu timed out, any changes not saved have been discarded."))
                try:
                    await self.exit()
                except StopLoop:
                    pass
                break

            try:
                await getattr(self, result.item)()
            except StopLoop:
                break
            except ContinueLoop:
                continue

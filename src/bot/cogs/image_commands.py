import discord
from discord import app_commands
from discord.ext import commands

from asyncpg import Pool

from main import NimbleNeutrinos
import config
import models


class Image:
    id: str
    user: discord.User
    tags: list[str]
    src: str

    def __init__(self, id: str, user: discord.User, tags: list[str], src: str) -> None:
        self.id = id
        self.user = user
        self.tags = tags
        self.src = src

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed()

        embed.set_author(name=self.user.name)
        embed.add_field(name="Tags", value=f"*{", ".join(self.tags)}*")
        embed.set_image(url=self.src)

        return embed


class ImageSwitcher(discord.ui.View):
    cur_image: int = 0
    image_count: int
    interaction: discord.Interaction
    images: list[Image]

    def __init__(self, images: list[Image], ctx: commands.Context, timeout: float = 300.0):
        self.images = images
        self.image_count = len(images)
        self.interaction = ctx.interaction
        super().__init__(timeout=timeout)

    async def send_message(self):
        await self.interaction.response.send_message(
            embed=self.images[self.cur_image].get_embed(),
            view=self,
        )

    async def _edit_message(self):
        await self.interaction.edit_original_response(
            embed=self.images[self.cur_image].get_embed(),
            view=self,
        )

    @discord.ui.button(label="View on Web", style=discord.ButtonStyle.green)
    async def web_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass  # This function should redirect the user to the web page of the image

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cur_image = (self.cur_image - 1) % self.image_count
        await self._edit_message()
        await interaction.response.defer()

    @discord.ui.button(label="Forward", style=discord.ButtonStyle.blurple)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cur_image = (self.cur_image + 1) % self.image_count
        await self._edit_message()
        await interaction.response.defer()


class ImageCommands(commands.Cog):
    model: models.Model = models.Model()
    bot: NimbleNeutrinos
    db_pool: Pool

    def __init__(self, bot: NimbleNeutrinos):
        self.bot = bot
        self.db_pool = bot.pool

    async def _get_last_image(self, ctx: commands.Context) -> discord.Message:
        messages = ctx.channel.history(limit=50)
        message: discord.Message | None = None
        attachments: list[discord.Attachment] = []
        image_attachments: list[discord.Attachment] = []

        while not (attachments and len(image_attachments) == 1 and message.author.id == ctx.author.id):
            message = await messages.__anext__()
            attachments = message.attachments

            image_attachments = [
                attachment for attachment in attachments if attachment.content_type.startswith("image")
            ]

        return message

    def _post_data(self, ctx: commands.Context, message_id: int, tags: list[str]):
        all_tags: list[models.Tag] = self.model.get_tags
        tag_objects: list[models.Tag] = []

        for tag in tags:
            tag_index = -1
            for i in range(len(all_tags)):
                if tag == all_tags[i].name:
                    tag_index = i
                    break

            new_tag: models.Tag
            if tag_index == -1:
                tag_id = self.model.create_tag(tag)
                new_tag = self.model.get_tag_by_id(tag_id)
            else:
                new_tag = all_tags[i]

            tag_objects.append(new_tag)

        return self.model.create_message(
            discord_id=message_id,
            channel_id=ctx.channel.id,
            user_id=ctx.author.id,
            tags=tag_objects,
        )

    @app_commands.command(
        name="addtags",
        description="Add tags to the last image sent by you in this channel. (Max. 50 messages ago)",
    )
    @app_commands.describe(tags="Space separated list of tags")
    async def add_tags(self, ctx: commands.Context, tags: str):
        image_message: discord.Message = await self._get_last_image(ctx)
        tag_list = [tag.lower() for tag in tags.split()]

        embed: discord.Embed

        try:
            self._post_data(ctx, image_message, tag_list)

            embed = discord.Embed(
                title="Image Added!",
                description=f"Tags: *{", ".join(tag_list)}*",
                color=discord.Color.blurple(),
            )
            image_url = image_message.attachments[0].url
            embed.set_image(url=image_url)

        except Exception:
            embed = discord.Embed(
                title="Error",
                description="Request failed, please try again later",
                color=discord.Color.red(),
            )

        await ctx.reply(embed=embed)

    # TODO: Make this SQL request work too (get all images in the channel with the given tags and/or from given user)
    # and return a list of Image objects
    async def _query_images(self, user: str | None, tags: str | None) -> list[Image]:
        db_response = self.db_pool.fetch(f"""
        SELECT * FROM {config.DB().DATABASE}
        """)

        return []

    @app_commands.command(
        name="search",
        description="Search for image using tags (searches through current channel).",
    )
    @app_commands.describe(
        tags="Space separated list of tags to search for (optional)",
        user="Username of the poster of the image (optional)",
    )
    async def search(self, ctx: commands.Context, tags: str | None, user: str | None = None):
        tag_list = (tags if tags else "").split()
        images: list[Image] = await self._query_images(user, tags)

        view = ImageSwitcher(images, ctx)
        await view.send_message()


async def setup(bot: NimbleNeutrinos):
    await bot.add_cog(ImageCommands(bot))
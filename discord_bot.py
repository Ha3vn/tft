import discord

TOKEN = "OTg5OTM4NjA3ODMxNzg1NTA0.GA0a3v.PEqu7AICesspEA7wsCpM6Wg0lwHLr1AKKTzcpI"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!\n")

    print("Currently present in: ")
    for guild in client.guilds:
        print(f"{guild.name}(id: {guild.id})")
        print()
        members = '\n - '.join([member.name for member in guild.members])
        print(f"Guild Members:\n - {members}")

        for member in guild.members:
            if member.name == "S.":
                await member.create_dm()
                for _ in range(1):
                    await member.dm_channel.send(
                        f"Hello Toilet Warrior, looks like you just went 1st. Player diff"
                    )


# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(
#         f'Hi {member.name}, welcome to my Discord server!'
#     )


client.run(TOKEN)

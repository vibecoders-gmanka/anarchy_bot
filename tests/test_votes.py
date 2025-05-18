import asyncio
import pytest

@pytest.mark.asyncio
async def test_votes_concurrent():
    from anarchy_bot.bot import Votes
    from pyrogram.types import User, Message
    from pyrogram.client import Client

    target = User(id=1, first_name="target")
    initiator = User(id=2, first_name="init")
    client = Client()

    votes = Votes(user_to_mute=target, initiator=initiator, client=client)
    msg = Message()
    await votes.reply(msg)

    async def worker(i: int):
        voter = User(id=10 + i, first_name=f"u{i}")
        if i % 2:
            await votes.vote_plus(voter, None)
        else:
            await votes.vote_minus(voter, None)
        await votes.update()

    tasks = [asyncio.create_task(worker(i)) for i in range(50)]
    await asyncio.gather(*tasks)

    assert len(votes.plus_dict) + len(votes.minus_dict) == 50

    await votes.done()
    assert votes.msg_to_edit.edits


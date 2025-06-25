import pytest
from datetime import datetime
from aiogram.types import CallbackQuery, Message, Chat, User
from services.models import TrackCallback
from tests.conftest import MockBot
from services.utils import (add_message_to_track, _get_msg_stack, erase_last_messages,
                            set_track_callback, get_track_callback, update_track_callback,
                            _erase_track_messages, terminate_state_branch,
                            save_variable_in_state, get_variable_from_state, get_variables_from_state)

@pytest.fixture()
async def context_filled(context):
    await context.set_data({'track_messages':[1, 2, 8], 'misc':"data"})
    return context

messages=[
    (Message(message_id=1, date=datetime(2025, 6, 6, 10, 0, 0), chat=Chat(id=1,type="private"))),
    (Message(message_id=2, date=datetime(2025, 6, 6, 10, 0, 0), chat=Chat(id=1,type="private"))),
    (Message(message_id=8, date=datetime(2025, 6, 6, 10, 0, 0), chat=Chat(id=1,type="private"))),
]

callbacks=[
    (CallbackQuery(id="id1", from_user=User(id=1, is_bot=False, first_name="name1"),chat_instance="instance1",data="data1")),
    (CallbackQuery(id="id2", from_user=User(id=2, is_bot=False, first_name="name2"),chat_instance="instance2",data="data2")),
    (CallbackQuery(id="id8", from_user=User(id=8, is_bot=False, first_name="name8"),chat_instance="instance8",data="data8")),
]

@pytest.mark.parametrize(
    "message",
    messages
)
@pytest.mark.asyncio
async def test_add_message_to_track(context, message):
    await add_message_to_track(message, context)
    await add_message_to_track(message, context)
    res = await context.get_data()
    assert res['track_messages'] == [message.message_id, message.message_id]

@pytest.mark.asyncio
async def test_get_msg_stack(context_filled):
    res = await _get_msg_stack(await context_filled)
    assert res == [1, 2, 8]

@pytest.mark.asyncio
async def test_get_msg_stack_none(context):
    res = await _get_msg_stack(context)
    assert res == None

@pytest.mark.parametrize(
    "count,expected",
    [
        (0, [1, 2, 8]),
        (1, [8]),
        (2, [2, 8]),
        (3, [1, 2, 8])
    ]
)
@pytest.mark.asyncio
async def test_erase_last_messages(context_filled, count, expected):
    context = await context_filled
    bot = MockBot()
    await erase_last_messages(context, count, bot, 1)
    assert bot.deleted_messages == expected

@pytest.mark.parametrize(
    "message,callback",
    [(i, j) for i, j in zip(messages, callbacks)]
)
@pytest.mark.asyncio
async def test_set_track_callback(context, message, callback):
    await set_track_callback(callback, message, context)
    res = await context.get_data()
    assert res["cb"] == TrackCallback(message=message,callback_data=callback.data)

@pytest.mark.parametrize(
    "message,callback",
    [(i, j) for i, j in zip(messages, callbacks)]
)
@pytest.mark.asyncio
async def test_get_track_callback(context, message, callback):
    await context.update_data(
        cb=TrackCallback(
            message=message,
            callback_data=callback.data
        )
    )
    res = await get_track_callback(context)
    assert res == TrackCallback(
        message=message,
        callback_data=callback.data
    )

@pytest.mark.asyncio
async def test_get_track_callback_none(context):
    res = await get_track_callback(context)
    assert res == None

@pytest.mark.parametrize(
    "message,callback,track",
    [(i, j, TrackCallback(
        message=i,
        callback_data=k.data
    )) for i, j, k in zip(messages, callbacks, callbacks[::-1])]
)
@pytest.mark.asyncio
async def test_update_track_callback(context, message, callback, track):
    await update_track_callback(track, callback, context)
    res = await context.get_data()
    assert res["cb"] == TrackCallback(message=message,callback_data=callback.data)

@pytest.mark.asyncio
async def test_erase_track_messages(context_filled):
    context = await context_filled
    bot = MockBot()
    await _erase_track_messages(context, bot, 1)
    assert bot.deleted_messages == [1, 2, 8]

@pytest.mark.asyncio
async def test_erase_track_messages_none(context):
    bot = MockBot()
    await _erase_track_messages(context, bot, 1)
    assert bot.deleted_messages == []

@pytest.mark.parametrize(
    "message",
    messages
)
@pytest.mark.asyncio
async def test_terminate_state_branch(context, message):
    bot = MockBot()
    message._bot = bot
    await terminate_state_branch(message, context)
    res = await context.get_data()
    assert res == {}
    assert bot.deleted_messages == [message.message_id]

@pytest.mark.parametrize(
    "message",
    messages
)
@pytest.mark.asyncio
async def test_terminate_state_branch_no_add_last(context, message):
    bot = MockBot()
    message._bot = bot
    await terminate_state_branch(message, context, False)
    res = await context.get_data()
    assert res == {}
    assert bot.deleted_messages == []

@pytest.mark.parametrize(
    "variable,convert_func,expected",
    [
        (-123, abs, 123),
        ("variable", None, "variable"),
        ([4, 5, 6], max, 6),
    ]
)
@pytest.mark.asyncio
async def test_save_variable_in_state(context_filled, variable, convert_func, expected):
    context = await context_filled
    await save_variable_in_state(context, variable, "track_messages", convert_func)
    res = await context.get_data()
    assert res['track_messages'] == expected

@pytest.mark.parametrize(
    "var_name,expected",
    [
        ("track_messages", [1, 2, 8]),
        ("BAD", None),
        (None, None)
    ]
)
@pytest.mark.asyncio
async def test_get_variable_from_state(context_filled, var_name, expected):
    context = await context_filled
    res = await get_variable_from_state(context, var_name)
    assert res == expected

@pytest.mark.parametrize(
    "var_name,expected",
    [
        (["track_messages", "misc"], [[1, 2, 8], "data"]),
        (["BAD"], [None]),
        ([], [])
    ]
)
@pytest.mark.asyncio
async def test_get_variables_from_state(context_filled, var_name, expected):
    context = await context_filled
    res = await get_variables_from_state(context, var_name)
    assert res == expected

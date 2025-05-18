import sys
import types
import pytest

@pytest.fixture(scope="session", autouse=True)
def stub_pyrogram():
    pyrogram = types.ModuleType("pyrogram")

    # errors
    errors = types.ModuleType("pyrogram.errors")
    class FloodWait(Exception):
        def __init__(self, value):
            self.value = value
    class MessageNotModified(Exception):
        pass
    errors.FloodWait = FloodWait
    errors.MessageNotModified = MessageNotModified
    pyrogram.errors = errors

    # enums
    enums = types.ModuleType("pyrogram.enums")
    class ChatType:
        SUPERGROUP = "supergroup"
    enums.ChatType = ChatType
    pyrogram.enums = enums

    # client
    client_mod = types.ModuleType("pyrogram.client")
    class Client:
        async def restrict_chat_member(self, *args, **kwargs):
            pass
    client_mod.Client = Client
    pyrogram.client = client_mod

    # types
    types_mod = types.ModuleType("pyrogram.types")
    class InlineKeyboardButton:
        def __init__(self, text, callback_data):
            self.text = text
            self.callback_data = callback_data
    class InlineKeyboardMarkup:
        def __init__(self, buttons):
            self.inline_keyboard = buttons
    class ChatPermissions:
        def __init__(self, **kwargs):
            pass
    class ChatPrivileges:
        def __init__(self, **kwargs):
            pass
    class Chat:
        def __init__(self, id=1):
            self.id = id
    class Message:
        def __init__(self):
            self.chat = Chat()
            self.edits = []
            self.from_user = None
            self._edit_calls = 0
        async def reply(self, **kwargs):
            return Message()
        async def edit(self, **kwargs):
            self._edit_calls += 1
            if self._edit_calls % 7 == 0:
                raise errors.FloodWait(0)
            self.edits.append(kwargs)
        async def delete(self):
            pass
    class User:
        def __init__(self, id, first_name='user', username=None, language_code='en'):
            self.id = id
            self.first_name = first_name
            self.username = username
            self.language_code = language_code
        def mention(self):
            return f"[{self.first_name}](tg://user?id={self.id})"
    class CallbackQuery:
        def __init__(self, from_user, message=None, data=''):
            self.from_user = from_user
            self.message = message
            self.data = data
        async def answer(self, _=None):
            pass
    class ChatMember:
        pass
    types_mod.InlineKeyboardButton = InlineKeyboardButton
    types_mod.InlineKeyboardMarkup = InlineKeyboardMarkup
    types_mod.ChatPermissions = ChatPermissions
    types_mod.ChatPrivileges = ChatPrivileges
    types_mod.CallbackQuery = CallbackQuery
    types_mod.ChatMember = ChatMember
    types_mod.Message = Message
    types_mod.User = User
    pyrogram.types = types_mod

    sys.modules['pyrogram'] = pyrogram
    sys.modules['pyrogram.errors'] = errors
    sys.modules['pyrogram.enums'] = enums
    sys.modules['pyrogram.client'] = client_mod
    sys.modules['pyrogram.types'] = types_mod
    yield

@pytest.fixture(autouse=True)
def patch_translation(monkeypatch):
    import anarchy_bot.lang as lang
    monkeypatch.setattr(lang, 't', lambda item, _: item)
    yield

@pytest.fixture(autouse=True)
def patch_chats(monkeypatch):
    import types as _types
    import anarchy_bot.common as common
    monkeypatch.setattr(common, 'chats', _types.SimpleNamespace(mute_votes={}))
    yield

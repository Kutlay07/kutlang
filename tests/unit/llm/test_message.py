from harness.llm.message import Message


def test_message_stores_role_and_content():
    message = Message(
        role="user",
        content="Hello",
    )

    assert message.role == "user"
    assert message.content == "Hello"


def test_message_is_immutable():
    message = Message(
        role="user",
        content="Hello",
    )

    try:
        message.content = "Changed"
        assert False
    except AttributeError:
        pass
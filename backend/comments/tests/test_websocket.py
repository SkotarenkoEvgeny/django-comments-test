import json

import pytest

from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer

from config.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connect():
    communicator = WebsocketCommunicator(
        application,
        "/ws/comments/",
    )

    connected, _ = await communicator.connect()

    assert connected is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_comment_created_event():
    communicator = WebsocketCommunicator(
        application,
        "/ws/comments/",
    )

    connected, _ = await communicator.connect()

    assert connected

    channel_layer = get_channel_layer()

    comment = {
        "id": 1,
        "user_name": "Ivan",
        "text": "Hello",
    }

    await channel_layer.group_send(
        "comments",
        {
            "type": "comment_created",
            "comment": comment,
        },
    )

    response = await communicator.receive_json_from()

    assert response["type"] == "comment_created"
    assert response["comment"] == comment

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_multiple_clients_receive_event():
    client1 = WebsocketCommunicator(
        application,
        "/ws/comments/",
    )

    client2 = WebsocketCommunicator(
        application,
        "/ws/comments/",
    )

    await client1.connect()
    await client2.connect()

    layer = get_channel_layer()

    payload = {
        "id": 5,
        "text": "Test",
    }

    await layer.group_send(
        "comments",
        {
            "type": "comment_created",
            "comment": payload,
        },
    )

    msg1 = await client1.receive_json_from()
    msg2 = await client2.receive_json_from()

    assert msg1 == msg2

    await client1.disconnect()
    await client2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_can_send_message_without_crash():
    communicator = WebsocketCommunicator(
        application,
        "/ws/comments/",
    )

    connected, _ = await communicator.connect()

    assert connected

    await communicator.send_json_to({
        "message": "hello",
    })

    await communicator.disconnect()



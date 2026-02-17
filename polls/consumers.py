import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"poll_{self.slug}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_vote_update(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

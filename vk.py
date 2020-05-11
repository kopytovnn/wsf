import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random


def postVK(text, photo):
    vk_session = vk_api.VkApi(
        token='19028f9161522857fe5784c36ea96b3e4a54df58a03634d565cb2182b4be8a13e1580c153d0a669548c0f')

    longpoll = VkBotLongPoll(vk_session, "194406021")
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo_wall([photo]
                              )

    vk_photo_id = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"

    vk.wall.post(message=text, attachments=[vk_photo_id], owner_id="-194406021")
class Client:
    #TODO улучшить наследование
    def __init__(self, proxy: str | None = None):
        from zafiaonline.api_client.player_methods import Players
        from zafiaonline.api_client.global_chat_methods import GlobalChat
        from zafiaonline.api_client.user_methods import Auth, User
        from zafiaonline.api_client.room_methods import Room, MatchMaking
        from zafiaonline.api_client.https_api import HttpsApi
        from zafiaonline.api_client.zafia_api import ZafiaApi

        self.auth = Auth(client = self, proxy = proxy)

        self.sub_modules: dict[str, Auth | Players | GlobalChat | User | Room | MatchMaking | HttpsApi | ZafiaApi] = {
            "auth": self.auth,
            "user": User(client = self.auth),
            "players": Players(client = self.auth),
            "global_chat": GlobalChat(client = self.auth),
            "room": Room(client = self.auth),
            "matchmaking": MatchMaking(client = self.auth),
            "https": HttpsApi(proxy = proxy),
            "zafia": ZafiaApi(proxy = proxy),
        }

    def __getattr__(self, name: str):
        for sub_name, sub in self.sub_modules.items():
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"'{self.__class__.__name__}' "
                             f"object has no attribute '{name}'")

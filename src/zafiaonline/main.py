class Client:
    #TODO улучшить наследование
    def __init__(self, proxy: str | None = None):
        from zafiaonline.api_client.player_methods import Players
        from zafiaonline.api_client.global_chat_methods import GlobalChat
        from zafiaonline.api_client.user_methods import Auth, User
        from zafiaonline.api_client.room_methods import Room, MatchMaking

        self.auth = Auth(client = self, proxy = proxy)

        self.sub_modules: dict[str, Auth | Players | GlobalChat | User | Room | MatchMaking] = {
            "auth": self.auth,
            "user": User(client=self.auth),
            "players": Players(client = self.auth),
            "global_chat": GlobalChat(client = self.auth),
            "room": Room(client = self.auth),
            "matchmaking": MatchMaking(client = self.auth),
        }

    def __getattr__(self, name: str):
        for sub_name, sub in self.sub_modules.items():
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"'{self.__class__.__name__}' "
                             f"object has no attribute '{name}'")

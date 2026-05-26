from datetime import datetime


class AgentConversationLogger:

    conversations = []

    @classmethod
    def log(
        cls,
        agent_name,
        message
    ):

        entry = {

            "timestamp":
                datetime.now().isoformat(),

            "agent":
                agent_name,

            "message":
                message
        }

        cls.conversations.append(entry)

    @classmethod
    def get_logs(cls):

        return cls.conversations[-100:]
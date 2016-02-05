
class Relay:

    def get_state(self):
        raise Exception("Not implemented")

    def set_state(self, state):
        raise Exception("Not implemented")

    def to_hash(self):
        return {
            "id": self.id,
            "state": self.get_state()
        }

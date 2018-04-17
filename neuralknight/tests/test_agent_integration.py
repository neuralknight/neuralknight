from ..models import UserAgent

class MockAgent(UserAgent):
    def make_move(self, *args=None):
        if args is not None:
            assert args

        proposal = self.state                                                   
        proposal[5][4] = 9
        proposal[7][4] = 0
        put_board(proposal) 


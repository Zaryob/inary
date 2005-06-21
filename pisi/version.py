# version structure

class Version:
    def __init__(self, verstring):
        self.comps = verstring.split('.-')

    def pred(self,rhs,pred):
        for i in range(0, len(comps)-1):
            if pred(self.comps[i],rhs.comps[i]):
                return True
        else:
            return False

    def lt(self,rhs):
        return self.pred(rhs, lambda x,y: x<y)

    def le(self,rhs):
        return self.pred(rhs, lambda x,y: x<=y)

    def gt(self,rhs):
        return self.pred(rhs, lambda x,y: x>y)

    def ge(self,rhs):
        return self.pred(rhs, lambda x,y: x>=y)

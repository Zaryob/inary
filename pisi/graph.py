# the most simple minded digraph class ever

class digraph(object):

    def __init__(self):
        self.__v = set()
        self.__adj = {}
        self.__vdata = {}
        #self.__edata = {}

    def add_vertex(u, data = None):
        #assert not u in self.__v
        self.__v.add(u)
        if data!=None:
            self.__vdata[u] = data

    def add_edge(u, v, edata = None):
        self.__adj[u].add(u)
        #if edata != None:

    def set_vertex_data(u, data):
        self.__vdata[u] = data

    def vertex_data(u):
        self.__vdata[u]

    def has_vertex(u):
        return u in self.__v

    def has_edge(u,v):
        if u in self.__v:
            return v in self.__adj[u]
        else:
            return False

    def adj(u):
        return self.__adj[u]

    def dfs(finish_hook = None):
        self.color = {}
        self.p = {}
        self.d = {}
        self.f = {}
        for u in self.__v:
            self.color[u] = 'w'
            self.p[u] = None
        self.time = 0
        for u in self.__v:
            if color[u] = 'w':
                dfs_visit(u)

    def dfs_visit(u, finish_hook):
        self.color[u] = 'g'
        self.d[u] = self.time = self.time + 1
        for v in self.adj(u):
            if self.color[v] = 'w':
                self.p[v] = u
                dfs_visit(v)
        self.color[u] = black
        if finish_hook != None:
            finish_hook(u)
        self.f[u] = self.time = self.time + 1

    def topological_sort():
        l = []
        dfs(lambda u: l.append(u))
        return l


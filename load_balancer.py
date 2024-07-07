import Pyro4

@Pyro4.expose
class LoadBalancer(object):
    def __init__(self):
        self.servers = []
        self.current_server = 0

    def add_server(self, uri):
        self.servers.append(uri)

    def get_server(self):
        if not self.servers:
            raise Exception("No servers available")
        uri = self.servers[self.current_server]
        self.current_server = (self.current_server + 1) % len(self.servers)
        return uri

def main():
    load_balancer = LoadBalancer()
    ns = Pyro4.locateNS()
    
    # Adiciona os servidores ao balanceador de carga
    server1_uri = ns.lookup("example.todolist1")
    server2_uri = ns.lookup("example.todolist2")
    
    load_balancer.add_server(server1_uri)
    load_balancer.add_server(server2_uri)
    
    daemon = Pyro4.Daemon()
    uri = daemon.register(load_balancer)
    ns.register("example.loadbalancer", uri)
    print("Load Balancer is ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
    
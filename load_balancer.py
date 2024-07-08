import Pyro4
import time
import threading

@Pyro4.expose
class LoadBalancer(object):
    def __init__(self):
        self.servers = []
        self.current_server = 0
        self.ns = Pyro4.locateNS()
        self.check_interval = 10  # Check for new servers every 10 seconds
        self.running = True
        
        # Start a thread to periodically check for new servers
        threading.Thread(target=self.check_for_new_servers, daemon=True).start()

    def add_server(self, uri):
        if uri not in self.servers:
            self.servers.append(uri)
            print(f"Added server: {uri}")
        else:
            print(f"Server {uri} already exists, not adding again.")

    def get_server(self):
        if not self.servers:
            raise Exception("No servers available")
        uri = self.servers[self.current_server]
        self.current_server = (self.current_server + 1) % len(self.servers)
        return uri

    def check_for_new_servers(self):
        while self.running:
            try:
                # List all servers currently registered in the nameserver
                all_servers = self.ns.list().keys()
                
                for server_name in all_servers:
                    server_uri = self.ns.lookup(server_name)
                    if server_uri not in self.servers:
                        self.add_server(server_uri)
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                print(f"Error while checking for new servers: {e}")
                time.sleep(self.check_interval)

def main():
    load_balancer = LoadBalancer()
    
    daemon = Pyro4.Daemon()
    uri = daemon.register(load_balancer)
    ns = Pyro4.locateNS()
    ns.register("example.loadbalancer", uri)
    print("Load Balancer is ready.")
    
    daemon.requestLoop()

if __name__ == "__main__":
    main()

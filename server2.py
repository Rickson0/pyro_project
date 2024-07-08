import Pyro4
import utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

@Pyro4.expose
class SecureTodoList(object):
    def __init__(self):
        self.tasks = []
        self.server_name = "example.todolist2"  # Change this to the appropriate name of your server

    def add_task(self, encoded_task, client_public_key_pem):
        private_key, _ = utils.load_keys()
        encrypted_task = base64.b64decode(encoded_task)
        decrypted_task = utils.decrypt_message(private_key, encrypted_task)
        self.tasks.append(decrypted_task.decode())
        self.notify_servers("add", decrypted_task.decode())
        return f'Task "{decrypted_task.decode()}" added.'

    def remove_task(self, encoded_task, client_public_key_pem):
        private_key, _ = utils.load_keys()
        encrypted_task = base64.b64decode(encoded_task)
        decrypted_task = utils.decrypt_message(private_key, encrypted_task)
        if decrypted_task.decode() in self.tasks:
            self.tasks.remove(decrypted_task.decode())
            self.notify_servers("remove", decrypted_task.decode())
            return f'Task "{decrypted_task.decode()}" removed.'
        else:
            return f'Task "{decrypted_task.decode()}" not found.'

    def list_tasks(self, client_public_key_pem):
        client_public_key = serialization.load_pem_public_key(
            client_public_key_pem.encode(),
            backend=default_backend()
        )
        encrypted_tasks = []
        for task in self.tasks:
            encrypted_task = utils.encrypt_message(client_public_key, task.encode())
            encoded_task = base64.b64encode(encrypted_task).decode()
            encrypted_tasks.append(encoded_task)
        return encrypted_tasks

    def get_public_key(self):
        _, public_key = utils.load_keys()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_public.decode()

    def notify_servers(self, action, task):
        ns = Pyro4.locateNS()
        servers = ns.list()
        for name, uri in servers.items():
            if name.startswith("example.todolist") and name != self.server_name:
                try:
                    remote_server = Pyro4.Proxy(uri)
                    if action == "add":
                        remote_server.notify_new_task(task)
                    elif action == "remove":
                        remote_server.notify_remove_task(task)
                except Pyro4.errors.PyroError as e:
                    pass

    def notify_new_task(self, task):
        self.tasks.append(task)

    def notify_remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

def main():
    todo_list = SecureTodoList()
    daemon = Pyro4.Daemon()
    uri = daemon.register(todo_list)
    ns = Pyro4.locateNS()
    ns.register(todo_list.server_name, uri)
    print(f"Server {todo_list.server_name} is ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()

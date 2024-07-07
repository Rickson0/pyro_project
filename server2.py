import Pyro4
import utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

@Pyro4.expose
class SecureTodoList(object):
    def __init__(self):
        self.tasks = []

    def add_task(self, encoded_task, client_public_key_pem):
        private_key, _ = utils.load_keys()
        encrypted_task = base64.b64decode(encoded_task)
        decrypted_task = utils.decrypt_message(private_key, encrypted_task)
        self.tasks.append(decrypted_task.decode())
        return f'Task "{decrypted_task.decode()}" added.'

    def remove_task(self, encoded_task, client_public_key_pem):
        private_key, _ = utils.load_keys()
        encrypted_task = base64.b64decode(encoded_task)
        decrypted_task = utils.decrypt_message(private_key, encrypted_task)
        if decrypted_task.decode() in self.tasks:
            self.tasks.remove(decrypted_task.decode())
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

def main():
    todo_list = SecureTodoList()
    daemon = Pyro4.Daemon()
    uri = daemon.register(todo_list)
    ns = Pyro4.locateNS()
    ns.register("example.todolist2", uri)
    print("Server2 is ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()

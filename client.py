import Pyro4
import utils
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

def main():
    ns = Pyro4.locateNS()
    lb_uri = ns.lookup("example.loadbalancer")
    load_balancer = Pyro4.Proxy(lb_uri)

    # Carregar chave privada do cliente
    private_key, public_key = utils.load_keys()

    while True:
        try:
            server_uri = load_balancer.get_server()
            server = Pyro4.Proxy(server_uri)

            # Carregar chave pública do servidor
            server_public_key_pem = server.get_public_key()
            server_public_key = serialization.load_pem_public_key(
                server_public_key_pem.encode(),
                backend=default_backend()
            )

            print("\n1. Add Task\n2. Remove Task\n3. List Tasks\n4. Exit")
            choice = input("Enter choice: ")

            if choice == '1':
                task = input("Enter task to add: ")
                encrypted_task = utils.encrypt_message(server_public_key, task.encode())
                encoded_task = base64.b64encode(encrypted_task).decode()
                print(server.add_task(encoded_task, public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()))
            elif choice == '2':
                task = input("Enter task to remove: ")
                encrypted_task = utils.encrypt_message(server_public_key, task.encode())
                encoded_task = base64.b64encode(encrypted_task).decode()
                print(server.remove_task(encoded_task, public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()))
            elif choice == '3':
                encrypted_tasks = server.list_tasks(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo).decode())
                decrypted_tasks = []
                for encrypted_task in encrypted_tasks:
                    decoded_task = base64.b64decode(encrypted_task)
                    decrypted_task = utils.decrypt_message(private_key, decoded_task)
                    decrypted_tasks.append(decrypted_task.decode())
                print("Tasks:")
                for task in decrypted_tasks:
                    print(task)
            elif choice == '4':
                break
            else:
                print("Invalid choice. Try again.")
        except Exception as e:
            print(f"Server error: {e}. Trying next server...")

if __name__ == "__main__":
    main()

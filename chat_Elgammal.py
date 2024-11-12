
import random
import customtkinter
from PIL import Image
import sympy

# Paramètres ElGamal partagés entre le client et le serveur
q = sympy.randprime(pow(10, 20), pow(10, 50))
g = sympy.randprime(2, q)
server_public_key = None

def gen_key(q):
    key = random.randint(2, q-1)
    while sympy.gcd(q, key) != 1:
        key = random.randint(2, q-1)
    return key

def power(a, b, c):
    x = 1
    y = a
    while b > 0:
        if b % 2 != 0:
            x = (x * y) % c
        y = (y * y) % c
        b = int(b / 2)
    return x % c

def encrypt(msg, q, h, g):
    k = gen_key(q)
    p = power(g, k, q)
    s = power(h, k, q)
    
    encrypted_msg = []
    for char in msg:
        m = ord(char)
        c = (s * m) % q
        encrypted_msg.append(c)
    
    return encrypted_msg, p

def decrypt(encrypted_msg, p, key, q):
    h = power(p, key, q)
    decrypted_msg = []
    
    for c in encrypted_msg:
        m = (c * pow(h, q-2, q)) % q
        decrypted_msg.append(chr(m))
    
    print(decrypted_msg)
    return decrypted_msg

# Cadre pour l'envoi de messages
class SendFrame(customtkinter.CTkFrame):
    def __init__(self, master, chat_frame):
        super().__init__(master)
        self.chat_frame = chat_frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Label et champ de texte pour le message clair
        self.text_label = customtkinter.CTkLabel(self, text="Entrez le message à chiffrer :", justify="center")
        self.text_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.text_clair = customtkinter.CTkTextbox(self, height=100)
        self.text_clair.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)

        # Bouton pour chiffrer le message
        self.create_button('change_icon.png', "Chiffrer", self.update_output, "e", 2)

        # Label et champ pour afficher le message crypté
        self.crypt_text_label = customtkinter.CTkLabel(self, text="Message crypté :", justify="center")
        self.crypt_text_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.output = customtkinter.CTkLabel(self, text="", height=100, fg_color="white", text_color="black")
        self.output.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="ew", columnspan=2)

        # Bouton pour envoyer le message crypté dans la ChatFrame
        self.create_button('send_icon.png', "Envoyer", self.send_message, "e", 5)

    def retrieve_input(self):
        return self.text_clair.get("1.0", 'end-1c')

    def update_output(self):
        input_text = self.retrieve_input()
        encrypted_msg, p = encrypt(input_text, q, server_public_key, g)
        encrypted_msg_str = "".join(map(str, encrypted_msg))
        self.output.configure(text=str(encrypted_msg_str))

    def send_message(self):
        crypted_text = self.output.cget("text")
        self.chat_frame.add_message(crypted_text)

    def create_button(self, image_path, text, callback, stick, row):
        send_icon = customtkinter.CTkImage(light_image=Image.open(image_path), size=(20, 20))
        button = customtkinter.CTkButton(self, text=text, image=send_icon, command=callback)
        button.grid(row=row, column=1, padx=10, pady=10, sticky=stick)
        button.configure(font=("Poppins Sans MS", 15, "bold"))



class ChatFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, server_private_key):
        super().__init__(master)
        self.server_private_key = server_private_key
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.config(height=500)

    def add_message(self, message_text):
        msg_frame = customtkinter.CTkFrame(self, fg_color='white', corner_radius=10)
        msg_frame.grid(row=self.grid_size()[1], column=0, padx=10, pady=(10, 0), sticky="ew")
        crypted_msg_output = customtkinter.CTkLabel(
            msg_frame, wraplength=400, text=message_text, fg_color='white', text_color="black", justify="left"
        )
        crypted_msg_output.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="we", columnspan=2)

    def decriffre(self):
        encrypted_msg = self.output.cget("text")
        en_msg = [int(x) for x in encrypted_msg.strip('[]').split(', ')]
        decrypted_msg = decrypt(en_msg, server_public_key, self.server_private_key, q)
        decrypted_text = ''.join(decrypted_msg)

        print(decrypted_text)
        label = customtkinter.CTkLabel(
            self, wraplength=400, text=decrypted_text, fg_color='#9fbee6', font=("Poppins Sans MS", 10, "bold"),
            text_color="black"
        )
        label.grid(row=self.grid_size()[1], column=0, padx=10, pady=(10, 0), sticky="w", columnspan=2)

class ChatWindows(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cryptage-Decryptage ElGammal")
        self.geometry("900x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (900 // 2)
        y = (screen_height // 2) - (750 // 2)
        self.geometry(f"900x750+{x}+{y}")

        # Définition de la clé privée et publique du serveur
        self.key = gen_key(q)
        global server_public_key
        server_public_key = power(g, self.key, q)
        print(f"Clé publique du serveur: {server_public_key}")

        # Créer le cadre de chat avec la clé privée du serveur
        self.chat_frame = ChatFrame(self, server_private_key=self.key)
        self.chat_frame.grid(row=0, column=0, padx=30, pady=(10, 0), sticky="ew")

        # Créer le cadre d'envoi de message
        self.send_frame = SendFrame(self, self.chat_frame)
        self.send_frame.grid(row=1, column=0, padx=30, pady=(10, 0), sticky="ew")

app = ChatWindows()
app.mainloop()

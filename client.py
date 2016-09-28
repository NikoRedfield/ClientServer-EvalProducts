import socket

hote = "localhost"
port = 5005

token = None
req_cid = None

def encode_msg(msg):
    if(msg == "fin"):
        return msg
    global req_cid
    global token
    msg = msg.split()
    code = msg[0]
    if (code == "token_request"):
        if(len(msg)!=3):
            return "error"
        try :
            typecheck = int(msg[1])
            typecheck = int(msg[2])
            req_cid=msg[1]
            #print("req_cid="+str(req_cid)) #Debug
            return req_cid+" TR "+ str(msg[2])
        except ValueError :
            print("ERREUR : Veuillez entrer un numero de service et un login de type int.")
    if(code == "make_msg"):
        if(len(msg)!=2):
            return "error"
        try :
            typecheck = int(msg[1])
            if (int(msg[1]) <= 10 and int(msg[1]) >= 0) :
                return str(req_cid)+" MM "+str(token)+" "+str(msg[1])
            else :
                print("ERREUR : Veuillez entrer une note entre 0 et 10.")
        except ValueError :
            print("ERREUR : Veuillez entrer une note de type int.")
    if(code == "advice_req"):
        if(len(msg)!=2):
            return "error"
        try :
            typecheck = int(msg[1])
            return str(msg[1])+" AR"
        except ValueError :
            print("ERREUR : Veuillez entrer un numero de service de type int.")
            return "error"
    else:
        return "error"
		
def decode_msg(msg):
    if(msg == "fin"):
        return
    global token
    msg = msg.split()
    code = msg[0]
    if (code == "token_msg"):
        global token
        token=int(msg[2])
        print("Jeton bien reçu: "+str(token))
        return msg[1]
    if(code == "login_id_err"):
        print("ERREUR : ID deja enregistre !")
        return msg[1]
    if(code == "token_err"):
        print("ERREUR : Jeton deja utilise !")
        return msg[1]
    if(code == "not_enough_data_wrn"):
        token = None #token has been consumed
        print("Votre demande a bien ete pris en compte.\nPas assez de note sur la gamme pour faire la moyenne !")
        return msg[1]
    if(code == "make_ack"):
        token = None #token has been consumed
        print("Votre demande a bien ete pris en compte.\nMoyenne des avis du produit: "+str(msg[2]))
        return msg[1]
    if(code == "advice_ack"):
        print("La moyenne pour la gamme demandee est actuellement "+str(msg[2]))
        return msg[1]
    else:
        print("Unknown command")
        return None

#Protocole info service interface

def proto_interface():
    print("\t\tCOMMANDES:\n\t\t---------\n-->token_request CID LOGIN\n-->make_msg NOTE\n-->advice_req CID")

#Client
connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion etablie avec le serveur sur le port {}".format(port))
proto_interface()

msg_a_envoyer = b""
#Communication
while msg_a_envoyer != b"fin":
    msg_a_envoyer = input("> ")
    msg_a_envoyer = encode_msg(msg_a_envoyer)
    msg_a_envoyer = msg_a_envoyer.encode()
    #Send message
    connexion_avec_serveur.send(msg_a_envoyer)
    msg_recu = connexion_avec_serveur.recv(1024)
    msg_recu = msg_recu.decode()
    #print(msg_recu) #Debug 
    decode_msg(msg_recu)
print("Fermeture de la connexion")
connexion_avec_serveur.close()





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
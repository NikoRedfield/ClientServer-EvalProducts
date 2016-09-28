import socket
import select
import random

#Protocol codes
token_request = "TR"
make_msg = "MM"
advice_req = "AR"
ok_code="0 "
warning_code = "1 "
error_code = "2 "

#Dictionnary of CID
CID = dict()  #(notes, mean, token)

#List of login
LOGIN=dict()

#List of tokens (One for each CID)
TOKENS=[]

#Login used for the current session
current_login = None

def decode_query(query):
    if(query == "fin"):
        return query
    Lparam=[]
    Lquery=query.split()
    print(Lquery) #Debug
    if len(Lquery)<2:
        return "Unknown Command to server, please try again"
    code=Lquery[1]
    #Identification
    if (code == token_request):
        Lparam.append(Lquery[0]) #CID
        #print(Lparam[0])        #Debug
        Lparam.append(Lquery[2]) #Login_id
       # print(Lparam) #Debug
        return token_req(Lparam)
    #Marking
    if (code == make_msg):
        Lparam.append(Lquery[2]) #token
        Lparam.append(Lquery[3]) #mark
        Lparam.append(Lquery[0]) #CID
        return mark_campaign(Lparam)
    #Consultation
    if(code == advice_req):
        Lparam.append(Lquery[0])
        return consult_campaign(Lparam)
    else:
        return "UNKNOWN"

#IDENTIFICATION    

def token_req(Lparam):
    cid=int(Lparam[0])
    login=int(Lparam[1])
    #Checks if cid is already defined
    if not (cid in CID):
        CID[cid]=([],0,newtoken())
    #Checks if login is already defined
    if not (login in LOGIN):
        LOGIN[login]=[CID.get(cid)[2]]
        global current_login
        current_login = login
        return token_msg(LOGIN.get(login)[0])
    #Login is defined 
    else :
        #Login has already been used for the requested CID
        tokenCID=CID.get(cid)[2]
        if checktoken(LOGIN.get(login),tokenCID):
            return login_id_err()
        else:
            #Login hasn't been used for the requested CID yet 
            LOGIN[login].append(tokenCID)
            current_login = login
            return token_msg(tokenCID)

#Checks if the cid token has already been used by the login
def checktoken(login_tokens,token):
    for t in login_tokens:
        if t == token:
            return True
    return False

def token_msg(token):
    return "token_msg "+ok_code+str(token)

def login_id_err():
    return "login_id_err "+error_code

#Generate a new token
def newtoken():
    a = random.randint(1,9)
    b = random.randint(0,9)
    c = random.randint(0,9)
    d = random.randint(0,9)
    e = random.randint(0,9)
    f = random.randint(0,9)
    stoken=str(a)+str(b)+str(c)+str(d)+str(e)+str(f)
    token = int(stoken)
    if token in TOKENS:
        return newtoken()
    else:
        TOKENS.append(token)
        return token

#MARKING

def mark_campaign(Lparam):
    if(Lparam[0] == 'None'):
         return token_err()
    token = int(Lparam[0])
    mark = int(Lparam[1])
    cid = int(Lparam[2])
    #print(cid) #Debug
    current_values = CID.get(cid)
    marks=current_values[0]
    #print(marks) #Debug
    marks+=[mark]
    #print(marks) #Debug
    new_mean = compute_mean(marks)
    CID[cid]=(marks,new_mean,current_values[2])
    if(new_mean == 0 and len(marks) < 3):
        return data_warning()
    else:
        return make_ack(new_mean)

#Compute the mean
def compute_mean(marks):
    nb=len(marks)
    if(nb>=3):
        acc = 0
        for m in marks:
            acc+=m
        return round(acc/nb,2)
    else:
        return 0

def data_warning():
    return "not_enough_data_wrn "+ warning_code

def make_ack(mean):
    return "make_ack "+ ok_code + str(mean)
    
def token_err():
    return "token_err " + error_code

#CONSULTATION

def consult_campaign(Lparam):
    requested_cid = int(Lparam[0])
    cid = CID.get(requested_cid)
    if(cid == None):
        return data_warning()
    mean=float(cid[1])
    marks=cid[0]
    if(mean == 0 and len(marks) < 3):
        return data_warning()
    return advice_ack(mean)

def advice_ack(mean):
    return "advice_ack "+ ok_code +str(mean)

#Server    
    
hote = ''
port = 5005

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
print("Le serveur ecoute a present sur le port {}".format(port))

serveur_lance = True
clients_connectes = []
while serveur_lance:
    # Check for new clients with a max waiting time of 50ms
    connexions_demandees, wlist, xlist = select.select([connexion_principale],
        [], [], 0.05)
    
    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        # Add the connected client to the socket list
        clients_connectes.append(connexion_avec_client)
    
   #Listen to the clients' messages
    clients_a_lire = []
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes,
                [], [], 0.05)
    except select.error:
        pass
    else:
        for client in clients_a_lire:
            msg_recu = client.recv(1024)
            msg_recu = msg_recu.decode()
            msg_recu = decode_query(msg_recu)
            print(">Sent: {}".format(msg_recu))
            client.send(msg_recu.encode())
            if msg_recu == "fin":
                serveur_lance = False

print("Fermeture des connexions")
for client in clients_connectes:
    client.close()

connexion_principale.close()
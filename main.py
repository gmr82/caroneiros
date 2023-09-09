""" alguns testes """


import pickle # ¿alterar p/ salvar em json?

from os import path, makedirs
from getpass import getpass
from modules.menu import Menu, dye  # corrigir
from modules.users import User, Regular, Admin, users # corrigir
from modules.carpools import Carpool, carpools # corrigir

# ########################################################################### variáveis globais
...
    
def rate_profile():
    """10| Avaliar perfil"""

    driver_user = input("Qual o ID do usuário a ser avaliado?\n  ~> ")
    profile_rating_score = input("Qual sua nota, de 0 a 5, para o usuário <?>?\n  ~> ")

    print(dye("Perfil avaliado com sucesso!", "green"))

def contribute():
    """11| Valor extra"""

    driver_user = input("Qual o ID do destinatário da contribuição?\n  ~> ")
    profile_rating_score = input("Qual o valor da contribuição, em BRL?\n  ~> ")
    raise NotImplementedError
    print(dye("Contribuição destinada a <?> com sucesso!", "green"))


# ######################################################################### funcões: principais
def sign_up(*args) -> bool:
    # users: dict[str, Any] = args[0]
    admin = False
    username = Menu.get_input("Defina um nome de usuário.")

    if username[0] == '@':
        admin = True
        username = username[1:]
    
    if users.get(username, False):
        print(dye("Nome de usuário já cadastrado!", "red"))
    else:
        password = getpass("Defina uma senha de acesso.\n  ~> ")
        user = Admin(username, password) if admin else Regular(username, password)
        if Menu.confirm("Confirmar o cadastro deste usuário?"):
            users.update({user.username: user})
            print(dye("Usuário cadastrado com sucesso!", "green"))
            user.access_user_menu()
        else:
            print(dye("Cadastro cancelado!", "red"))
    
    return True

def sign_in(*args) -> bool:
    # users: dict[str, Any] = args[0]

    username: str = input("Nome de usuário.\n  ~> ")

    user: Regular | Admin = users.get(username, False) 
    if user:
        password = getpass("Senha de acesso.\n  ~> ")
        if user.password_is(password):
            print(dye(f"Olá, {username}!", "cyan"))
            user.access_user_menu() # ¿POLIMORFISMO?
        else:
            print(dye("Senha inválida!", "red"))
    else:
        print(dye("Usuário não cadastrado!", "red"))

    return True

def unsign(*args) -> bool:
    # users: dict[str, Any] = args[0]

    username: str = input("Nome de usuário.\n  ~> ")

    user = users.get(username, False) 
    
    if type(user) is Admin:
        print(dye(f'Administradores não podem ser removidos.', 'red'))
        return True
    
    if user:
        password = getpass("Senha de acesso.\n  ~> ")
        if user.password_is(password):
            if Menu.confirm("Confirmar o descadastro deste usuário?"):
                del users[user.username] # AQUI
                print(dye("Usuário descadastrado com sucesso!", "green"))
            else:
                print(dye("Descadastro cancelado!", "red"))
        else:
            print(dye("Senha inválida!", "red"))
    else:
        print(dye("Usuário não cadastrado!", "red"))

    return True

# ######################################################################## funcões: temporárias
def print_all_users(*args) -> bool:
    """¿?"""
    User.print_from(users)
    print(dye(f"{len(users)}", "red"))
    return True

def print_all_carpools(*args) -> bool:
    """¿?"""
    Carpool.print_from(carpools)
    print(dye(f"{len(carpools)}", "red"))
    return True



# ########################### funcões: p/ ler/serializar e desserializar/escrever de/em arquivo
def try_write_pkl_dict(dictionary: dict[str, User|Regular|Admin], path: str) -> None:
    """ Tentar serializar e escrever dicionário, em arquivo """
    exception_msg = None
    try:
        with open(path, "wb") as pickle_file:
            print(dye(f"Tentando serializar objeto ({type(dictionary).__name__})…", "yellow"))
            pickle.dump(dictionary, pickle_file)
        print(dye(f"Tentando escrever em {path}…", "yellow"))
    except FileNotFoundError:
        exception_msg = f"{path} não foi encontrado."
    except (IOError, OSError) as error:
        exception_msg = f"Erro de E/S ao escrever em {path}: {error}."
    except pickle.PicklingError as error:
        exception_msg = f"Erro ao serializar objeto ({type(dictionary).__name__}): {error}."
    except MemoryError:
        exception_msg = f"Erro de falta de memória ao escrever em {path}."
    except Exception as error:
        exception_msg = f"Erro desconhecido: {error}."
    else:
        print(dye(f"Objeto ({type(dictionary).__name__}) serializado e escrito com sucesso em {path}!", "green"))
    finally:
        if exception_msg is not None:
            print(dye(exception_msg, 'red'))

def try_read_pkl_dict(path: str) -> dict[str, User|Regular|Admin]:
    """ Tentar ler e desserializar dicionário, de arquivo """
    exception_msg = None
    dictionary: dict[str, User|Regular|Admin] = {}
    try:
        print(dye(f"Tentando ler de {path}…", "yellow"))
        with open(path, "rb") as pickle_file:
            print(dye(f"Tentando desserializar objeto ({type(dictionary).__name__})…", "yellow"))
            dictionary = pickle.load(pickle_file)
    except FileNotFoundError:
        exception_msg = f"{path} não foi encontrado."
    except EOFError:
        exception_msg = f"Erro de fim de arquivo ao ler de {path}."
    except pickle.UnpicklingError as error:
        exception_msg = f"Erro ao desserializar objeto ({type(dictionary).__name__}): {error}."
    except Exception as error:
        exception_msg = f"Erro desconhecido: {error}."
    else:
        print(dye(f"Objeto ({type(dictionary).__name__}) lido e desserializado com sucesso de {path}!", "green"))
    finally:
        if exception_msg is not None:
            print(dye(exception_msg, 'red'))
        return dictionary


# ########################################################################## instanciando menus
initial_menu = Menu(
    title="Menu: Início",
    options=[
        (dye("print all users (temp)", 'red'), print_all_users, None),
        (dye("print all carpools (temp)", 'red'), print_all_carpools, None),
        ("Entrar", sign_in, users),
        ("Inscrever-se", sign_up, users),
        ("Desinscrever-se", unsign, users),
        ("Encerrar", "Encerrando…", None)
    ], invalid_selection_text="Seleção inválida!")

# options=[
#     ("print all users", print_all_users, None),
#     #  ('write dict users', write_dict_users, None),
#     #  ('read dict users', read_dict_users, None),
#     ("print all carpools", print_all_carpools, None),
#     #  ('write dict carpools', write_dict_carpools, None),
#     #  ('read dict carpools', read_dict_carpools, None),
#     ("↩", "see you soon…")
# ]


# ##################################################################################### rodando

if __name__ == "__main__":
    
    rw = True
    if rw:
        users.update(try_read_pkl_dict('io/users.pkl'))
        carpools.update(try_read_pkl_dict('io/carpools.pkl'))

        # users.update({'admin': Admin('admin', 'admin')})
        
        if not len(carpools):
            # carpools.update()
            ...

    msg = None
    try:
        initial_menu.run_in_loop()
    except KeyboardInterrupt:
        msg = '\nInterrupção: Ctrl+C'
    else:
        if rw:
            if not path.exists("io"):
                makedirs("io")

            try_write_pkl_dict(users, 'io/users.pkl')
            try_write_pkl_dict(carpools, 'io/carpools.pkl')
    finally:
        if msg is None:
            msg = 'bye!'
        print(dye(msg, 'cyan'))
    
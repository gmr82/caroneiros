"""alguns testes"""

import os  # corrigir (mkdir)
import pickle
import re

from modules.menu import *  # corrigir
from modules.users import *  # corrigir
from modules.carpool import Carpool  # corrigir

from getpass import getpass

def change_username():
    """¿?"""
    new_username = input("Defina o novo nome de usuário*.\n  ~> ")

    if new_username == active_user.username:
        print(dye("Nome de usuário alterado!", "red"))
        return

    if users.get(new_username):
        print(dye("Nome já utilizado por outro usuário!"))
        return

    users.pop(active_user.username)
    active_user.change_username(new_username)
    users[active_user.username] = active_user
    print(dye("Nome de usuário alterado!"))


def change_password():
    """¿?"""
    new_password = input("Defina a nova senha.\n  ~> ")
    active_user.change_password(new_password)
    print(dye("Senha alterada!", "red"))


def edit_profile_attribute():
    """¿?"""
    key = input("Insira a chave do atributo.\n  ~> ")
    value = input(
        "Defina o valor do atributo. "
        + dye(" Obs.: '' para remover.", "red")
        + "\n  ~> "
    )

    if value == "":
        value = None

    msg = active_user.profile.update_attribute(key, value)
    print(dye("Atributo " + msg + "!"))


def clear_history():
    active_user.clear_rides_history()
    print(dye("Histórico de caronas removido!", "red"))


def show_profile() -> bool:
    """Mostrar perfil"""
    active_user.profile.view()
    return True


def show_carpools(keys: set) -> bool:
    """Mostrar caronas"""
    total = len(keys)

    for key in keys:
        carpools[key].show_me()

    if total == 0:
        print(dye("Não há caronas disponíveis!", "red"))
        return False

    if total == 1:
        print(dye(f"{total} carona disponível!", "red"))
    else:
        dye(f"{total} caronas disponíveis!", "red")

    return True


def create_carpool():
    """6| Oferecer carona"""
    # ride_date = input('Quando será a viagem?\n  ~> ') # corrigir
    origin = input("Qual o local de partida?\n  ~> ")
    destination = input("Qual o local de destino?\n  ~> ")

    match input(
        "Deseja ofertar ou demandar esta carona? " + dye("[o/d]", "red") + "\n  ~> "
    ).lower():
        case "o":
            driver_username = active_user.username
            seats_provided = int(input("Quantas vagas deseja disponibilizar?\n  ~> "))
            status = "offered"
            role = "driver"
            passenger_username = None
        case "d":
            driver_username = None
            seats_provided = None
            status = "demanded"
            role = "passenger"
            passenger_username = active_user.username
        case _:
            print(dye("Opção inválida!", "red"))
            return

    carpool = Carpool(destination, origin, driver_username, status)
    carpool.seats_provided = seats_provided  # tratar int
    carpool.add_passenger(passenger_username)

    carpool.show_me()
    if (
        input("Digite 'ok' para confirmar a carona " + status + "*.\n  ~> ").lower()
        == "ok"
    ):
        identifier = carpool.identifier
        carpools[identifier] = carpool
        active_user.rides_history.update({identifier: role})
        print(dye("Carona " + status + "* com sucesso!", "red"))
    else:
        print(dye("Carona não " + status + "*!", "red"))


def hitch_a_carpool(user, carpool_key: str):
    """¿?"""
    carpool: Carpool = carpools[carpool_key]
    if (
        not carpool.has_driver()
        and input(
            dye("Sapoha ainda não tem motorista!", "red")
            + "\n"
            + "Digite 'm' para se tornar o motorista.\n  ~> "
        ).lower()
        == "m"
    ):
        seats_provided = int(input("Quantas vagas deseja disponibilizar?\n  ~> "))
        if seats_provided < len(carpool.passengers_usernames):
            print(
                dye(
                    "Quantidade insuficiente para a demanda! (mín.: "
                    + str(len(carpool.passengers_usernames))
                    + " vagas)",
                    "red",
                )
            )
            return
        status = "offered"
        if (
            input("Digite 'ok' para confirmar a carona " + status + "*.\n  ~> ").lower()
            == "ok"
        ):
            carpool.driver_username = active_user.username
            carpool.status = status
            carpool.seats_provided = seats_provided
            active_user.rides_history.update({carpool_key: "driver"})
            carpool.show_me()
            print(dye("Carona " + status + "* com sucesso!", "red"))
            return

    if carpool.driver_is(active_user.username):
        print(dye("Você é o motorista da carona!", "red"))
        return

    if active_user.username in carpool.passengers_usernames:
        print(dye("Você já é passageiro da carona!", "red"))
        return

    if not carpool.has_vacancy():
        print(dye("Não há vagas!", "red"))
        return

    if input("Digite 'ok' para tomar a carona.\n  ~> ").lower() == "ok":
        carpool.passengers_usernames.append(user.username)
        role = "passenger"
        active_user.rides_history.update({carpool_key: role})
        print(dye("Carona tomada com sucesso!", "red"))
    else:
        print(dye("Carona não tomada!", "red"))


def find_ride() -> None:
    """7| Procurar carona"""
    match input(
        "Vizualizar caronas ofertadas ou demandadas? "
        + dye("[o/d]*", "red")
        + "\n  ~> "
    ).lower():
        case "o":
            status = "offered"
        case "d":
            status = "demanded"
        case "*":
            status = None
        case _:
            print(dye("Opção inválida!", "red"))
            return

    keys = carpools_by_status(status)

    if not show_carpools(keys):
        return

    key = input(
        "Digite o imenso identificador da carona para pegá-la."
        + dye(" Obs.: ≠ para retornar.", "red")
        + "\n  ~> "
    )

    key = re.sub(
        r"[\W]", "", key
    )  # tentativa de filtro para manter apenas letras e números

    if key in keys:
        hitch_a_carpool(active_user, key)


def account() -> None:
    return account_menu.run_in_loop()


def profile() -> None:
    return profile_menu.run_in_loop()


def rate_profile():
    """10| Avaliar perfil"""

    driver_user = input("Qual o ID do usuário a ser avaliado?\n  ~> ")
    profile_rating_score = input("Qual sua nota, de 0 a 5, para o usuário <?>?\n  ~> ")

    print(dye("Perfil avaliado com sucesso!", "red"))


def contribute():
    """11| Valor extra"""

    driver_user = input("Qual o ID do destinatário da contribuição?\n  ~> ")
    profile_rating_score = input("Qual o valor da contribuição, em BRL?\n  ~> ")
    raise NotImplementedError
    print(dye("Contribuição destinada a <?> com sucesso!", "red"))


def sign_up() -> None:
    """cadastrar"""
    username = input("Defina um nome de usuário.\n  ~> ")
    if users.get(username):
        print(dye("Nome de usuário já cadastrado!", "red"))
        return
    
    password = input("Defina uma senha de acesso.\n  ~> ")

    user = Regular(username, password)
    print(user)
        
    if confirm("Confirma a inscrição do usuário?"):
        users[user.username] = user
        print(dye("Usuário cadastrado com sucesso!", "red"))
        global active_user  # corrigir
        active_user = user
        access(active_user)
    else:
        print(dye("Cadastrado cancelado!", "red"))
    return


def unsign():
    """descadastrar"""
    response = input(
        "Confirma a desinscrição do usuário? " + dye("[s]", "red") + "\n  ~> "
    )
    if response[0].lower() == "s":
        # delete_user(active_user)
        del users[active_user.username]
        return False
    return True


def access(user: User) -> None:
    """acessar"""
    print(dye(f"Olá, {user.username}!", "red"))
    user_menu.run_in_loop()


def sign_in() -> None:
    """login"""
    username: str = input("Nome de usuário.\n  ~> ")
    if not username in users:
        print(dye("Usuário não cadastrado!", "red"))
        return

    password= getpass("Senha de acesso.\n  ~> ")


    if not users[username].password_is(password):
        print(dye("Senha inválida!", "red"))
        return

    global active_user  # corrigir

    active_user = users[username]
    access(active_user)


def debug() -> bool:
    """¿?"""
    debug_menu.run_in_loop()
    return True


def print_all_users() -> bool:
    """¿?"""
    User.print_from(users)
    print(dye(f"{len(users)}", "red"))
    return True


def print_all_carpools() -> bool:
    """¿?"""
    Carpool.print_from(carpools)
    print(dye(f"{len(carpools)}", "red"))
    return True


def carpools_by_status(status: str | None = None) -> set:
    """filtra burramente as caronas pelo status"""
    keys: set = set()
    if status is None:
        for key, carpool in carpools.items():
            keys.add(key)
    else:
        for key, carpool in carpools.items():
            if carpool.status == status:
                keys.add(key)
    return keys


# ############################################################### funcões p/ salvar em arquivo


def write_pkl_users():
    """¿?"""
    with open("io/users.pkl", "wb") as pickle_file:
        pickle.dump(users, pickle_file)


def read_pkl_users():
    """¿?"""
    global users  # corrigir
    with open("io/users.pkl", "rb") as pickle_file:
        users = pickle.load(pickle_file)


def write_pkl_carpools():
    """¿?"""
    with open("io/carpools.pkl", "wb") as pickle_file:
        pickle.dump(carpools, pickle_file)


def read_pkl_carpools():
    """¿?"""
    global carpools  # corrigir
    with open("io/carpools.pkl", "rb") as pickle_file:
        carpools = pickle.load(pickle_file)


# ############################################################### variáveis globais

active_user: Regular # | Admin
users: dict = {}
carpools: dict = {}

# ############################################################### instanciando os menus

sign_menu = Menu(
    title="Menu: Início",
    options=[
        ("Inscrever-se", sign_up, True),
        ("Entrar", sign_in, True),
        ("DEBUG", debug, True),
        ("Encerrar", "Encerrando…", None)
    ], invalid_selection_text="Seleção inválida!")

debug_menu = Menu(
    title="Menu: DEBUG",
    options=[
        ("print all users", print_all_users, True),
        #  ('write dict users', write_dict_users, None),
        #  ('read dict users', read_dict_users, None),
        ("print all carpools", print_all_carpools, True),
        #  ('write dict carpools', write_dict_carpools, None),
        #  ('read dict carpools', read_dict_carpools, None),
        ("↩", "see you soon…", None)
    ], invalid_selection_text="Seleção inválida!")

user_menu = Menu(
    title="Menu: Usuário",
    options=[
        ("Adicionar carona*", create_carpool, True),
        ("Procurar carona", find_ride, True),
        #  ('Sugerir carona', suggest_ride, None),
        #  ('Histórico de caronas', past_rides, None),
        #  ('Avaliar perfil', rate_profile, None),
        #  ('Valor extra', contribute, None),
        ("Perfil", profile, True),
        ("Conta", account, True),
        ("Sair", "Saindo…", None)
    ], invalid_selection_text="Seleção inválida!")

account_menu = Menu(
    title="Menu: Conta",
    options=[
        ("Alterar username", change_username, False),
        ("Alterar senha", change_password, False),
        # ("Limpar histórico", clear_history, False),
        ("Desinscrever-se*", unsign, False),
        ("Retornar", "Retornando…", None)
    ], invalid_selection_text="Seleção inválida!")

profile_menu = Menu(
    title="Menu: Perfil",
    options=[
        ("Mostrar", show_profile, True),
        ("Adicionar/Editar atributo", edit_profile_attribute, True),
        ("Retornar", "Retornando…", None)
    ], invalid_selection_text="Seleção inválida!")

# ############################################################### rodando

if __name__ == "__main__":
    BOOL = True

    if BOOL:
        try:
            print(dye("Tentando carregar usuários…", "yellow"))
            read_pkl_users()
            print(dye("Tentando carregar caronas…", "yellow"))
            read_pkl_carpools()
        except Exception as e:
            print(e)
        else:
            print(dye("Usuários e caronas carregados com sucesso!", "blue"))
        finally:
            pass

    sign_menu.run_in_loop()

    if BOOL:
        if not os.path.exists("io"):
            os.makedirs("io")
        write_pkl_users()
        print(dye("Salvando usuários…", "blue"))
        write_pkl_carpools()
        print(dye("Salvando caronas…", "blue"))
        # try:
        # except FileNotFoundError:
        # pass

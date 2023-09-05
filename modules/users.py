""" módulo de usuário """

import re # corrigir

from getpass import getpass
from modules.interfaces import DraftInterface, abstractmethod
from modules.carpools import Carpool, carpools
from typing import Any
from modules.profile import Profile
from modules.menu import Menu, dye

# ######################################WWWWWWWWWWWW######################### variáveis globais
users: dict[str, Any] = {} # | None = None # dict[str, User | Regular | Admin]

class User(DraftInterface):
    """ rascunho da classe usuário """
    # _users: dict[str, Any] = {}

    def __init__(self, username: str, password: str | None = None) -> None:
        self._username: str = username
        self._password: str | None  # criar classe p/ senha
        self.change_password(password)
    
    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str | None:
        return self._password

    def is_in(self, users: list | dict) -> bool:
        return self.username in users

    @staticmethod
    def print_from(users: list[Any] | dict[str, Any]) -> None:
        if type(users) is list:
            for user in users:
                print(user)
        elif type(users) is dict:
            for key, user in users.items():
                print(f'{key} | {user}')

    def change_username(self, username: str) -> None:
        self._username = username

    def change_password(self, password: str | None = None) -> None:
        password = None if password == "" else password
        self._password = password

    def password_is(self, input: str | None = None) -> bool:
        input = None if input == "" else input
        return input == self.password
    
    def set_user_menu(self) -> Menu:
        """ configurar menu de usuário """
        raise NotImplementedError
    
    @abstractmethod
    def access_user_menu(self, *args) -> bool | None:
        raise NotImplementedError
        
    @abstractmethod
    def set_account_menu(self) -> Menu:
        raise NotImplementedError
    
    @abstractmethod
    def access_account_menu(self, *args) -> bool | None:
        raise NotImplementedError
    
    def access_change_password(self, *args) -> bool | None:
        new_password: str = getpass("Defina a nova senha.\n  ~> ")

        if Menu.confirm("Tem certeza disso?"):
            self.change_password(new_password)
            print(dye("Senha alterada com sucesso!", "green"))
        else:
            print(dye("Senha não alterada!", "red"))
        return



class Regular(User):

    def __init__(self, username: str, password: str | None = None) -> None:
        super().__init__(username, password)
        self._profile: Profile = Profile(username)
        self.rides_history: dict = dict()
        
        self._user_menu: Menu = self.set_user_menu()
        self._account_menu: Menu = self.set_account_menu()

    def __repr__(self) -> str:
        """ retorna uma representação printável do objeto """
        string = str()
        string += f"Regular(username={self.username}, "
        string += f"password={self.password}, "
        string += f"profile={self._profile}, "
        string += f"rides_history={self.rides_history})"
        return string
    
    @property
    def profile(self) -> Profile:
        return self._profile
    
    @property
    def user_menu(self) -> Menu:
        return self._user_menu
    
    @property
    def account_menu(self) -> Menu:
        return self._account_menu

    def set_user_menu(self) -> Menu:
        title = "Menu: Usuário"
        invalid_selection_text = "Seleção inválida!"

        options = list()  # ¿mudar p/ tupla?
        options.append(("Perfil", self.profile.access_profile_menu, None))
        options.append(("Lançar carona", self.add_carpool, None))
        options.append(("Procurar carona", self.find_carpool, None))
        # options.append(('Sugerir carona', suggest_ride, None))
        # options.append(('Histórico de caronas', past_rides, None))
        # options.append(('Avaliar perfil', rate_profile, None))
        # options.append(('Valor extra', contribute, None))
        options.append(("Conta", self.access_account_menu, None))
        options.append(("Sair", "Saindo…"))
        return Menu(title=title, options=options, invalid_selection_text=invalid_selection_text)
    
    def access_user_menu(self) -> bool | None:
        return self.user_menu.run_in_loop()    

    def access_change_username(self, *args) -> bool | None:
        # users: dict[str, Any] = args[0]
        new_username: str = input("Defina o novo nome de usuário*.\n  ~> ")
        if new_username == self.username:
            print(dye("Nome de usuário mantido!", "yellow"))
            return

        if users.get(new_username):
            print(dye("Nome já utilizado por outro usuário!", "red"))
            return True

        if Menu.confirm("Tem certeza disso?"):
            users.pop(self.username)
            self.change_username(new_username)
            self.profile.update_attribute('username', new_username)
            users[self.username] = self
            print(dye("Nome de usuário alterado com sucesso!", "green"))
        else:
            print(dye("Nome de usuário não alterado!", "red"))

        return

    def set_account_menu(self) -> Menu:
        """
        configurar menu de conta
        """
        title = "Menu: Conta"
        invalid_selection_text = "Seleção inválida!"

        options = list()  # ¿mudar p/ tupla?
        options.append(("Alterar username", self.access_change_username, users))
        options.append(("Alterar senha", self.access_change_password, None))
        options.append(("?", print, self))
        options.append(("Sair", "Saindo…"))

        return Menu(title=title, options=options, invalid_selection_text=invalid_selection_text)

    def access_account_menu(self, *args) -> bool | None:
        return self.account_menu.run_in_loop()

    def add_carpool(self, *args) -> bool:
        """if not type(args[0]) is dict:
        raise NotImplementedError('coleção não passada')"""

        origin = input("Qual o local de partida?\n  ~> ")
        destination = input("Qual o local de destino?\n  ~> ")

        match input("Deseja ofertar ou demandar esta carona? "
                    + dye("[o/d]", "red") + "\n  ~> ").lower()[0]:
            case "o":
                driver_username = self.username
                seats_provided = Menu.get_input('Quantos assentos deseja disponibilizar?', int)
                status = "ofertada"
                role = "driver"
                passenger_username = None
            case "d":
                driver_username = None
                seats_provided = None
                status = "demandada"
                role = "passenger"
                passenger_username = self.username
            case _:
                print(dye("Opção inválida!", "red"))
                return True

        carpool = Carpool(destination, origin, driver_username, status)
        carpool.seats_provided = seats_provided  # tratar int
        carpool.add_passenger(passenger_username)

        carpool.view()
        if Menu.confirm("Confirmar o lançamento desta carona?"):
            identifier = carpool.identifier
            carpools.update({identifier: carpool})
            self.rides_history.update({identifier: role})
            print(dye("Carona " + status + " com sucesso!", "green"))
        else:
            print(dye("Carona não " + status + "!", "red"))

        return True

    def find_carpool(self, *args) -> bool:

        status: str | None

        match input("Vizualizar caronas ofertadas ou demandadas? "
            + dye("[o/d]*", "red") + "\n  ~> ").lower()[0]:
            case "o":
                status = "ofertada"
            case "d":
                status = "demandada"
            case "*":
                status = None
            case _:
                print(dye("Opção inválida!", "red"))
                return True

        keys = Carpool.carpools_keys_by_status(status)

        if not Carpool.show_carpools(keys):
            return True

        key = input("Digite o identificador da carona para mais opções."
                    + dye(" Obs.: ≠ para retornar.", "red") + "\n  ~> ")

        key = re.sub(r"[\W]", "", key)  # tentativa de filtro para manter apenas letras e números

        if key not in keys:
            print(dye("Identificador inválido!", "red"))
        else:
            self.hitch_a_carpool(key)
        return True
    
    def hitch_a_carpool(self, carpool_key: str) -> None:

        carpool = carpools.get(carpool_key)

        if carpool is None:
            return
        
        if carpool.driver_is(self.username):
            print(dye("Você já é o motorista da carona!", "red"))
            return

        if self.username in carpool.passengers_usernames:
            print(dye("Você já é passageiro da carona!", "red"))
            return

        if not carpool.has_seats_available():
            print(dye("Não há vagas!", "red"))
            return

        if carpool.status == 'demandada' and Menu.confirm("Deseja ofertá-la?"):
            
            while True:
                seats_provided = Menu.get_input('Quantos assentos deseja disponibilizar?', int)
                # seats_provided = int(seats_provided) if seats_provided.isdigit() else 0
                if seats_provided < carpool.get_passengers_quantity():
                    print(dye("Quantidade insuficiente para a demanda! (mín.: "
                              + str(len(carpool.passengers_usernames))
                              + " vagas)", "red",))
                    continue
                break
                
            status = "ofertada"
            carpool.driver_username = self.username
            carpool.update_status(status)
            carpool.seats_provided = seats_provided
            self.rides_history.update({carpool_key: "driver"})
            print(dye("Carona ofertada com sucesso!", "green"))
            return
        
        if Menu.confirm('Deseja tomar esta carona?'):
            carpool.passengers_usernames.append(self.username)
            self.rides_history.update({carpool_key: "passenger"})
            print(dye("Carona tomada com sucesso!", "green"))
        else:
            print(dye("Carona não tomada!", "red"))
        
        carpool.update_status()
    


class Admin(User):

    def __init__(self, username: str, password: str | None = None) -> None:
        super().__init__(username, password)
        self._user_menu: Menu = self.set_user_menu()
        self._account_menu: Menu = self.set_account_menu()
        self._debug_menu: Menu= self.set_debug_menu()

    def __repr__(self) -> str:
        """ retorna uma representação printável do objeto """
        string = str()
        string += f"Admin(username={self.username}, "
        string += f"password={self.password})"
        return string

    @property
    def user_menu(self) -> Menu:
        return self._user_menu

    @property
    def account_menu(self) -> Menu:
        return self._account_menu
    
    @property
    def debug_menu(self) -> Menu:
        return self._debug_menu

    def set_user_menu(self) -> Menu:
        title = "Menu: Usuário*"
        invalid_selection_text = "Seleção inválida!"

        options = list()  # ¿mudar p/ tupla?
        options.append(("DEBUG", self.access_debug_menu, None))
        options.append(("Conta", self.access_account_menu, None))
        options.append(("Sair", "Saindo…"))
        return Menu(title=title, options=options, invalid_selection_text=invalid_selection_text)

    def access_user_menu(self, *args) -> bool | None:
        return self.user_menu.run_in_loop()
    
    def set_debug_menu(self) -> Menu:
        title = "Menu: DEBUG"
        invalid_selection_text = "Seleção inválida!"

        options = list()  # ¿mudar p/ tupla?
        options.append(("Remover todas as caronas", print, None))
        options.append(("Remover todas os usuários", print, None))
        options.append(("Sair", "Saindo…"))
        return Menu(title=title, options=options, invalid_selection_text=invalid_selection_text)

    def access_debug_menu(self, *args) -> bool | None:
        return self.debug_menu.run_in_loop()
    
    def set_account_menu(self) -> Menu:
        title = "Menu: Conta"
        invalid_selection_text = "Seleção inválida!"

        options = list()  # ¿mudar p/ tupla?
        options.append(("Alterar senha", self.access_change_password, None))
        options.append(("Retornar", "Retornando…"))

        return Menu(title=title, options=options, invalid_selection_text=invalid_selection_text)

    def access_account_menu(self, *args) -> bool | None:
        return self.account_menu.run_in_loop()
    

    @staticmethod
    def clear_rides_history(user: Regular) -> None:
        """
        limpar histórico de corridas
        """
        user.rides_history.clear()
        print(dye(f"Histórico de caronas de {user.username} foi removido!", "red"))
        raise NotImplementedError
    
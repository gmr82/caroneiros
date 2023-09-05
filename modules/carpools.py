''' módulo de carona '''

from datetime import datetime
from uuid import uuid4
from typing import Literal, Any
from dataclasses import dataclass
from modules.interfaces import DraftInterface
from modules.menu import dye

# #############################WWWWWWWWWWWW################################## variáveis globais
carpools: dict[str, Any] = {} # | None = None # dict[str, Carpool]


@dataclass
class Ride:
    '''rascunho da classe corrida'''
    date: datetime|None  # ¿data? da corrida
    origin: str
    destination: str

    def __repr__(self) -> str:
        return f'{self.origin} → {self.destination} ({self.date})'


class Carpool(DraftInterface):
    ''' rascunho da classe carona '''

    def __init__(self, origin, destination, driver_username=None, status=None):
        self._identifier: str = str(uuid4())[0:3]  # ¿?
        self.ride = Ride(date=None, destination=destination, origin=origin)
        self._status: Literal['demandada', 'ofertada', 'cheia'] | None = status
        self.driver_username: str | None = driver_username
        self.seats_provided: int | None = None  # assentos disponibilizados
        self._passengers_usernames: list = []

    def __repr__(self) -> str:
        string = f'Carpool(identifier={self.identifier}, '
        string += f'ride={self.ride}, '
        string += f'status={self.status}, '
        string += f'driver_username={self.driver_username}, '
        string += f'seats_available={self.seats_provided}, '
        string += f'passengers_usernames={self.passengers_usernames})'
        return string

    @property
    def identifier(self) -> str:
        return self._identifier
    
    @property
    def status(self) -> str:
        return str(self._status)
    
    def is_in(self, carpools: list | dict) -> bool:
        return self.identifier in carpools

    @staticmethod
    def print_from(carpools: list | dict) -> None:
        if type(carpools) is list:
            for carpool in carpools:
                print(carpool)
        elif type(carpools) is dict:
            for key, carpool in carpools.items():
                print(f'{key} | {carpool}')
    
    def view(self) -> None:
        """ visualizar, porcamente, a carona """

        # attributes = dict(self.__dict__) # gambiarra p/ corrigir
        # for key, value in attributes.items():
        #     print(f'{key}: {value}')
        
        width = 52
        seats_provided = self.seats_provided
        seats_available = (0 if seats_provided is None else seats_provided) - self.get_passengers_quantity()

        print(f'╓{"":─^{width}}╖',
              f'║{"Carona #" + self.identifier:^{width}}║',
              f'╟{"":─^{width}}╢',
              f'║{f" trajeto: {self.ride}":<{width}}║',
              f'║{f" condição: {self.status}":<{width}}║',
              f'║{f" motorista: {self.driver_username}":<{width}}║',
              f'║{f" assentos livres/disponibilizados: {seats_available}/{seats_provided}":<{width}}║',
              f'║{f" passageiros: {self.passengers_usernames}":<{width}}║',
              f'╙{"":─^{width}}╜', sep='\n')

    def driver_is(self, driver_username: str) -> bool:
        return self.driver_username == driver_username
    
    def update_status(self, new_status: Literal['demandada', 'ofertada', 'cheia'] | None = None) -> None:
        if new_status is not None:
            self._status = new_status
        elif not self.has_seats_available():
            self._status = 'cheia'
            print(dye('Boa! Esta carona está completa!', 'yellow'))
        else:
            ...
        # print(dye('Atualizando status…', 'yellow'))
    
    def has_driver(self) -> bool:
        return bool(self.driver_username)
    
    def add_passenger(self, passenger_username: str|None) -> None:
        if self.has_seats_available() and passenger_username:
            self._passengers_usernames.append(passenger_username)

    def get_passengers_quantity(self) -> int:
        return len(self._passengers_usernames)

    @property
    def passengers_usernames(self) -> list:
        return self._passengers_usernames

    def has_seats_available(self) -> bool:
        return len(self.passengers_usernames) < self.seats_provided if self.seats_provided else True

    @staticmethod
    def carpools_keys_by_status(status: str | None) -> set[Any]:
        """ filtrar burramente as caronas pelo status """
        keys = set()
        if status is None:
            for key, carpool in carpools.items():
                keys.add(key)
        else:
            for key, carpool in carpools.items():
                if carpool.status == status:
                    keys.add(key)
        return keys
    
    @staticmethod
    def show_carpools(keys: set) -> bool:
        """ mostrar caronas do conjunto """
        total = len(keys)
        
        for key in keys:
            carpools[key].view()
        
        if total == 0:
            msg = "Não há caronas disponíveis!"
        else:
            msg = f"{total} {'carona disponível' if total ==1 else 'caronas disponíveis'}!"
        
        print(dye(msg, "red"))

        return bool(total)
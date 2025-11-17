from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        consumi_medi=[]

        if self._impianti is None:
            return []

        for impianto in self._impianti:
            consumi_impianto=impianto.get_consumi() # Il metodo definito nel DTO
            # Raccoglie i consumi di ogni impianto

            if consumi_impianto is None:
                continue

            consumi_mensili=[]
            for m in consumi_impianto:
                if m.data.month==mese:
                    consumi_mensili.append(m.kwh) # Aggiungo i kilowatt ora

            if len(consumi_mensili)>0:
                media=sum(consumi_mensili)/len(consumi_mensili)
                consumi_medi.append((impianto.nome, round(media,2)))
            else:
                consumi_medi.append((impianto.nome, 0))
        return consumi_medi
        # TODO

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """

        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return

        # Condizione finale
        if giorno==8:
            if self.__costo_ottimo==-1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima= list(sequenza_parziale)
            return
        # Ricorsione
        else:
            # Per ogni impianto
            for id_impianto in consumi_settimana.keys():
                # Costo fisso per lo spostamento
                costo_spostamento = 0
                # Se NON è il primo giorno E l'impianto scelto è diverso da quello precedente
                if ultimo_impianto is not None and id_impianto!=ultimo_impianto:
                    costo_spostamento=5

                costo_energetico=consumi_settimana[id_impianto][giorno-1]

                # Costo totale
                costo_nuovo=costo_corrente+costo_energetico+costo_spostamento
                sequenza_parziale.append(id_impianto)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_impianto, costo_nuovo, consumi_settimana)

                # Backtracking
                sequenza_parziale.pop()
        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_settimana = {}
        if self._impianti is None:
            return {}

        for impianto in self._impianti:
            consumi_impianto=impianto.get_consumi()

            if consumi_impianto is None:
                continue
            consumi_filtrati = [c for c in consumi_impianto
                                if c.data.month == mese and 1 <= c.data.day <= 7]
            consumi_ordinati = sorted(consumi_filtrati, key=lambda x: x.data.day)
            kwh_list = [c.kwh for c in consumi_ordinati]

            if len(kwh_list) == 7:
                consumi_settimana[impianto.id] = kwh_list
            else:
                # Log di sicurezza per il debug
                print(
                    f"Attenzione: Dati incompleti per impianto {impianto.id} nel mese {mese}. Trovati {len(kwh_list)}/7 giorni.")
        return consumi_settimana

        # TODO


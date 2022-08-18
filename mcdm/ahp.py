import pandas as pd  # manipular dados


# metodo estatico utilizado para retornar um dataframe com o resultado dos frameworks AHPSaaty e AHPGaussiano
def resultado(dados_agregados):
    df_resultado = dados_agregados.copy()
    df_resultado['Pontuacao'] = df_resultado.sum(axis=1)
    df_resultado = df_resultado.sort_values('Pontuacao', ascending=False)
    df_resultado['Ranking'] = list(range(1, len(df_resultado) + 1))
    return df_resultado[['Ranking', 'Pontuacao']]


class _AnalyticHierarchyProcess:
    def __init__(self, matriz_decisao, objetivo):

        # se objetivo nao for especificado todos os criterios da matriz decisao serao maximizados
        # maximizar criterios significa que 'quanto maior o seu valor melhor'
        # minimizar criterios significa que 'quanto menor o seu valor melhor'
        dicionario = dict((col, 'max') for col in matriz_decisao.columns)

        # verificar se objetivo especificado é valido
        # se sim, minimizar criterio da matriz de decisao
        if objetivo != 'max':
            if type(objetivo) != list:
                raise TypeError('objetivo deve ser uma lista')
            for item in objetivo:
                if item in dicionario:
                    dicionario[item] = 'min'
                else:
                    raise KeyError(f'{item} nao e um criterio da matriz de decisao')

        self._matriz_decisao = matriz_decisao
        self.objetivo = dicionario
        self.preferencia_local = self._normalizar_decisao()

    # tornar adimensional a matriz decisao
    def _normalizar_decisao(self):
        matriz_normalizada = self._matriz_decisao.copy()
        for item in self.objetivo:
            # criterio do tipo 'quanto maior melhor'
            if self.objetivo[item] == 'max':
                # normalizar
                soma = matriz_normalizada[item].sum()
                matriz_normalizada[item] = matriz_normalizada[item] / soma
            # crietrio do tipo 'quanto menor melhor'
            else:
                # manipulacao algebrica para trocar o numerador pelo denominador
                matriz_normalizada[item] = matriz_normalizada[item].apply(lambda x: 1 / x)
                # normalizar
                soma = matriz_normalizada[item].sum()
                matriz_normalizada[item] = matriz_normalizada[item] / soma
        return matriz_normalizada

    # criar indicador de comparacao entre as alternativas
    # multiplica a preferencia local pelo peso do criterio
    # a soma da matriz agregacao por alternativa gera a pontuacao do resultado
    def _agregacao(self, peso):
        matriz_agregacao = self.preferencia_local.copy()
        for indice, item in enumerate(matriz_agregacao.columns):
            matriz_agregacao[item] = matriz_agregacao[item] * peso[indice]
        return matriz_agregacao


class AHPSaaty(_AnalyticHierarchyProcess):

    """
    Analytic Hierarchy Process (AHP) e um metodo criado por Thomas Saaty para auxiliar nas tomadas de decisao multicriterio.
    Caracterizado por uma matriz de decisao composta por alternativas e criterios ponderados pelo tomador de decisao em questao.
    Baseado em matematica e psicologia, o AHP nao so determina a melhor decisao como tambem justifica a escolha.
    Restricao: auxilia a tomada de decisao para problemas com ate 15 criterios.
    Para problemas com mais de 15 criterios, verificar AHPGaussiano.

    Parametro
    ----------
    :param matriz_julgamentos: dataframe (required), matriz quadrada dos criterios de decisao preenchida com a escala fundamental de Saaty
    :param matriz_decisao: dataframe (required), matriz de linhas contendo as alternativas e colunas contendo os criterios
    :param objetivo: list, vetor contendo apenas os criterio de decisao que devem ser minimizados
                     default = 'max', assume que todos os criterios devem ser maximizados

    Atributos
    ----------
    :ivar objetivo: dict, contem os criterios e suas respectivas otimizacoes ('max', 'min')
    :ivar preferencia_local: dataframe, contem a matriz de decisao normalizada
    :ivar peso: serie, contem a ponderacao de cada criterio
    :ivar resultado: dataframe, preferencia global contendo o ranking das alternativas e suas respectivas pontuacoes
    :ivar cr: float, razao de consistencia que verifica se as avaliações paritarias respeitam o principio da transitividade
              cr deve ser <= 0,1 para que a matriz de julgamento seja consistente e o resultado satisfatorio

    Metodo
    ---------
    Sem metodos
    """

    # indice randomico, random index (RI)
    # _indice_consistencia = {n: RI}, sendo n o numero de criterios
    # n <= RI (15)
    _indice_consistencia = {
        1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41,
        9: 1.45, 10: 1.49, 11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
    }

    def __init__(self, matriz_julgamentos, matriz_decisao, objetivo='max'):
        _AnalyticHierarchyProcess.__init__(self, matriz_decisao, objetivo)

        # validar estrtura da matriz de julgamentos e da matriz de decisao
        if matriz_julgamentos.shape[1] != matriz_decisao.shape[1]:
            raise ValueError('numero de colunas das matrizes de julgamentos e de decisao devem ser iguais')
        elif matriz_decisao.shape[1] > len(AHPSaaty._indice_consistencia):
            raise InterruptedError('matriz de decisao deve conter no maximo 15 criterios de avaliacao')

        # validar se matriz de julgamentos obedece grau de importancia da escala Saaty
        if (matriz_julgamentos.max().max() > 9) or (matriz_julgamentos.min().min() < (1/9)):
            raise InterruptedError('matriz de julgamentos viola escala fundamental de Saaty')

        self._matriz_julgamentos = matriz_julgamentos
        self._julgamentos_normalizados = self._normalizar_julgamentos()
        self._n = self._matriz_julgamentos.shape[1]
        self.peso = self._vetor_prioridade()
        self._matriz_consitencia = self._analise_consistencia()
        self._dados_agregados = _AnalyticHierarchyProcess._agregacao(self, self.peso)
        self._maxlambda = self._lambda_max()
        self._ri = AHPSaaty._indice_consistencia[self._n]
        self._ci = (self._maxlambda - self._n) / (self._n - 1)
        self.cr = self._ci / self._ri
        self.resultado = resultado(self._dados_agregados)

    # normalizar coluna da matriz julgamento
    def _normalizar_julgamentos(self):
        soma_col = [self._matriz_julgamentos[col].sum() for col in self._matriz_julgamentos.columns]
        matriz_normalizada = pd.DataFrame()
        for indice, coluna in enumerate(self._matriz_julgamentos.columns):
            matriz_normalizada[coluna] = self._matriz_julgamentos[coluna].apply(lambda x: x / soma_col[indice])
        return matriz_normalizada

    # media ponderada de cada criterio
    def _vetor_prioridade(self):
        return self._julgamentos_normalizados.sum(axis=1) / self._n

    # multiplica a matriz de julgamentos pelo vetor peso
    def _analise_consistencia(self):
        matriz_consistencia = pd.DataFrame()
        for indice, coluna in enumerate(self._matriz_julgamentos.columns):
            matriz_consistencia[coluna] = self._matriz_julgamentos[coluna] * self.peso[indice]
        return matriz_consistencia

    # escalar necessario para calculo da razao de consistencia (cr)
    def _lambda_max(self):
        soma_linha = self._matriz_consitencia.sum(axis=1)
        return ((soma_linha / self.peso).sum()) / self._n


class AHPGaussiano(_AnalyticHierarchyProcess):

    """
    Metodo de decisao multicriterio derivado do Analytic Hierarchy Process desenvolvido por Marcos dos Santos.
    Apresenta uma nova abordagem ao metodo original de Tomas Saaty baseada na análise de sensibilidade proveniente
    do fator gaussiano. Neste metodo nao e necessario a avaliacao par a par entre os criterios para obtencao dos
    seus respectivos pesos. Vale ressaltar, que a viabilidade do modelo so e satisfeita em cenarios em que as
    alternativas possuam entradas cardinais nos criterios em analise.

    Parametro
    ----------
    :param matriz_decisao: dataframe (required), matriz de linhas contendo as alternativas e colunas contendo os criterios
    :param objetivo: list, vetor contendo apenas os criterio de decisao que devem ser minimizados
                     default = 'max', assume que todos os criterios devem ser maximizados

    Atributos
    ----------
    :ivar objetivo: dict, contem os criterios e suas respectivas otimizacoes ('max', 'min')
    :ivar preferencia_local: dataframe, contem a matriz de decisao normalizada
    :ivar fator_gaussiano: serie, contem o coeficiente de variação com relação a media
    :ivar peso: serie, contem a ponderacao de cada criterio
    :ivar resultado: dataframe, preferencia global contendo o ranking das alternativas e suas respectivas pontuacoes

    Metodo
    ---------
    Sem metodos
    """

    def __init__(self, matriz_decisao, objetivo='max'):
        _AnalyticHierarchyProcess.__init__(self, matriz_decisao, objetivo)

        self._media = self._media()
        self._desvio_padrao = self._desvio_padrao()
        self.fator_gaussiano = self._fator_gaussiano()
        self.peso = self._fator_gaussiano_normalizado()
        self._dados_agregados = _AnalyticHierarchyProcess._agregacao(self, self.peso)
        self.resultado = resultado(self._dados_agregados)

    def _media(self):
        return self.preferencia_local.sum() / len(self._matriz_decisao)

    def _desvio_padrao(self):
        return self.preferencia_local.std()

    def _fator_gaussiano(self):
        return self._desvio_padrao / self._media

    def _fator_gaussiano_normalizado(self):
        peso = self.fator_gaussiano.copy()
        soma = self.fator_gaussiano.sum()
        return peso.apply(lambda x: x / soma)

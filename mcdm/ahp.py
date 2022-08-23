import pandas as pd  # manipular dados


def _check_objetivo(criterios, objetivo='max'):
    """
    Função auxiliar que verifica se o objetivo especificado é valido. Se sim, minimiza todos os critérios da matriz de
    decisão que estajam contidos na lista informada. Se objetivo não for especificado, todos os critérios da matriz de
    decisão serão maximizados.
    Maximizar critérios significa que 'quanto maior o seu valor melhor';
    Minimizar critérios significa que 'quanto menor o seu valor melhor'.

    :param criterios: dataframe, matriz de decisão ou matriz de julgamentos.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
                     default = 'max', assume que todos os critérios devem ser maximizados.
    :return: dict, dicionário onde as chaves são os critérios de avaliação e os valores são suas otimizações(max/min).
    """
    dicionario = dict((col, 'max') for col in criterios.columns)
    if objetivo != 'max':
        if type(objetivo) != list:
            raise TypeError('objetivo deve ser uma lista')
        for item in objetivo:
            if item in dicionario:
                dicionario[item] = 'min'
            else:
                raise KeyError(f'{item} nao e um criterio valido')
    return dicionario


def _normalizar_decisao(matriz_decisao, objetivo='max'):
    """
    Função auxiliar que torna adimensional a matriz de decisão.
    A matriz de decisão normalizada indica as preferências locais das alternativas com relação ao critério de avaliação.

    :param matriz_decisao: dataframe, matriz de decisão.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
                     default = 'max', assume que todos os critérios devem ser maximizados.
    :return: dataframe, contém a matriz de decisão normalizada.
    """
    objetivo = _check_objetivo(matriz_decisao, objetivo)
    matriz_normalizada = matriz_decisao.copy()
    for item in objetivo:
        if objetivo[item] == 'max':
            soma = matriz_normalizada[item].sum()
            # normalizar
            matriz_normalizada[item] = matriz_normalizada[item] / soma
        else:
            # manipulação algébrica para trocar o numerador pelo denominador
            matriz_normalizada[item] = matriz_normalizada[item].apply(lambda x: 1 / x)
            # normalizar
            soma = matriz_normalizada[item].sum()
            matriz_normalizada[item] = matriz_normalizada[item] / soma
    return matriz_normalizada


def _agregacao(matriz_decisao, peso, objetivo='max'):
    """
    Função auxiliar que cria indicador de comparação entre as alternativas da matriz de decisão.
    Multiplica a preferência local pelo peso do critério de avaliação.
    A soma da matriz agregação por alternativa informa a preferência global.

    :param matriz_decisao: dataframe, matriz de decisão.
    :param peso: serie, contém a ponderação de cada critério.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
                     default = 'max', assume que todos os critérios devem ser maximizados.
    :return: dataframe, contém a matriz de agregação.
    """
    matriz_agregacao = _normalizar_decisao(matriz_decisao, objetivo)
    for indice, item in enumerate(matriz_agregacao.columns):
        matriz_agregacao[item] = matriz_agregacao[item] * peso[indice]
    return matriz_agregacao


def _resultado(matriz_decisao, peso, objetivo='max'):
    """
    Função auxiliar que cria um dataframe com as preferências globais e cria uma classificação das alternativas.

    :param matriz_decisao: dataframe, matriz de decisão.
    :param peso: serie, contém a ponderação de cada critério.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
                     default = 'max', assume que todos os critérios devem ser maximizados.
    :return: dataframe, contém a alternativa, a sua classificação e a sua pontuação.
    """
    df_resultado = _agregacao(matriz_decisao, objetivo, peso)
    # soma a linha da matriz de agregação
    df_resultado['Pontuacao'] = df_resultado.sum(axis=1)
    # ordena e cria a classificação
    df_resultado = df_resultado.sort_values('Pontuacao', ascending=False)
    df_resultado['Ranking'] = list(range(1, len(df_resultado) + 1))
    return df_resultado[['Ranking', 'Pontuacao']]


class AHPSaaty:
    """
    Analytic Hierarchy Process (AHP) é um método criado por Thomas Saaty para auxiliar nas tomadas de decisão
    multicritério. Caracterizado por uma matriz de decisão composta por alternativas e critérios ponderados pelo
    tomador de decisão em questão. Baseado em matemática e psicologia, o AHP não só determina a melhor decisão
    como também justifica a escolha.
    Restrição: Auxilia a tomada de decisão para problemas com até 15 critérios.
    Para problemas com mais de 15 critérios verificar AHPGaussiano.

    Parâmetros
    ----------
    :param matriz_julgamentos: dataframe (required), matriz quadrada dos critérios de decisão preenchida com
        a escala fundamental de Saaty.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
        default = 'max', assume que todos os critérios devem ser maximizados.

    Atributos
    ----------
    :ivar otimizacao: dict, contém os critérios e as suas respectivas otimizações ('max', 'min').
    :ivar peso: serie, contém a ponderação de cada critério.
    :ivar cr: float, razão de consistência que verifica se as avaliações paritárias respeitam o princípio
        da tansitividade. cr deve ser ≤ 0,1 para que a matriz de julgamento seja consistente e o resultado satisfatório.

    Métodos
    ----------
    preferencia_local(matriz_decisao): calcula a preferência local em cada critério.
    preferencia_global(matriz_decisao): calcula a preferência global das alternativas.
    """
    # índice randomico, random index (RI)
    # _indice_consistencia = {n: RI}, sendo n o número de critérios
    # n <= RI (15)
    _indice_consistencia = {
        1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41,
        9: 1.45, 10: 1.49, 11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
    }

    def __init__(self, matriz_julgamentos, objetivo='max'):

        self._matriz_julgamentos = matriz_julgamentos
        self._objetivo = objetivo
        self._check_matriz_julgamentos()

        self.otimizacao = _check_objetivo(matriz_julgamentos, objetivo)
        self._julgamentos_normalizados = self._normalizar_julgamentos()
        self._n = self._matriz_julgamentos.shape[1]
        self.peso = self._vetor_prioridade()
        self._matriz_consitencia = self._analise_consistencia()
        self._maxlambda = self._lambda_max()
        self._ri = AHPSaaty._indice_consistencia[self._n]
        self._ci = (self._maxlambda - self._n) / (self._n - 1)
        self.cr = self._ci / self._ri

    def _check_matriz_julgamentos(self):
        """
        Valida se a matriz de julgamentos obedece grau de importância da escala Saaty.
        Matriz de julgamento deve conter valores de 1 a 9 e a sua respectiva recíproca.
        Matriz de julgamento deve ser uma matriz quadrada.
        """
        if (self._matriz_julgamentos.max().max() > 9) or (self._matriz_julgamentos.min().min() < 1/9):
            raise InterruptedError('matriz de julgamentos viola escala fundamental de Saaty')
        if self._matriz_julgamentos.shape[0] != self._matriz_julgamentos.shape[1]:
            raise InterruptedError('matriz de julgamento deve ser uma matriz quadrada')
        if [coluna for coluna in self._matriz_julgamentos.columns] != [indice for indice in self._matriz_julgamentos.index]:
            raise InterruptedError('coluna e indices da matriz de julgamentos devem estar ordenados igualmente')
        for linha in self._matriz_julgamentos.index:
            for coluna in self._matriz_julgamentos.columns:
                if (self._matriz_julgamentos.loc[linha, coluna]) != (1 / self._matriz_julgamentos.loc[coluna, linha]):
                    raise InterruptedError(f'erro na recíproca da matriz de julgamento:item ({linha},{coluna})/({coluna},{linha})')

    def _normalizar_julgamentos(self):
        """ Normaliza a coluna da matriz de julgamentos e retorna um dataframe. """
        soma_col = [self._matriz_julgamentos[col].sum() for col in self._matriz_julgamentos.columns]
        matriz_normalizada = pd.DataFrame()
        for indice, coluna in enumerate(self._matriz_julgamentos.columns):
            matriz_normalizada[coluna] = self._matriz_julgamentos[coluna].apply(lambda x: x / soma_col[indice])
        return matriz_normalizada

    def _vetor_prioridade(self):
        """ Calcula a média ponderada de cada critério e retorna uma serie. """
        return self._julgamentos_normalizados.sum(axis=1) / self._n

    def _analise_consistencia(self):
        """ Multiplica a matriz de julgamentos pelo vetor peso e retorna um dataframe. """
        matriz_consistencia = pd.DataFrame()
        for indice, coluna in enumerate(self._matriz_julgamentos.columns):
            matriz_consistencia[coluna] = self._matriz_julgamentos[coluna] * self.peso[indice]
        return matriz_consistencia

    def _lambda_max(self):
        """ Escalar necessário para cálculo da razão de consistência (cr). Retorna um float. """
        soma_linha = self._matriz_consitencia.sum(axis=1)
        return ((soma_linha / self.peso).sum()) / self._n

    def _check_matriz_decisao(self, matriz_decisao):
        """ Valida a estrutura da matriz de julgamentos e da matriz de decisão. """
        if matriz_decisao.shape[1] > len(AHPSaaty._indice_consistencia):
            raise InterruptedError('matriz de decisao deve conter no maximo 15 criterios de avaliacao')
        if self._matriz_julgamentos.shape[1] != matriz_decisao.shape[1]:
            raise ValueError('numero de colunas das matrizes de julgamentos e de decisao devem ser iguais')
        if [coluna for coluna in self._matriz_julgamentos.columns] != [indice for indice in matriz_decisao.columns]:
            raise InterruptedError('colunas da matriz de decisão e matriz de julgamentos devem ser iguais')

    def preferencia_local(self, matriz_decisao):
        """
        Método que recebe a matriz de decisão, normaliza os seus dados e retorna as preferências locais de cada critério

        :param matriz_decisao: dataframe, matriz com linhas contendo as alternativas e colunas contendo os critérios.
        :return: dataframe, matriz contendo as preferências locais em cada critério.
        """
        return _normalizar_decisao(matriz_decisao, self._objetivo)

    def preferencia_global(self, matriz_decisao):
        """
        Método que recebe a matriz de decisão e o seu objetivo de otimização, valida a estrutura da matriz de decisão e
        retorna a preferência global, contendo a classificação das alternativas e as suas pontuações.

        :param matriz_decisao: dataframe, matriz com linhas contendo as alternativas e colunas contendo os critérios.
        :return: dataframe, preferência global contendo a classificação das alternativas e as suas pontuaçõess.
        """
        self._check_matriz_decisao(matriz_decisao)
        return _resultado(matriz_decisao, self._objetivo, self.peso)


class AHPGaussiano:
    """
    Método de decisão multicriterio derivado do Analytic Hierarchy Process desenvolvido por Marcos dos Santos.
    Apresenta uma nova abordagem ao método original de Tomas Saaty baseada na análise de sensibilidade proveniente
    do fator gaussiano. Neste método não é necessária a avaliação par a par entre os critérios para obtenção dos
    seus respectivos pesos. Vale ressaltar, que a viabilidade do modelo só é satisfeita em cenários em que as
    alternativas possuam entradas cardinais nos critérios em análise.

    Parâmetros
    ----------
    :param matriz_decisao: dataframe (required), matriz com linhas contendo as alternativas e colunas contendo
        os critérios.
    :param objetivo: list, vetor contendo apenas os critérios de decisão que devem ser minimizados.
        default = 'max', assume que todos os criterios devem ser maximizados.

    Atributos
    ----------
    :ivar otimizacao: dict, contém os critérios e as suas respectivas otimizações ('max', 'min').
    :ivar preferencia_local: dataframe, contém a preferência local em cada critério.
    :ivar fator_gaussiano: serie, contém o coeficiente de variação com relação à média.
    :ivar peso: serie, contém a ponderação de cada critério.

    Métodos
    ----------
    preferencia_global(): calcula a preferência global das alternativas.
    """
    def __init__(self, matriz_decisao, objetivo='max'):

        self._matriz_decisao = matriz_decisao
        self._objetivo = objetivo

        self.otimizacao = _check_objetivo(matriz_decisao, objetivo)
        self.preferencia_local = _normalizar_decisao(matriz_decisao, objetivo)
        self._media = self._media()
        self._desvio_padrao = self._desvio_padrao()
        self.fator_gaussiano = self._fator_gaussiano()
        self.peso = self._fator_gaussiano_normalizado()

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

    def preferencia_global(self):
        """
        Método sem parâmetros que retorna um dataframe contendo a preferência global do problema.
        Contém a classificação das alternativas e as suas pontuações.
        """
        return _resultado(self._matriz_decisao, self._objetivo, self.peso)

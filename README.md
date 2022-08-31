# MÉTODO DE DECISÃO MULTICRITÉRIO

<br>

Multiple-criteria decision-making (MCDM) é uma subdisciplina da Pesquisa Operacional que avalia explicitamente vários critérios conflitantes na tomada de decisão, servindo para inúmeros campos de aplicação. Como exemplo de métodos neste campo de pesquisa temos: AHP, ANP, PROMETHEE, TOPSIS, THOR, SAPEVO, ELECTRE.

**Neste pacote em específico trazemos uma solução em Python para o Analytic Hierarchy Process (AHP), por este ser um dos mais utilizados.**

AHP foi um método desenvolvido em 1970 por [Thomas Saaty](https://pt.wikipedia.org/wiki/Thomas_Saaty). Baseado em matematica e psicologia, este framework ajuda pessoas a escolher e justificar a sua escolha para uma melhor tomada de decisão em situações complexas através da [propriedade matemática da transitividade](https://pt.wikipedia.org/wiki/Rela%C3%A7%C3%A3o_transitiva).


<hr>

## Sumário

[Instalação](#Instalação) <br>
[Documentação](#Documentação): <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Classe AHP <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Classe AHP-Gaussiano <br>
[Aplicação](#Aplicação): <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Escolha do novo Diretor na Empresa <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Escolha de compra para o novo celular <br>
[Apêndice](#Apêndice): <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Escala Fundamental de Saaty <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Matriz de Julgamentos <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Matriz de Decisão


<hr>

## Instalação

```pip install git+https://github.com/MarioLisboaJr/multiple_criteria_decision.git```

<hr>

## Documentação

## [mcdm.ahp](https://github.com/MarioLisboaJr/multiple_criteria_decision/blob/main/mcdm/ahp.py#L92).AHPSaaty

classe mcdm.ahp.AHPSaaty(matriz_julgamentos, objetivo='max')

Analytic Hierarchy Process (AHP) é um método criado por Thomas Saaty para auxiliar nas tomadas de decisão multicritério. Caracterizado por uma matriz de decisão composta por alternativas e critérios ponderados pelo tomador de decisão em questão. Baseado em matemática e psicologia, o AHP não só determina a melhor decisão como também justifica a escolha.
    
**Restrição**: auxilia a tomada de decisão para problemas com até 15 critérios. <br>
Para problemas com mais de 15 critérios, verificar AHPGaussiano. <br>

### Parâmetro:

- `matriz_julgamentos`: **dataframe (required)**, matriz quadrada dos critérios de decisão preenchida com a escala fundamental de Saaty.


- `objetivo`: **list**, vetor contendo apenas os critérios de decisão que devem ser minimizados.
     - default = 'max', assume que todos os critérios devem ser maximizados.

### Atributos:

- `otimizacao`: **dict**, contém os critérios e suas respectivas otimizações ('max', 'min').

    
- `peso`: **serie**, contém a ponderação de cada critério.


- `cr`: **float**, razão de consistência que verifica se as avaliações paritárias respeitam o princípio da transitividade.
     - cr deve ser <= 0,1 para que a matriz de julgamento seja consistente e o resultado satisfatório.


### Métodos:

- `preferencia_local(matriz_decisao)`: calcula a preferência local em cada critério.
  - **Parâmetro**: **matriz_decisao**: dataframe, matriz com linhas contendo as alternativas e colunas contendo os critérios.
  - **Devolução**: **dataframe**, matriz contendo as preferências locais em cada critério.
  
  
- `preferencia_global(matriz_decisao)`: calcula a preferência global das alternativas.
    - **Parâmetro**: **matriz_decisao**: dataframe, matriz com linhas contendo as alternativas e colunas contendo os critérios.
    - **Devolução**: **dataframe**, preferência global contendo a classificação das alternativas e as suas pontuações.

## [mcdm.ahp](https://github.com/MarioLisboaJr/multiple_criteria_decision/blob/main/mcdm/ahp.py#L215).AHPGaussiano

classe mcdm.ahp.AHPGaussiano(matriz_decisao, objetivo='max')

Método de decisão multicritério derivado do Analytic Hierarchy Process desenvolvido por Marcos dos Santos. Apresenta uma nova abordagem ao metodo original de Tomas Saaty baseada na análise de sensibilidade proveniente do fator gaussiano. Neste método não é necessário a avaliação par a par entre os critérios para obtenção dos seus respectivos pesos. Vale ressaltar, que a viabilidade do modelo só é satisfeita em cenários em que as alternativas possuam entradas cardinais nos critérios em análise.

### Parâmetro:

- `matriz_decisao`: **dataframe (required)**, matriz de linhas contendo as alternativas e colunas contendo os critérios.


- `objetivo`: **list**, vetor contendo apenas os critério de decisão que devem ser minimizados.
     - default = 'max', assume que todos os critérios devem ser maximizados.

### Atributos:

- `otimizacao`: **dict**, contem os critérios e suas respectivas otimizações ('max', 'min').


- `preferencia_local`: **dataframe**, contem a matriz de decisão normalizada.


- `fator_gaussiano`: **serie**, contem o coeficiente de variação com relação a média.


- `peso`: **serie**, contem a ponderação de cada critério.

### Método:

- `preferencia_global()`: calcula a preferência global das alternativas.
    - **Parâmetro**: Sem Parâmetro.
    - **Devolução**: **dataframe**, preferência global contendo a classificação das alternativas e as suas pontuações.

<hr>

## Aplicação

#### Escolha do novo Diretor na Empresa:

[Descrição do Caso](https://en.wikipedia.org/wiki/Analytic_hierarchy_process_%E2%80%93_leader_example#Overview) <br>

**Definição do Objetivo**: Selecionar o líder mais indicado a assumir o posto do diretor-executivo <br>
**Definição dos Critérios**: Experience, Education, Charisma, Age <br>
**Definição das Alternativas**: Tom, Dick, Harry <br>

```python
import pandas as pd
from mcdm.ahp import AHPSaaty

criterios = ['Experience', 'Education', 'Charisma', 'Age']
alternativas = ['Tom', 'Dick', 'Harry']

# 1º Passo: Criar Matriz de Decisão
# 'Age' é o único dado quantitativo dos critérios
# Assim podemos inserí-lo diretamento na matriz de decisão
age = [50, 60, 30]
matriz_decisao = pd.DataFrame(age, columns=['Age'], index=alternativas)

# 'Experience', 'Education' e 'Charisma' são dados qualitativos
# Utilizar o AHPSaaty para transformar esses dados em quantitativos e achar o peso de cada alternativa em cada critério

# Experience
experience_julgamento = [
    [  1, 1/4, 4],
    [  4,   1, 9],
    [1/4, 1/9, 1]
]
df_julgamento_experience = pd.DataFrame(experience_julgamento, index=alternativas, columns=alternativas)
ahp_experience = AHPSaaty(df_julgamento_experience)
matriz_decisao['Experience'] = ahp_experience.peso  # inserir na matriz de decisão

# Education
education_julgamento = [
    [  1, 3, 1/5],
    [1/3, 1, 1/7],
    [  5, 7,   1]
]
df_julgamento_education = pd.DataFrame(education_julgamento, index=alternativas, columns=alternativas)
ahp_education = AHPSaaty(df_julgamento_education)
matriz_decisao['Education'] = ahp_education.peso  # inserir na matriz de decisão

# Charisma
charisma_julgamento = [
    [  1,   5, 9],
    [1/5,   1, 4],
    [1/9, 1/4, 1]
]
df_julgamento_charisma = pd.DataFrame(charisma_julgamento, index=alternativas, columns=alternativas)
ahp_charisma = AHPSaaty(df_julgamento_charisma)
matriz_decisao['Charisma'] = ahp_charisma.peso  # inserir na matriz de decisão

# Organizar a matriz de decisão
matriz_decisao = matriz_decisao[criterios]


# 2º Passo: Criar Matriz de Julgamentos
julgamento = [
    [  1,   4,   3, 7],
    [1/4,   1, 1/3, 3],
    [1/3,   3,   1, 5],
    [1/7, 1/3, 1/5, 1]
]
matriz_julgamentos = pd.DataFrame(julgamento, columns=criterios, index=criterios)


# 3º Passo: Aplicar o Método
ahp = AHPSaaty(matriz_julgamentos)
selecao_alternativas = ahp.preferencia_global(matriz_decisao)
print(selecao_alternativas)
```

```
       Ranking  Pontuacao
Dick         1   0.474528
Tom          2   0.364213
Harry        3   0.161259
```

#### Escolha de compra para o novo celular:

**Definição do Objetivo**: Selecionar o celular com o melhor custo benefício <br>
**Definição dos Critérios**: Custo, Camera, Armazenamento, Bateria <br>
**Definição das Alternativas**: Xiaomi, Samsung, Iphone <br>

```python
import pandas as pd
from mcdm.ahp import AHPSaaty
from mcdm.ahp import AHPGaussiano

criterios = ['Custo', 'Camera', 'Armazenamento', 'Bateria']
alternativas = ['Xiaomi', 'Samsung', 'Iphone']
dados = [
    [1200, 12, 64, 24],
    [1500, 12, 128, 18],
    [5000, 20, 128, 10]
]

# 1º Passo: Criar Matriz de Decisão
matriz_decisao = pd.DataFrame(dados, columns=criterios, index=alternativas)


# 2º Passo: Criar Matriz de Julgamentos
julgamento = [
    [  1,   3,   5, 7],
    [1/3,   1,   3, 7],
    [1/5, 1/3,   1, 3],
    [1/7, 1/7, 1/3, 1]
]
matriz_julgamento = pd.DataFrame(julgamento, columns=criterios, index=criterios)


# 3º Passo: Aplicar o Método
minimizar_criterio = ['Custo']
ahp = AHPSaaty(matriz_julgamento, minimizar_criterio)
ahp_gaussiano = AHPGaussiano(matriz_decisao, minimizar_criterio)

escolha_ahp = ahp.preferencia_global(matriz_decisao)
escolha_ahp_gaussiano = ahp_gaussiano.preferencia_global()

print(escolha_ahp, '\n\n', escolha_ahp_gaussiano)
```

```
         Ranking  Pontuacao
Xiaomi         1   0.393204
Samsung        2   0.356861
Iphone         3   0.249935 

          Ranking  Pontuacao
Xiaomi         1   0.380453
Samsung        2   0.359630
Iphone         3   0.259916
```


<hr>

## Apêndice

## Escala Fundamental de Saaty:

Relação de Importância      | Grau de Importância | Recíproca
:--------------------------:|:-------------------:|:----------:
Igualdade                   | 1                   | 1
Intermediário               | 2                   | 1/2
Importância Moderada        | 3                   | 1/3
Intermediário               | 4                   | 1/4
Mais Importante             | 5                   | 1/5 
Intermediário               | 6                   | 1/6
Muito Mais Importante       | 7                   | 1/7
Intermediário               | 8                   | 1/8
Extremamente Mais Importante| 9                   | 1/9 

## Matriz de Julgamentos:

Pontos de atenção para elaboração desta matriz:

- É uma Matriz quadrada;
- A avaliação dos critérios é feita sempre por linha em relação a coluna;
- A avaliação deve respeitar Grau de Importância e sua Recíproca da Escala Saaty
- Note que sua diagonal principal é sempre igual a 1;
- À esquerda da diagonal principal é sempre igual ao inverso à direita da diagonal principal (Axioma da Reciprocidade).

\            |  Critério 1   |  Critério 2   |  Critério 3   | Critério n  
:---:        | :-----:       |:-----:        |:-----:        |:-----:
Critério 1   | ``1``         | 7             | 5             | 3
Critério 2   |   1/7         | ``1``         | 1/3           | 1/6
Critério 3   |   1/5         |   3           | ``1``         | 1/3
Critério n   |   1/3         |   6           |   3           | ``1``

Note:

- Considerando que o **Critério 1 é Muito Mais Importante que o Critério 2**, pela Escala Fundamental de Saaty, atribuímos ao campo o valor **7**. Logo, **Critério 2 é Muito Menos Importante que o Critério 1** e portanto deve ser atribuído o valor de **1/7**. 

## Matriz de Decisão:

Pontos de atenção para elaboração desta matriz:

- É uma matriz de Alternativas por Critérios;
- Para AHPSaaty n deve ser menor ou igual a 15, caso contrário, utilizar AHPGaussiano.

\               |  Critério 1   |  Critério 2   |  ...   | Critério n  
:--------------:|:-------------:|:-------------:|:------:|:-----------:
Alternativa 1   | 1200          |  12           |  ...   |  24  
Alternativa 2   | 1500          |  12           |  ...   |  18  
...             | ...           | ...           | ...    | ...
Alternativa m   | 5000          |  20           |  ...   |  10  

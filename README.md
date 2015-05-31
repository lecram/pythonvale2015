# Usando Metaprogramação para Instrumentar Python com Python

## Slides

### PDF

Os slides que utilizei na apresentação estão no arquivo `slides-short.pdf`. O arquivo `slides-full.pdf` é uma versão extendida, com mais detalhes e uma demo extra.

### Online

Os slides podem ser vistos em http://lecram.github.io/pythonvale2015 . Note que em algumas partes é possível navegar para baixo para ver o conteúdo extra.

## Código Fonte

Este repositório contém o código fonte completo dos casos de uso mostrados na apresentação:

- Grafo de Chamadas (`graph.py`)
- Análise de Cobertura (`cover.py`)
- Perfilador (`prof.py`)
- Depurador (`debug.py`)

Estes scripts recebem um programa Python como argumento. O arquivo `app.py` é o programa usado como exemplo.

**Observação**: estes scripts são apenas demos educativas que têm o objetivo de ilustrar a utilidade das funções `sys.setprofile()` e `sys.settrace()`. Fiquem à vontade para extendê-los e transformá-los em algo útil.

### Grafo de Chamadas

O script `graph.py` gera um grafo em formato [dot](http://www.graphviz.org/content/dot-language) representando as chamadas de funções ocorridas durante a execução do programa analisado.

```
$ python graph.py app.y
```

Para gerar uma imagem do grafo, basta utilizar a ferramenta `dot` do [Graphviz](http://www.graphviz.org/):

```
$ python graph.py app.py | dot -Tpng -o app_graph.png
```

### Análise de Cobertura

O script `cover.py` exibe o código fonte do programa analisado, colorindo as linhas executadas de verde e as demais de vermelho (isto só funciona em um terminal Unix):

```
$ python cover.py app.py
```

É recomendável utilizar o comando `less` para navegar na saída produzida:

```
$ python cover.py app.py | less -R
```

### Perfilador

O script `prof.py` exibe uma tabela das funções que mais utilizaram um recurso durante a execução do programa analisado. Por padrão, o recurso é tempo em segundos:

```
$ python prof.py app.py
```

Pode-se usar o comando `column` para formatar melhor a tabela gerada:

```
$ python prof.py app.py | column -t
```

### Depurador

O script `debug.py` executa um depurador simples que permite inspecionar o programa analisado enquanto o mesmo é executado:

```
$ python debug.py app.py
```

Os comandos implementados são:

- `break N` para adicionar um ponto de parada na linha N;
- `unbreak N` para remover o ponto de parada na linha N;
- `continue` para continuar a execução até encontrar um breakpoint;
- `step` para executar a próxima linha;
- `print EXPR` para imprimir o resultado da expressão dada no contexto atual;
- `quit` para interromper a execução do programa e sair do depurador.

### Demo Extra

O código na pasta `extra` é só uma brincadeira que não deu tempo de apresentar :)

## Licença

Todo o código e documentação neste repositório estão em Domínio Público.

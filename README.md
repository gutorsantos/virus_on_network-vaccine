# Virus on a Network

## Apresentação do novo modelo

O modelo foi modificado com base em um exemplo fornecido no repositório do [framework MESA](https://github.com/projectmesa/mesa-examples).

Foi adicionado ao contexto da simulação a existência de pessoas vacinadas contra o virus em questão. Além disso, as vacinas possuem um percentual de proteção. 

Por exemplo, num ambiente onde a chance de contaminação seja de 90%, caso a vacina possua uma taxa de proteção de 80%, então a pessoa vacinada possui uma chance de contaminação de 18% de infecção.

## Descrição da hipótese

A hipótese formulada foi:

"Em um dado ambiente, com indivíduos vulneráveis, vulneráveis mas vacinadas e infectadas, caso hajam indivíduos vacinados a contaminação será menor de que se não houvesse nenhum indivíduo vacinado, consequentemente, ao haver um aumento no número de indivíduos vacinados a transmissão do vírus reduz. "

## Mudanças

Foi adicionado os seguintes parâmetros:
- num_vaccinated - porcentagem da população total que iniciará a simulação vacinada (varia de 0% a 100%)
- vaccine_rate - taxa de proteção da vacina, pode-se entender como porcentagem de redução da chance de contaminação (varia de 0% a 100%)

Além disso foram implementadas novas lógicas para que a chance de infecção fosse reduzida para os indivíduos vacinados, como pode ser visto no trecho de código abaixo:
```
def try_to_infect_neighbors(self):
    ...
        ...
        elif a.state == State.SUSCEPTIBLE_AND_VACCINATED:
            t = self.random.random()
            b = abs(self.virus_spread_chance*(1-self.vaccine_rate))
            print(t, b)
            if t < abs(self.virus_spread_chance*(1-self.vaccine_rate)):
                a.state = State.INFECTED
```

Outras modificações foram realizadas porém essas são mínimas e foram feitas apenas para as novas execução correta da simulação.

## Como utilizar

### Dependências
 
Para a execução correta do modelo deve-se instalar o pacote **mesa** e os outros listados em **requirements.txt**.

### Execução

Para rodar a simulação em modo gráfico utilize o comando:

```
python run.py
```

Para rodar a simulação em modo batch utilize o comando:
```

python run_batch.py
```

git subtree pull --prefix experiments/gutorsantos/labs/VoN-Vaccine https://github.com/gutorsantos/virus_on_network-vaccine.git main --squash
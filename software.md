![](./Captura%20de%20tela%20de%202023-10-27%2014-54-28.png)


Iniciou-se com *Standard Firmata* e construiu-se uma prova de conceito. Com o desenvolvimento do sistema surgiram necessidades que não eram atendidas então migrou-se para [Telemetrix](https://mryslab.github.io/telemetrix/).

Numa primeira abordagem, pode-se dizer que telemetrix é composto por um programa que é executado na *placa* e um conjunto de bibliotecas da linguagem Python que permitem usar a *placa* através, por exemplo, do interpretador Python (REPL).

Para instalar o programa na *placa*, usa-se a IDE do Arduino, instala-se a biblioteca (de arduino) `telemetrix4Arduino`, abre-se o exemplo `telemetrix4Arduino` e envia-se o programa para o Arduino. Mais detalhes em https://mryslab.github.io/telemetrix/telemetrix4arduino/ . 

Para instalar as bibliotecas usar os comandos `pip3 install telemetrix` e `pip3 install telemetrix_aio`. Mais detalhes em https://mryslab.github.io/telemetrix/install_telemetrix/ e https://mryslab.github.io/telemetrix/install_telemetrix-aio/ . 

Após instalar o programa na *placa* e as bibliotecas no *computador*, pode-se testar o conjunto fazendo o LED do Arduino piscar. Isto é feito abrindo o REPL (o comando costuma ser `python3`) e executando o programa listado em https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/blink.py . Se você baixar o arquivo `blink.py` basta digitar `import blink` no REPL.

 

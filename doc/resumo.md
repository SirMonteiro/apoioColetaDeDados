No começo, conversei com o Prof. Dr. Fabio Nakano sobre o projeto e ele me passou o que já havia pesquisado, estudar o [Arduino Mega](https://docs.arduino.cc/hardware/mega-2560) e talvez alguns hardwares comunicáveis com esse microcontrolador, que, apesar da contraindicação de algumas fontes, parece ser um hardware bastante acessível e livre a adaptações.

Para a validação dos estudos foi comprado o [multímetro de precisão Ty720 da Yokogawa](https://tmi.yokogawa.com/br/solutions/products/portable-and-bench-instruments/digital-multimeters/ty720-digital-multimeter/), um equipamento que permite a comunicação serial com um computador para a passagem de dados dele, sendo o detalhe para manter ele medindo constante, a reposição das pilhas nele, para isso foi comprado um estoque de pilhas alcalinas com o objetivo de manter esse equipamento com o funcionamento original dele afim de evitar qualquer variação nas medições.

Para controlar e processar todos os dados obtidos pelos dois hardwares foi pensado em ter um computador de placa-única (SBC), capaz de capturar as aferições e deixá-las disponível a qualquer momento para o pesquisador e para os estudos realizados. Para esse projeto, foi então comprado um [Raspberry pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/).

Para a comunicação entre o Arduino e o Raspberry pi inicialmente foi feita pelo protocolo [firmata](https://github.com/firmata/protocol), assim, o raspberry se comunica utilizando de _scripts_ python pela biblioteca [pyFirmata](https://pypi.org/project/pyFirmata/), por detalhes técnicos, a biblioteca foi alterada para a utilização do [telemetrix](https://pypi.org/project/telemetrix/) que é uma alternativa ao pyFirmata com uma melhor inicialização e suporte ao protocolo I2C.

Em uma das visitas ao laboratório, a Verena trouxe um kit montado por outros pesquisadores, de um arduino equipado com o módulo [ADS1115](https://www.ti.com/product/ADS1115), um conversor analógico digital de 16bits e assim idealizei o primeiro circuito para testes:

![Primeiro diagrama elétrico|1200](../res/firstDiagram.svg)

O Raspberry pi conectado ao wifi para ter acesso remoto aos dados coletados, O múltimetro Yokogawa representado pelo voltímetro no circuito acima conectado a usb, e um arduino também conectado na usb, que nele possui conectado dois pares de relês e um módulo ADS1115.

Desse modo, é criado uma tabela contendo os valores brutos da coleta, que está funcionando da seguinte maneira: é conectado ao circuito um par de relês de cada vez para realizar a leitura de n pontos sendo a limitação o número de portas digitais do arduino, assim é coletado o ponto representado por um par de relês, o _timestamp_ da medição, o valor da entrada analógica do arduino conectado ao ponto de medição, a tensão referência do arduino medida pelo ADS1115, a tensão do ponto testado pelo ADS1115 e a tensão medida pelo Multímetro.

O uso dos relês estão atrelados em conseguir medir vários pontos ao "mesmo tempo", sem que um seja interferido por outro, pois eles sempre serão isolados até que o par de relê responsável pelo ponto se conecte ao circuito.

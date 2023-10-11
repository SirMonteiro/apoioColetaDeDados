(Autor: Fábio Nakano)

Um requisito para a elaboração deste projeto é o de substituir a operação de um operador humano usando um multímetro de maneira que essa substituição possa ser explicada e aceita. Em outras palavras, o requisito é atendido se uma pessoa é capaz de aceitar que a medição feita pelo circuito é tão boa quanto a medição feita por um operador humano. 

> Quando um operador usa um multímetro, por exemplo, para medir a tensão elétrica em várias pilhas, ele conecta os bornes das pontas de prova nos conectores do multímetro, seleciona, no multímetro, uma escala adequada, toma uma pilha, conecta eletricamente uma ponta de prova ao terminal positivo da pilha, outra ponta de prova ao terminal negativo da pilha e faz uma medida relativa à pilha que tomou; desfaz a conexão das pontas de prova com a pilha, toma outra pilha, faz as conexões com esta outra pilha e faz a medida relativa a esta outra pilha; repetindo o processo até que não reste mais pilhas para medir.

No processo acima, enquanto o operador não conecta as pontas de prova a alguma pilha, as pontas de prova e os polos de todas as pilhas estão isolados pelo ar. Quando o operador conecta as pontas de prova, uma pilha está conectada às duas pontas de prova e as outras pilhas continuam isoladas pelo ar.

Com base neste modelo do processo, nota-se que é requisito do processo que as pilhas e o multímetro não estejam previamente conectadas, mesmo que, num polo só ou numa ponta de prova só. 

Nota-se que o componente eletro-eletrônico que conecta contatos e atende ao modelo é o relé. Este é um componente eletromecânico que, grosso modo, consiste em um eletroímã, uma alavanca e contatos elétricos. Internamente, o eletroímã é eletricamente isolado dos contatos por ar e pelas partes plásticas que o constituem. Nos relés de polo único e três contatos que serão usados, os contatos são designados comum (C), normalmente aberto (NA) e normalmente fechado (NF). Em condições normais de operação, quando o eletroímã está desligado, C está eletricamente conectado a NF e NA está isolado (por ar); quando o eletroímã é ligado, C passa a ligar-se a NA e NF fica isolado (por ar). Mais detalhes e uma animação mostrando o funcionamento do relé podem ser vistos na [Wikipedia](https://en.wikipedia.org/wiki/Relay).

As características elétricas de um relé estão em sua folha de dados (datasheet). Os relés usados são praticamente *commodities* em que o fabricante permite até personalizar a logomarca impressa no corpo do componente (https://www.alibaba.com/product-detail/12v-Relay-Manufacturer-JQC-3F-Spdt_1600775361783.html?spm=a2700.pc_countrysearch.main07.31.3cda4e03oW9rNh , https://www.alibaba.com/product-detail/12v-Relay-Manufacturer-JQC-3F-Spdt_1600835031247.html?spm=a2700.pc_countrysearch.main07.32.65784e03gY5kTx). Isto tem impacto sobre a confiança nas especificações técnicas das folhas de dados, quaisquer que sejam. Mesmo assim, é útil ter uma especificação como base. [Esta](.//home/fabio/MeuGithub/apoioColetaDeDados/Documentos/FL-3FF-Datasheet.pdf) foi obtida do site Maker Hero (https://makerhero.com/img/files/download/FL-3FF-Datasheet.pdf?_gl=1*48j2g0*_ga*NDc4NjY0MzMyLjE2OTY5NjYzNjQ.*_ga_025J7BMBEC*MTY5Njk2NjM2NC4xLjAuMTY5Njk2NjM2NC42MC4wLjA.).

Da especificação destaca-se:
	
1. Máxima tensão/corrente nos contatos em corrente contínua: 10A 30VDC (**nota 1**)
2. Máxima resistência de contato (contato fechado): $100m\Omega@6VDC\.maximum$
3. Resistência de isolação: $100M\Omega@500VDC\.minimum$

**nota 1**: Este dado não está na folha de dados, mas está no corpo de um relé com características de contato AC similares (máxima tensão/corrente nos contatos em corrente alternada: 10A 250VAC/30VDC; 12A 125VAC/28VDC)

Consequentemente, é possível afirmar:

1. O contato isolado, seja NA, seja NF, é tão bem isolado quanto são as pontas de prova dos polos das pilhas não conectadas;
2. o circuito a que pertence o eletroímã é distinto do circuito a que pertencem C, NA e NF.

A partir da afirmação 1 é possível afirmar que a operação de conectar a ponta de prova ao polo da pilha pode ser feita através dos contatos de um (ou mais) relé(s).

A partir da afirmação 2 é possível afirmar que é indiferente, para o processo de medição das pilhas, se o contato for operado por um operador humano ou por um eletroímã. Também a partir da afirmação 2, é indiferente, para o processo de medição das pilhas, se houver ou não circuitos conectados ao eletroímã, desde que este não esteja conectado ao circuito dos contatos.

A substituição do operador humano pelos relés e circuitos de controle dos relés então é:
	
(figura ou diagrama...)

Este circuito, por construção, atende aos requisitos. O leitor pode inspecionar e confrontar o circuito aos requisitos, se desejar.




# Apoio a coleta de dados - Medidor de tensão elétrica

Repositório criado para manter o histórico das documentações e códigos feitos durante a Iniciação Científica feita pela [PUB](https://prg.usp.br/programa-unificado-de-bolsas-de-estudo-para-estudantes-de-graduacao-pub/).

# Resumo

Atualmente, para fazer a aferição de potencial elétrico em ambientes de baixa tensão e corrente com precisão é necessário equipamentos de custo elevado e muita das vezes usar os _softwares_ proprietários das ferramentas, além disso, vários equipamentos precisam da disponibilidade do pesquisador para operar fazer manualmente. Desse modo, essa pesquisa visa estudar maneiras de realizar essa aferição com equipamentos de baixo custo que conseguem chegar em uma precisão igual ou maior aos equipamentos especializados e de forma contínua informar ao pesquisador o estado do objeto a ser aferido de forma forma a dispensar o mesmo de fazer essa tarefa repetitiva.

# Funcionamento

O sistema (_hardware_ e _software_) que está em construção mede tensões com vários sensores e registra essas tensões em arquivos texto.

Um multímetro de precisão também é usado como sensor. Suas medidas serão usadas como referência para avaliação da qualidade dos outros sensores.

Relés são usados para conectar e desconectar as fontes de tensão.

Estes relés e alguns dos sensores são controlados por uma _placa_ microcontrolada Arduino Mega que se comunica com um _computador_. No caso é usado um Raspberry Pi modelo 4B com 4Gbytes de RAM com sistema operacional Raspbian.

Tanto o multímetro quanto a _placa_ comunicam-se com o _computador_ por portas USB.

Há muitas maneiras de programar a _placa_ e o computador de maneira que se comuniquem, por exemplo, executando na _placa_ um programa específico a esta aplicação, por exemplo, escrito em linguagem C e compilado com a IDE do Arduino; e executando no computador, por exemplo, um programa de comunicação serial genérico como puTTY ou minicom e alguns _scripts_ de sistema operacional.

Esta solução, embora funcional, dificultaria:

-   reconfigurações no sistema, por exemplo, agregar outros sensores, pois criaria vários programas que precisariam ser ajustados;
-   criação de uma interface gráfica local ao sistema, pois não provê facilidades para criação dessas interfaces;

(Por outro lado, permitiria usar o Raspberry Pi sem gerenciador de interface, o que possibilitaria usar um _computador_ com menos capacidade de processamento.)

Optou-se por executar na _placa_ um programa de controle genérico e centralizar o desenvolvimento do _software_ no _computador_. Desta forma, se conveniente, a leitura do multímetro e dos sensores, o controle dos relés, o gerenciamento dos dados e a interface gráfica podem ser feitos através de um ou mais programas escritos na linguagem Python.

Segue o detalhamento das partes do sistema

-   [Detalhamento do _hardware_](doc/hardware.md);
-   [Detalhamento do _software_](doc/software.md);
